import logging
import sys

from fastapi import FastAPI, status
from generic_proxy import router as generic_router
from slack_proxy import router as slack_router
from starlette.responses import HTMLResponse
from os import environ

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
    # hosted_site = environ.get("WEBSITE_HOSTNAME")
    redoc_button = "<button onclick=\"document.location='redoc'\">redoc</button>"
    docs_button = "<button onclick=\"document.location='docs'\">docs</button>"
    message = f'REST Data Proxy<br>See {docs_button} or {redoc_button} for available endpoints.'

    return HTMLResponse(
        status_code=status.HTTP_200_OK,
        content="""
<!doctype html>
<title>Data Proxy</title>
<style>
  body { text-align: center; padding: 150px; }
  h1 { font-size: 50px; }
  body { font: 20px Helvetica, sans-serif; color: #333; }
  article { display: block; text-align: center; width: 650px; margin: 0 auto; }
  a { color: #dc8100; text-decoration: none; }
  a:hover { color: #333; text-decoration: none; }
  button { color: #dc8100; text-decoration: none; }
  button:hover { color: #333; text-decoration: none; }
</style>

<article>
    <div>
        <p>%s</p>
    </div>
</article>
        """ % (message),
    )


app.include_router(
    slack_router,
    prefix="/slack_poxy",
)

app.include_router(
    generic_router,
    prefix="/generic_proxy",
)
