from aiohttp.web import Request, Response


async def index(request: Request) -> Response: # noqa: ARG001
    return Response(text="Hello, world!")
