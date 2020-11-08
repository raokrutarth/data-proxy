import logging
import sys
from fastapi import FastAPI
from slack_proxy import router as slack_router

# configure logging with filename, function name and line numbers
logging.basicConfig(
    datefmt='%I:%M:%S %p %Z',
    format='%(levelname)s [%(asctime)s - %(filename)s:%(lineno)s::%(funcName)s]\t%(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)
log = logging.getLogger(__name__)

app = FastAPI()


app.include_router(
    slack_router,
    prefix="/slack_poxy",
)
