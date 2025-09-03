# Base OS and configuration
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y curl wget git sudo bash locales ca-certificates && rm -rf /var/lib/apt/lists/*

# Install OpenVSCode Server
RUN curl -fsSL https://github.com/gitpod-io/openvscode-server/releases/download/openvscode-server-v1.103.1/openvscode-server-v1.103.1-linux-x64.tar.gz \
    | tar -xz -C /opt \
    && mv /opt/openvscode-server* /opt/openvscode-server

# Set Hostname
RUN echo framelab > /etc/hostname

# Create non-root user
ARG USERNAME=framelab
ARG USER_UID=1000
ARG USER_GID=1000
RUN if ! getent group $USER_GID >/dev/null; then \
        groupadd -g $USER_GID $USERNAME; \
    fi \
 && if ! id -u $USER_UID >/dev/null 2>&1; then \
        useradd -m -u $USER_UID -g $USER_GID -s /bin/bash $USERNAME; \
    else \
        echo "User with UID $USER_UID already exists, reusing..."; \
    fi \
 && mkdir -p /home/$USERNAME/.openvscode-server/extensions \
 && chown -R $USER_UID:$USER_GID /home/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# Expose port
EXPOSE 3000

# Default command
CMD ["/opt/openvscode-server/bin/openvscode-server", "--host", "0.0.0.0", "--port", "3000", "--without-connection-token"]
