"""
Render entry point — wraps main.app and adds static file serving.
Not used in local development (run.sh uses main:app directly).
"""
import pathlib
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from main import app  # noqa: F401 — registers all routes

# The root GET "/" in main.py returns a JSON health probe which would
# shadow the React index.html. Remove it so StaticFiles can serve index.html.
app.routes[:] = [
    r for r in app.routes
    if not (getattr(r, "path", "") == "/" and "GET" in getattr(r, "methods", set()))
]

_static = pathlib.Path(__file__).parent / "static"
if _static.exists():
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
