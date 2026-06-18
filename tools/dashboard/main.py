import argparse
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from tools.dashboard.docs_router import router as docs_router
from tools.dashboard.backlog_router import router as backlog_router
from tools.dashboard.state_router import router as state_router

TEMPLATES_DIR = Path(__file__).parent / "templates"


def require_write(request: Request):
    if request.app.state.read_only:
        raise HTTPException(status_code=403, detail="Read-only mode")


def create_app(read_only: bool = False) -> FastAPI:
    app = FastAPI(title="Orquesta Studio")
    app.state.read_only = read_only

    if TEMPLATES_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(TEMPLATES_DIR)), name="static")

    @app.get("/")
    async def index():
        index_file = TEMPLATES_DIR / "index.html"
        return FileResponse(str(index_file))

    app.include_router(docs_router)
    app.include_router(backlog_router)
    app.include_router(state_router)

    return app


def main():
    parser = argparse.ArgumentParser(description="Orquesta Studio Dashboard")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--read-only", action="store_true")
    args = parser.parse_args()

    import uvicorn

    app = create_app(read_only=args.read_only)
    uvicorn.run(app, host="127.0.0.1", port=args.port, reload=False)


if __name__ == "__main__":
    main()
