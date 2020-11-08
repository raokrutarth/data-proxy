#!/bin/bash -ex

if ! which poetry; then
    # Install poetry if it's not installed
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    export PATH=${PATH}:"${HOME}/.poetry/bin"
fi

poetry install

export PYTHONPATH=${PYTHONPATH}:"$(pwd)/app"

# poetry run uvicorn \
#     --host 0.0.0.0 \
#     --port ${1:-443} \
#     --log-level info \
#     --workers 4 \
#     main:app
poetry run gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app