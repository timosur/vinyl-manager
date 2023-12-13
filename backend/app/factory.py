from fastapi import FastAPI, Depends,Security
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse

from app.api import api_router
from app.core.config import settings
from app.deps.users import azure_scheme

def create_app():
    description = f"{settings.PROJECT_NAME} API"

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_PATH}/openapi.json",
        docs_url="/docs/",
        description=description,
        redoc_url=None,
        swagger_ui_oauth2_redirect_url='/oauth2-redirect',
        swagger_ui_init_oauth={
            'usePkceWithAuthorizationCodeGrant': True,
            'clientId': settings.OPENAPI_CLIENT_ID,
        },
    )
    setup_routers(app)
    setup_cors_middleware(app)
    serve_static_app(app)

    return app


def setup_routers(app: FastAPI) -> None:
    app.include_router(api_router, prefix=settings.API_PATH, dependencies=[Security(azure_scheme, scopes=['user.access'])])

    # The following operation needs to be at the end of this function
    use_route_names_as_operation_ids(app)

def serve_static_app(app):
    app.mount("/", StaticFiles(directory="static"), name="static")

    @app.middleware("http")
    async def _add_404_middleware(request: Request, call_next):
        """Serves static assets on 404"""
        response = await call_next(request)
        path = request["path"]
        if path.startswith(settings.API_PATH) or path.startswith("/docs"):
            return response
        if response.status_code == 404:
            return FileResponse("static/index.html")
        return response


def setup_cors_middleware(app):
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            expose_headers=["Content-Range", "Range"],
            allow_headers=['*'],
        )


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    route_names = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in route_names:
                raise Exception("Route function names should be unique")
            route.operation_id = route.name
            route_names.add(route.name)
