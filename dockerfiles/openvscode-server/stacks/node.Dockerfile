# Build arg to select base image tag/name
ARG BASE_IMAGE=openvscode-base:latest
FROM ${BASE_IMAGE}

USER root
RUN set -eux; \
    apt-get update; \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -; \
    apt-get install -y --no-install-recommends nodejs git && \
    npm i -g pnpm yarn && \
    rm -rf /var/lib/apt/lists/*

USER developer

ENV NODE_OPTIONS="--max-old-space-size=4096"


