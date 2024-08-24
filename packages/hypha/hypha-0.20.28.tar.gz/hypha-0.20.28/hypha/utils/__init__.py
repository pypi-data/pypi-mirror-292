"""Provide utilities that should not be aware of hypha."""
import copy
import asyncio
import gzip
import os
import posixpath
import secrets
import string
import time
from datetime import datetime
from typing import Callable, List, Optional
import shortuuid
import friendlywords as fw

import httpx
from fastapi.routing import APIRoute
from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipResponder
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

_os_alt_seps: List[str] = list(
    sep for sep in [os.path.sep, os.path.altsep] if sep is not None and sep != "/"
)


def random_id(readable=True):
    """Generate a random ID."""
    if readable:
        return (
            fw.generate("po", separator="-")
            + "-"
            + f"{int((time.time() % 1) * 100000000):08d}"
        )
    else:
        return shortuuid.ShortUUID().random(length=22)


PLUGIN_CONFIG_FIELDS = [
    "name",
    "source_hash",
    "version",
    "format_version",
    "type",
    "tags",
    "icon",
    "requirements",
    "env",
    "defaults",
    "flags",
    "inputs",
    "outputs",
    "dependencies",
    "app_id",
]


class EventBus:
    """An event bus class for handling and listening to events asynchronously."""

    def __init__(self, logger=None):
        """Initialize the event bus."""
        self._callbacks = {}
        self._logger = logger

    def on(self, event_name, func):
        """Register an event callback."""
        self._callbacks[event_name] = self._callbacks.get(event_name, []) + [func]
        return func

    def once(self, event_name, func):
        """Register an event callback that only runs once."""

        def once_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.off(event_name, once_wrapper)
            return result

        return self.on(event_name, once_wrapper)

    def off(self, event_name, func=None):
        """Remove an event callback."""
        if func:
            if event_name in self._callbacks and func in self._callbacks[event_name]:
                self._callbacks[event_name].remove(func)
                if not self._callbacks[event_name]:
                    del self._callbacks[event_name]
        else:
            self._callbacks.pop(event_name, None)

    def emit(self, event_name, data):
        """Trigger an event and return a task that completes when all handlers are done."""
        tasks = []
        for func in self._callbacks.get(event_name, []):
            try:
                result = func(data)
                if asyncio.iscoroutine(result):
                    tasks.append(result)
            except Exception as e:
                if self._logger:
                    self._logger.error(
                        "Error in event callback: %s, %s, error: %s",
                        event_name,
                        func,
                        e,
                    )

        if tasks:
            return asyncio.ensure_future(asyncio.gather(*tasks))
        else:
            fut = asyncio.get_event_loop().create_future()
            fut.set_result(None)
            return fut

    async def wait_for(self, event_name, match=None, timeout=None):
        """Wait for a specific event with an optional timeout and conditions."""
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def handler(args):
            if self._matches(match, args):
                if not future.done():
                    future.set_result(args)

        self.on(event_name, handler)
        try:
            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            raise
        finally:
            self.off(event_name, handler)

    def _matches(self, match, data):
        """Check if the event data matches the given criteria."""
        if not match:
            return True  # No match criteria provided, always match
        if not data or len(data) < 1:
            return False  # No data to match against
        return all(data.get(key) == value for key, value in match.items())


