import secrets
import logging
from os import environ
from collections import deque

from fastapi import Depends, HTTPException, status, APIRouter, Request
from starlette.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

log = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBasic()

_USERNAME = environ.get("SLACK_PROXY_USERNAME")
_PASSWORD = environ.get("SLACK_PROXY_PASSWORD")

_EVENT_QUEUE = deque(maxlen=1000)  # TODO check approx memory usage per event


def get_verified_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, _USERNAME)
    correct_password = secrets.compare_digest(credentials.password, _PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/event")
def receive_event(request: Request):
    """
        Endpoint for slack events API verification and receive for:
        https://api.slack.com/events/url_verification
        https://api.slack.com/events-api#url_verification
    """
    payload = request.json()
    if "challenge" in payload:
        # verification step
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=dict(
                challenge=payload["challenge"],
            )
        )
    logging.info(f"Adding payload {payload} to slack event queue.")
    _EVENT_QUEUE.append(payload)

    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get("/event")
def get_latest_event(
    username: str = Depends(get_verified_username),
):
    """
        ...
    """
    if not _EVENT_QUEUE:
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content="No events received. "
        )

    log.info(f"Sending latest slack event to user {username}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dict(event=_EVENT_QUEUE.popleft())
    )
