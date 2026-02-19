# Production environment Dockerfile template
ARG PYTHON_VERSION=python:3.10-slim-bookworm
ARG DEBIAN_MIRROR="http://deb.debian.org/debian testing main"
ARG PYTHON_PACKAGES="httpx==0.27.2 requests==2.32.3 jinja2==3.1.6 PySocks httpx[socks]"
ARG NODEJS_VERSION=v20.11.1
ARG NODEJS_MIRROR="https://npmmirror.com/mirrors/node"
ARG TARGETARCH

FROM ${PYTHON_VERSION}

# Re-declare args after FROM (so they're available in this stage)
ARG DEBIAN_MIRROR
ARG PYTHON_PACKAGES
ARG NODEJS_VERSION
ARG NODEJS_MIRROR
ARG TARGETARCH

# Install system dependencies
RUN set -eux; \
    echo "deb ${DEBIAN_MIRROR}" > /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      pkg-config \
      libseccomp-dev \
      wget \
      curl \
      xz-utils \
      zlib1g \
      expat \
      perl \
      libsqlite3-0 \
      passwd \
    ; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

# Copy binary files
COPY main /main
COPY env /env

# Copy configuration files
COPY docker/conf/config.yaml /conf/config.yaml
COPY dependencies/python-requirements.txt /dependencies/python-requirements.txt
COPY docker/entrypoint.sh /entrypoint.sh

# Set permissions and install python deps
RUN set -eux; \
    chmod +x /main /env /entrypoint.sh; \
    python3 -m pip install --no-cache-dir ${PYTHON_PACKAGES}

# --- Offline Node.js tarball (no network download) ---
# Put your pre-downloaded tarball in the build context at:
#   node/node-v20.11.1-linux-x64.tar.xz
# If you also build for arm64, add the arm64 tarball too and COPY it similarly.
COPY node/node-v20.11.1-linux-x64.tar.xz /opt/node-v20.11.1-linux-x64.tar.xz

# Use pre-downloaded Node.js based on architecture and run environment initialization
RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
      amd64) NODEJS_ARCH="linux-x64" ;; \
      arm64) NODEJS_ARCH="linux-arm64" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    NODE_VER="${NODEJS_VERSION#v}"; \
    export NODE_TAR_XZ="/opt/node-v${NODE_VER}-${NODEJS_ARCH}.tar.xz"; \
    export NODE_DIR="/opt/node-v${NODE_VER}-${NODEJS_ARCH}"; \
    test -f "${NODE_TAR_XZ}"; \
    /env; \
    rm -f /env

# Set environment variables (dynamically set, replaced by generate.sh at runtime)
# Keep defaults for amd64; runtime can override if needed.
ENV NODE_TAR_XZ=/opt/node-v20.11.1-linux-x64.tar.xz
ENV NODE_DIR=/opt/node-v20.11.1-linux-x64

ENTRYPOINT ["/entrypoint.sh"]