def generate_password(length=20):
    """Generate a password."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


def is_safe_path(basedir: str, path: str, follow_symlinks: bool = True) -> bool:
    """Check if the file path is safe."""
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))


def safe_join(directory: str, *pathnames: str) -> Optional[str]:
    """Safely join zero or more untrusted path components to a base directory.

    This avoids escaping the base directory.
    :param directory: The trusted base directory.
    :param pathnames: The untrusted path components relative to the
        base directory.
    :return: A safe path, otherwise ``None``.

    This function is copied from:
    https://github.com/pallets/werkzeug/blob/fb7ddd89ae3072e4f4002701a643eb247a402b64/src/werkzeug/security.py#L222
    """
    parts = [directory]

    for filename in pathnames:
        if filename != "":
            filename = posixpath.normpath(filename)

        if (
            any(sep in filename for sep in _os_alt_seps)
            or os.path.isabs(filename)
            or filename == ".."
            or filename.startswith("../")
        ):
            raise Exception(
                f"Illegal file path: `{filename}`, "
                "you can only operate within the work directory."
            )

        parts.append(filename)

    return posixpath.join(*parts)


def parse_s3_list_response(response, delimeter):
    """Parse the s3 list object response."""
    if response.get("KeyCount") == 0:
        return []
    items = [
        {
            "type": "file",
            "name": item["Key"].split("/")[-1] if delimeter == "/" else item["Key"],
            "size": item["Size"],
            "last_modified": datetime.timestamp(item["LastModified"]),
        }
        for item in response.get("Contents", [])
    ]
    # only include when delimeter is /
    if delimeter == "/":
        items += [
            {"type": "directory", "name": item["Prefix"].rstrip("/").split("/")[-1]}
            for item in response.get("CommonPrefixes", [])
        ]
    return items


def list_objects_sync(s3_client, bucket, prefix=None, delimeter="/"):
    """List a objects sync."""
    prefix = prefix or ""
    response = s3_client.list_objects_v2(
        Bucket=bucket, Prefix=prefix, Delimiter=delimeter
    )

    items = parse_s3_list_response(response, delimeter)
    while response["IsTruncated"]:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter=delimeter,
            ContinuationToken=response["NextContinuationToken"],
        )
        items += parse_s3_list_response(response, delimeter)
    return items


def remove_objects_sync(s3_client, bucket, prefix, delimeter=""):
    """Remove all objects in a folder."""
    assert prefix != "" and prefix.endswith("/")
    response = s3_client.list_objects_v2(
        Bucket=bucket, Prefix=prefix, Delimiter=delimeter
    )
    items = response.get("Contents", [])
    if len(items) > 0:
        delete_response = s3_client.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [
                    {
                        "Key": item["Key"],
                        # 'VersionId': 'string'
                    }
                    for item in items
                ],
                "Quiet": True,
            },
        )
        assert (
            "ResponseMetadata" in delete_response
            and delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        )
    while response["IsTruncated"]:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter=delimeter,
            ContinuationToken=response["NextContinuationToken"],
        )
        items = response.get("Contents", [])
        if len(items) > 0:
            delete_response = s3_client.delete_objects(
                Bucket=bucket,
                Delete={
                    "Objects": [
                        {
                            "Key": item["Key"],
                            # 'VersionId': 'string'
                        }
                        for item in items
                    ],
                    "Quiet": True,
                },
            )
            assert (
                "ResponseMetadata" in delete_response
                and delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200
            )


async def list_objects_async(
    s3_client,
    bucket: str,
    prefix: Optional[str] = None,
    delimeter: str = "/",
    max_length: Optional[int] = None,
):
    """List objects async."""
    prefix = prefix or ""
    response = await s3_client.list_objects_v2(
        Bucket=bucket, Prefix=prefix, Delimiter=delimeter
    )
    items = parse_s3_list_response(response, delimeter)
    while response["IsTruncated"]:
        response = await s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter=delimeter,
            ContinuationToken=response["NextContinuationToken"],
        )
        items += parse_s3_list_response(response, delimeter)
        if max_length and len(items) > max_length:
            items = items[:max_length]
            break
    return items


async def remove_objects_async(s3_client, bucket, prefix, delimeter=""):
    """Remove all objects in a folder asynchronously."""
    assert prefix != "" and prefix.endswith("/")
    response = await s3_client.list_objects_v2(
        Bucket=bucket, Prefix=prefix, Delimiter=delimeter
    )
    items = response.get("Contents", [])
    if len(items) > 0:
        delete_response = await s3_client.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [
                    {
                        "Key": item["Key"],
                        # 'VersionId': 'string'
                    }
                    for item in items
                ],
                "Quiet": True,
            },
        )
        assert (
            "ResponseMetadata" in delete_response
            and delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        )
    while response["IsTruncated"]:
        response = await s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter=delimeter,
            ContinuationToken=response["NextContinuationToken"],
        )
        items = response.get("Contents", [])
        if len(items) > 0:
            delete_response = await s3_client.delete_objects(
                Bucket=bucket,
                Delete={
                    "Objects": [
                        {
                            "Key": item["Key"],
                            # 'VersionId': 'string'
                        }
                        for item in items
                    ],
                    "Quiet": True,
                },
            )
            assert (
                "ResponseMetadata" in delete_response
                and delete_response["ResponseMetadata"]["HTTPStatusCode"] == 200
            )


class GZipMiddleware:
    """Middleware to gzip responses (fixed to not encoding twice)."""

    def __init__(
        self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 9
    ) -> None:
        """Initialize the middleware."""
        self.app = app
        self.minimum_size = minimum_size
        self.compresslevel = compresslevel

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Call the middleware."""
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            # Make sure we're not already gzipping
            if (
                "gzip" in headers.get("Accept-Encoding", "")
                and "text/event-stream" not in headers.get("Accept", "text/html")
                and "Content-Encoding" not in headers
            ):
                responder = GZipResponder(
                    self.app, self.minimum_size, compresslevel=self.compresslevel
                )
                await responder(scope, receive, send)
                return
        await self.app(scope, receive, send)


class GzipRequest(Request):
    """Gzip Request."""

    async def body(self) -> bytes:
        """Get the body."""
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            # pylint: disable=attribute-defined-outside-init
            self._body = body
        return self._body


