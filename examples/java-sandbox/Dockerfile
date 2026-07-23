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
ARG JDK_VERSION=21
ARG MAVEN_VERSION=3.9.9

# Install JDK 21 via Adoptium APT repo
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public \
    | gpg --dearmor -o /usr/share/keyrings/adoptium-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/adoptium-archive-keyring.gpg] https://packages.adoptium.net/artifactory/deb ubuntu-jammy main" \
    > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        "temurin-${JDK_VERSION}-jdk=${JDK_VERSION}*" \
    && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ENV JAVA_HOME="/usr/lib/jvm/temurin-${JDK_VERSION}-jdk-${TARGETARCH}"

# Install Maven
RUN wget -q "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
    && tar xzf "apache-maven-${MAVEN_VERSION}-bin.tar.gz" -C /opt \
    && ln -s "/opt/apache-maven-${MAVEN_VERSION}" /opt/maven \
    && rm "apache-maven-${MAVEN_VERSION}-bin.tar.gz"

ENV MAVEN_HOME="/opt/maven"
ENV PATH="${JAVA_HOME}/bin:${MAVEN_HOME}/bin:${PATH}"

# Pre-create workspace owned by the `user` account (uid=1000, provisioned by base image)
RUN mkdir -p /home/user/workspace /home/user/.m2 \
    && chown -R user:user /home/user/workspace /home/user/.m2

WORKDIR /home/user/workspace

EXPOSE 49983