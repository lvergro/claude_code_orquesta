from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api")


@router.get("/backlog")
def backlog():
    return HTMLResponse('<div id="content-inner">Coming soon...</div>')
