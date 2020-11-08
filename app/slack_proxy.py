import logging
import secrets
from collections import deque
from os import environ
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import JSONResponse

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


class Handshake(BaseModel):
    token: str
    challenge: str
    type: str


@router.post("/event")
async def receive_event(
    body: Any = Body(...),
):
    """
    Endpoint for slack events API verification and receive for

    https://api.slack.com/events/url_verification
    https://api.slack.com/events-api#url_verification
    """
    if "token" not in body or "type" not in body:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Request body missing required fields.",
        )

    if "challenge" in body:
        # verification step
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=dict(
                challenge=body["challenge"],
            ),
        )

    logging.info(f"Adding payload {body} to slack event queue.")
    _EVENT_QUEUE.append(body)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=dict(status="Event saved.")
    )


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
            content="No available events present.",
        )

    log.info(f"Sending latest slack event to user {username}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dict(
            event=_EVENT_QUEUE.popleft(),
            events_left_in_queue=len(_EVENT_QUEUE),
        ),
    )
