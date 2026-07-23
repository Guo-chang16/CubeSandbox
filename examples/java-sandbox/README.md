# Java Sandbox

A Cube-ready sandbox image with JDK 21 and Maven 3.9, built on top of
[`cubesandbox-base`](../../docker/Dockerfile.cube-base). Suitable for
Agent-driven Java code execution and lightweight JAR application hosting.

- envd listens on `:49983` (Cube readiness probe) — inherited from the base image.
- JDK 21 (Eclipse Temurin) and Maven 3.9.9 are preinstalled under `/opt/maven`.

See [Bring Your Own Image (envd)](../../docs/guide/tutorials/bring-your-own-image.md)
for the full tutorial.

## Use Cases

- Agent executes Java code snippets or calls third-party Java libraries
- Sandboxed execution of lightweight JAR applications
- Isolated Java compilation / unit-test environment
- Online Java programming environment for teaching or interviewing

## Build

```bash
docker build -t java-sandbox:latest examples/java-sandbox
```

## Run & verify locally

```bash
docker run --rm -d \
    -p 49983:49983 \
    --name java-sandbox-test \
    java-sandbox:latest

# JDK version
docker exec java-sandbox-test java --version

# Maven version
docker exec java-sandbox-test mvn --version

# envd readiness probe: should return 204
curl -s -o /dev/null -w "envd /health => %{http_code}\n" \
    http://127.0.0.1:49983/health

# Confirm non-root user
docker exec java-sandbox-test whoami  # => user

docker rm -f java-sandbox-test
```

## Register as a Cube template

```bash
docker tag  java-sandbox:latest <your-registry>/java-sandbox:v1.0.0
docker push <your-registry>/java-sandbox:v1.0.0

cubemastercli tpl create-from-image \
    --image       <your-registry>/java-sandbox:v1.0.0 \
    --writable-layer-size 2G \
    --expose-port 49983 \
    --probe       49983 \
    --probe-path  /health
```

## Try it with the E2B SDK

After registering the template, run the demo scripts:

### hello_java.py — compile & run a single Java class

```bash
pip install -r requirements.txt

cp .env.example .env
# fill in E2B_API_URL and CUBE_TEMPLATE_ID

python hello_java.py
```

Expected output:

```
=== sandbox info ===
...
=== java --version ===
openjdk version "21.x.x" ...
=== mvn --version ===
Apache Maven 3.9.9 ...
=== upload & compile HelloSandbox.java ===
javac: compiled successfully
=== run HelloSandbox ===
=== CubeSandbox Java Runtime ===
Java version: 21.x.x
OS:           Linux
User:         user
```

### maven_build.py — build & run a Maven project

```bash
python maven_build.py
```

This script creates a minimal Maven project with a Gson dependency on
the fly, then runs `mvn compile exec:java` inside the sandbox.

## Resource Recommendations

| Scenario | CPU | Memory | Writable Layer |
|----------|:---:|--------|:--------------:|
| Single-file compile & run | 1 | 512Mi | 1G |
| Small Maven project | 2 | 1Gi | 2G |
| Medium Maven project (with tests) | 2 | 2Gi | 5G |

## Known Limitations

- No GUI / AWT / Swing support
- Maven dependencies are downloaded on first use inside the sandbox; for
  offline environments, pre-seed dependencies in the Docker image
- JNI libraries that depend on glibc are compatible (Ubuntu 22.04 base)
- Egress network is restricted by default; configure `allow_out` at sandbox
  creation time if your project needs external repositories beyond Maven
  Central
