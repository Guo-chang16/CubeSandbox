# syntax=docker/dockerfile:1.7
#
# java-sandbox: JDK 21 + Maven 3.9 on top of cubesandbox-base.
#
# Build:
#   docker build -t java-sandbox:latest examples/java-sandbox
#
# Verify locally:
#   docker run --rm -d --name java-sandbox-test java-sandbox:latest
#   docker exec java-sandbox-test java --version
#   docker exec java-sandbox-test mvn --version
#   curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:49983/health  # => 204
#   docker rm -f java-sandbox-test

ARG CUBE_BASE_IMAGE=ghcr.io/tencentcloud/cubesandbox-base:2026.16
FROM ${CUBE_BASE_IMAGE}

ARG DEBIAN_FRONTEND=noninteractive
ARG JDK_FULL_VERSION=21.0.6+7
ARG MAVEN_VERSION=3.9.9
ARG TARGETARCH

# Map Docker's TARGETARCH (amd64, arm64) to Adoptium's naming (x64, aarch64).
RUN [ -z "$TARGETARCH" ] && TARGETARCH=$(uname -m) || true
RUN arch="${TARGETARCH}"; \
    [ "$arch" = "amd64" ] && arch="x64"; \
    [ "$arch" = "arm64" ] && arch="aarch64"; \
    echo "$arch" > /tmp/jdk_arch

# Install wget for downloads; removed at the end to keep the image lean.
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# Download and install JDK from Adoptium GitHub releases.
# The extracted directory name is discovered dynamically so only
# JDK_FULL_VERSION needs updating on the next security release.
RUN arch=$(cat /tmp/jdk_arch) && \
    majorver=$(echo "${JDK_FULL_VERSION}" | cut -d. -f1) && \
    url="https://github.com/adoptium/temurin${majorver}-binaries/releases/download/jdk-${JDK_FULL_VERSION}/OpenJDK${majorver}U-jdk_${arch}_linux_hotspot_$(echo ${JDK_FULL_VERSION} | tr '+' '_').tar.gz" && \
    wget -q "$url" -O /tmp/jdk.tar.gz && \
    dir=$(tar tzf /tmp/jdk.tar.gz | head -1 | cut -d/ -f1) && \
    tar xzf /tmp/jdk.tar.gz -C /opt && \
    mv "/opt/$dir" "/opt/jdk-${majorver}" && \
    rm /tmp/jdk.tar.gz /tmp/jdk_arch

ENV JAVA_HOME="/opt/jdk-$(echo ${JDK_FULL_VERSION} | cut -d. -f1)"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Download and install Maven
RUN wget -q "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
    -O /tmp/maven.tar.gz \
    && tar xzf /tmp/maven.tar.gz -C /opt \
    && ln -s "/opt/apache-maven-${MAVEN_VERSION}" /opt/maven \
    && rm /tmp/maven.tar.gz \
    && apt-get purge -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV MAVEN_HOME="/opt/maven"
ENV PATH="${MAVEN_HOME}/bin:${PATH}"

# Pre-create workspace owned by the `user` account (uid=1000, provisioned by base image)
RUN mkdir -p /home/user/workspace /home/user/.m2 \
    && chown -R user:user /home/user/workspace /home/user/.m2

WORKDIR /home/user/workspace

EXPOSE 49983
