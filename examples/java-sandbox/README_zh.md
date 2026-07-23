# Java 沙箱

基于 [`cubesandbox-base`](../../docker/Dockerfile.cube-base) 构建的 JDK 21 + Maven 3.9 沙箱镜像，
适用于 Agent 调用 Java 工具 / 轻量 Java 应用执行的场景。

- envd 监听 `:49983`（Cube 就绪探针）— 由基础镜像提供。
- 预装 JDK 21（Eclipse Temurin）和 Maven 3.9.9。

完整教程参见 [自带镜像接入 (envd)](../../docs/zh/guide/tutorials/bring-your-own-image.md)。

## 适用场景

- Agent 需要执行 Java 代码片段或调用 Java 第三方库
- 轻量 JAR 应用的沙箱化运行
- Java 编译 / 单元测试的隔离执行环境
- 教学 / 面试中的 Java 在线编程环境

## 构建镜像

```bash
docker build -t java-sandbox:latest examples/java-sandbox
```

## 本地验证

```bash
docker run --rm -d \
    -p 49983:49983 \
    --name java-sandbox-test \
    java-sandbox:latest

# 验证 JDK 版本
docker exec java-sandbox-test java --version

# 验证 Maven 版本
docker exec java-sandbox-test mvn --version

# 验证 envd 探针：应返回 204
curl -s -o /dev/null -w "envd /health => %{http_code}\n" \
    http://127.0.0.1:49983/health

# 验证非 root 用户
docker exec java-sandbox-test whoami  # => user

docker rm -f java-sandbox-test
```

## 注册为 Cube 模板

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

## E2B SDK 调用示例

注册模板后，运行示例脚本：

### hello_java.py — 编译并执行单个 Java 类

```bash
pip install -r requirements.txt

cp .env.example .env
# 填入 E2B_API_URL 和 CUBE_TEMPLATE_ID

python hello_java.py
```

预期输出：

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

### maven_build.py — 构建并运行 Maven 项目

```bash
python maven_build.py
```

该脚本在沙箱内动态创建一个包含 Gson 依赖的最小 Maven 项目，然后执行
`mvn compile exec:java`。

## 资源建议

| 场景 | CPU | 内存 | 可写层 |
|------|:---:|------|:------:|
| 单文件编译执行 | 1 | 512Mi | 1G |
| Maven 小型项目 | 2 | 1Gi | 2G |
| Maven 中型项目（含单测） | 2 | 2Gi | 5G |

## 已知限制

- 不支持 GUI / AWT / Swing 应用
- Maven 依赖在沙箱首次运行时下载；离线环境建议在 Docker 镜像中预置依赖
- JNI / 原生库兼容 glibc（Ubuntu 22.04 基础镜像）
- 出口网络默认受限；如需访问 Maven Central 以外的外部仓库，请在创建沙箱时
  配置 `allow_out`
