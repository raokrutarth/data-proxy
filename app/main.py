import logging
import sys
from fastapi import FastAPI, status
from slack_proxy import router as slack_router
from starlette.responses import HTMLResponse

# configure logging with filename, function name and line numbers
logging.basicConfig(
    datefmt='%I:%M:%S %p %Z',
    format='%(levelname)s [%(asctime)s - %(filename)s:%(lineno)s::%(funcName)s]\t%(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)
log = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
def root():
    return HTMLResponse(
        status_code=status.HTTP_200_OK,
        content="<h1>REST Data Proxy</h1>"
    )


app.include_router(
    slack_router,
    prefix="/slack_poxy",
)
