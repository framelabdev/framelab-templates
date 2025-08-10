ARG OPENVSCODE_VERSION=1.93.0

FROM debian:bookworm-slim AS base

ENV DEBIAN_FRONTEND=noninteractive \
    OPENVSCODE_SERVER_DIR=/opt/openvscode-server \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      dumb-init \
      git \
      locales \
      unzip \
      xz-utils \
      bash \
      procps \
      wget && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${OPENVSCODE_SERVER_DIR}

# Download OpenVSCode Server release
RUN set -eux; \
    curl -fsSL -o /tmp/openvscode.tar.gz \
      https://github.com/gitpod-io/openvscode-server/releases/download/openvscode-server-v1.102.3/openvscode-server-v1.102.3-linux-x64.tar.gz; \
    tar -xzf /tmp/openvscode.tar.gz --strip-components=1 -C ${OPENVSCODE_SERVER_DIR}; \
    rm -f /tmp/openvscode.tar.gz

# App data locations
RUN mkdir -p /data/user-data /data/extensions

# Non-root user
ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} /data

# Copy custom product details (branding)
# Build context is the template root (dockerfiles/openvscode-server)
COPY config/product.json ${OPENVSCODE_SERVER_DIR}/resources/app/product.json

# Preinstall extensions if provided
COPY extensions/extensions.txt /tmp/extensions.txt
COPY scripts/install-extensions.sh /usr/local/bin/install-extensions
RUN chmod +x /usr/local/bin/install-extensions && /usr/local/bin/install-extensions /tmp/extensions.txt || true && \
    chown -R ${USERNAME}:${USERNAME} /data

# Entrypoint
COPY base/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 3000

USER ${USERNAME}
WORKDIR /workspace

ENV PORT=3000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/usr/local/bin/entrypoint.sh"]


