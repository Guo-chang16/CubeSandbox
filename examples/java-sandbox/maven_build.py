# Copyright (c) 2024 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

"""maven_build.py — build & run a Maven project inside a Cube sandbox."""

import os
from pathlib import Path
from dotenv import load_dotenv
from e2b import Sandbox

load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)

template_id = os.environ["CUBE_TEMPLATE_ID"]

pom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>hello-maven</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.11.0</version>
        </dependency>
    </dependencies>
</project>"""

app_java = """package com.example;

import com.google.gson.Gson;
import java.util.Map;

public class App {
    public static void main(String[] args) {
        Map<String, String> info = Map.of(
            "runtime", "CubeSandbox Java",
            "jdk", System.getProperty("java.version"),
            "user", System.getProperty("user.name")
        );
        System.out.println(new Gson().toJson(info));
    }
}"""

with Sandbox.create(template=template_id) as sandbox:
    print("=== creating Maven project ===")
    sandbox.commands.run("mkdir -p src/main/java/com/example")
    sandbox.files.write("pom.xml", pom_xml)
    sandbox.files.write("src/main/java/com/example/App.java", app_java)

    print("\n=== mvn compile ===")
    result = sandbox.commands.run(
        "mvn --batch-mode compile",
        on_stdout=lambda line: print(f"  [mvn] {line}"),
    )
    if result.exit_code != 0:
        print(f"mvn compile FAILED (exit={result.exit_code})")
        print(result.stderr)
        exit(1)

    print("\n=== mvn exec:java ===")
    result = sandbox.commands.run(
        "mvn --batch-mode exec:java -Dexec.mainClass=com.example.App",
        on_stdout=lambda line: print(f"  [mvn] {line}"),
    )