#!/bin/bash -ex

SRC_DIRS="./app ./tests"

poetry run autoflake \
    --remove-all-unused-imports \
    --recursive \
    --remove-unused-variables \
    --in-place \
    --exclude=__init__.py \
    ${SRC_DIRS}

poetry run isort \
    --multi-line=3 \
    --trailing-comma \
    --force-grid-wrap=0 \
    --combine-as \
    --line-width 88 \
    ${SRC_DIRS}

poetry run black ${SRC_DIRS}

poetry run mypy \
    --ignore-missing-imports \
    ${SRC_DIRS}