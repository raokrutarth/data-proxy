#!/bin/bash -ex

if ! which poetry; then
    # Install poetry if it's not installed
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    export PATH=${PATH}:"${HOME}/.poetry/bin"
fi

poetry config virtualenvs.in-project true
poetry install

export PYTHONPATH=${PYTHONPATH}:"$(pwd)/app"

if [[ -z "${debug}" ]]; then
    # in production, use gunicorn and it defaults to port 8000. Which is what azure expects.
    poetry run gunicorn --bind=0.0.0.0 -w 4 -k uvicorn.workers.UvicornWorker main:app
else
    export SLACK_PROXY_USERNAME=dev
    export SLACK_PROXY_PASSWORD=dev

    poetry run uvicorn \
        --reload \
        --host 0.0.0.0 \
        --port ${1:-8000} \
        --log-level info \
        --workers 4 \
        main:app
fi