class GzipRoute(APIRoute):
    """Gzip Route."""

    def get_route_handler(self) -> Callable:
        """Get route handler."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


class PatchedCORSMiddleware(CORSMiddleware):
    """
    A patched version of CORS middleware.

    This is required because the CORS middleware does not
    send explicit origin when allow_credentials is True.
    """

    async def send(self, message, send, request_headers) -> None:
        """Send the message."""
        if message["type"] != "http.response.start":
            await send(message)
            return

        message.setdefault("headers", [])
        headers = MutableHeaders(scope=message)
        headers.update(self.simple_headers)
        # We need to first normalize the case of the headers
        # To avoid multiple values in the headers
        # See issue: https://github.com/encode/starlette/issues/1309
        # pylint: disable=protected-access
        items = headers._list
        # pylint: disable=protected-access
        headers._list = [
            (item[0].decode("latin-1").lower().encode("latin-1").title(), item[1])
            for item in items
        ]
        headers = MutableHeaders(headers=dict(headers.items()))

        origin = request_headers["Origin"]
        has_cookie = "cookie" in request_headers
        allow_credential = (
            "Access-Control-Allow-Credentials" in self.simple_headers
            and self.simple_headers["Access-Control-Allow-Credentials"] == "true"
        )

        # If request includes any cookie headers, then we must respond
        # with the specific origin instead of '*'.
        if self.allow_all_origins and (has_cookie or allow_credential):
            self.allow_explicit_origin(headers, origin)

        # If we only allow specific origins, then we have to mirror back
        # the Origin header in the response.
        elif not self.allow_all_origins and self.is_allowed_origin(origin=origin):
            self.allow_explicit_origin(headers, origin)

        message["headers"] = headers.raw
        await send(message)


async def _http_ready_func(url, p, logger=None):
    """Check if the http service is ready."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(url)
            # We only care if we get back *any* response, not just 200
            # If there's an error response, that can be shown directly to the user
            if logger:
                logger.debug(f"Got code {resp.status} back from {url}")
            return True
        except httpx.RequestError as exc:
            if logger:
                logger.debug(f"Connection to {url} failed: {exc}")
            return False


async def launch_external_services(
    server: any,
    command: str,
    name=None,
    env=None,
    check_services=None,
    check_url=None,
    timeout=5,
    logger=None,
):
    """
    Launch external services asynchronously and monitors their status (requires simpervisor).

    Args:
        server: The server instance for which the services are to be launched.
        command (str): The command to be executed to start the service. Any placeholders such as {server_url},
                       {workspace}, and {token} in the command will be replaced with actual values.
        name (str, optional): The name of the service. If not provided, the first argument of the command is used as the name.
        env (dict, optional): A dictionary of environment variables to be set for the service.
        check_services (list, optional): A list of service IDs to be checked for readiness. The service is considered ready
                                          if all services in the list are available.
        check_url (str, optional): A URL to be checked for readiness. The service is considered ready if the URL is accessible.
        timeout (int, optional): The maximum number of seconds to wait for the service to be ready. Defaults to 5.
        logger (logging.Logger, optional): A logger instance to be used for logging messages. If not provided, no messages
                                           are logged.

    Raises:
        Exception: If the service fails to start or does not become ready within the specified timeout.

    Returns:
        proc (SupervisedProcess): The process object for the service. You can call proc.kill() to kill the process.
    """
    from simpervisor import SupervisedProcess

    token = await server.generate_token()
    # format the cmd so we fill in the {server_url} placeholder
    command = command.format(
        server_url=server.config.local_base_url,
        workspace=server.config["workspace"],
        token=token,
    )
    command = [c.strip() for c in command.split() if c.strip()]
    assert len(command) > 0, f"Invalid command: {command}"
    name = name or command[0]
    # split command into list, strip off spaces and filter out empty strings
    server_env = os.environ.copy()
    server_env.update(env or {})

    async def ready_function(p):
        if check_services:
            for service_id in check_services:
                try:
                    await server.get_service(
                        server.config["workspace"] + "/" + service_id
                    )
                except Exception:
                    return False
            return True
        if check_url:
            return await _http_ready_func(check_url, p, logger=logger)
        return True

    proc = SupervisedProcess(
        name,
        *command,
        env=server_env,
        always_restart=False,
        ready_func=ready_function,
        ready_timeout=timeout,
        log=logger,
    )

    try:
        await proc.start()

        is_ready = await proc.ready()

        if not is_ready:
            await proc.kill()
            raise Exception(f"External services ({name}) failed to start")
    except:
        if logger:
            logger.exception(f"External services ({name}) failed to start")
        raise
    return proc


async def _example_hypha_startup(server):
    """An example hypha startup module."""
    assert server.register_codec
    assert server.rpc
    assert server.disconnect
    await server.register_service(
        {
            "id": "example-startup-service",
            "config": {
                "visibility": "public",
                "require_context": False,
            },
            "test": lambda x: x + 22,
        }
    )
