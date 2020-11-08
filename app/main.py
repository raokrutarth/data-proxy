import logging
import sys

from fastapi import FastAPI, status
from slack_proxy import router as slack_router
from starlette.responses import HTMLResponse
from generic_proxy import router as generic_router

# configure logging with filename, function name and line numbers
logging.basicConfig(
    datefmt="%I:%M:%S %p %Z",
    format="%(levelname)s [%(asctime)s - %(filename)s:%(lineno)s::%(funcName)s]\t%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)
log = logging.getLogger(__name__)

app = FastAPI(
    title="Data Proxy",
    description="REST based data proxy server to facilitate data exchange between services in private networks.",
)


@app.get("/")
def root():
    return HTMLResponse(
        status_code=status.HTTP_200_OK,
        content="<h1>REST Data Proxy. See /docs or /redoc for available endpoints.</h1>",
    )


app.include_router(
    slack_router,
    prefix="/slack_poxy",
)

app.include_router(
    generic_router,
    prefix="/generic_proxy"
)
