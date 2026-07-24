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
ARG JDK_MAJOR=21
ARG MAVEN_VERSION=3.9.9
ARG TARGETARCH

# Install wget, download & checksum-verify JDK and Maven, then purge wget.
# All in one RUN layer so the purge actually shrinks the final image.
# ${TARGETARCH:-$(uname -m)} reads the build-arg if set (BuildKit),
# falling back to `uname -m` for non-BuildKit builds. Map Docker's
# naming (amd64/arm64/x86_64) to Adoptium's naming (x64/aarch64).
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/* \
    && arch="${TARGETARCH:-$(uname -m)}"; \
       [ "$arch" = "x86_64" ] && arch="x64"; \
       [ "$arch" = "amd64" ]  && arch="x64"; \
       [ "$arch" = "arm64" ]  && arch="aarch64"; \
       [ "$arch" = "arm" ]    && { echo "Adoptium has no JDK 21 build for 32-bit ARM" >&2; exit 1; }; \
       jdk_url="https://github.com/adoptium/temurin${JDK_MAJOR}-binaries/releases/download/jdk-${JDK_FULL_VERSION}/OpenJDK${JDK_MAJOR}U-jdk_${arch}_linux_hotspot_$(echo ${JDK_FULL_VERSION} | tr '+' '_').tar.gz"; \
       mvn_url="https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
    && wget -q "$jdk_url.sha256" -O /tmp/jdk.tar.gz.sha256 \
    && wget -q "$jdk_url" -O /tmp/jdk.tar.gz \
    && sha256sum -c /tmp/jdk.tar.gz.sha256 \
    && dir=$(tar tzf /tmp/jdk.tar.gz | head -1 | cut -d/ -f1) \
    && tar xzf /tmp/jdk.tar.gz -C /opt \
    && mv "/opt/$dir" "/opt/jdk-${JDK_MAJOR}" \
    && rm /tmp/jdk.tar.gz /tmp/jdk.tar.gz.sha256 \
    && wget -q "$mvn_url.sha512" -O /tmp/maven.tar.gz.sha512 \
    && wget -q "$mvn_url" -O /tmp/maven.tar.gz \
    && sha512sum -c /tmp/maven.tar.gz.sha512 \
    && tar xzf /tmp/maven.tar.gz -C /opt \
    && ln -s "/opt/apache-maven-${MAVEN_VERSION}" /opt/maven \
    && rm /tmp/maven.tar.gz /tmp/maven.tar.gz.sha512 \
    && apt-get purge -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME="/opt/jdk-${JDK_MAJOR}"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

ENV MAVEN_HOME="/opt/maven"
ENV PATH="${MAVEN_HOME}/bin:${PATH}"

# Pre-create workspace owned by the `user` account (uid=1000, provisioned by base image)
RUN mkdir -p /home/user/workspace /home/user/.m2 \
    && chown -R user:user /home/user/workspace /home/user/.m2

WORKDIR /home/user/workspace

EXPOSE 49983
