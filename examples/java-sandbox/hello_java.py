# Copyright (c) 2024 Tencent Inc.
# SPDX-License-Identifier: Apache-2.0

"""hello_java.py — compile & run a Java class inside a Cube sandbox."""

import os
import sys
from pathlib import Path
from env_utils import load_local_dotenv
from e2b_code_interpreter import Sandbox

load_local_dotenv()

template_id = os.environ["CUBE_TEMPLATE_ID"]

java_source = (Path(__file__).parent / "HelloSandbox.java").read_text()

ok = True

with Sandbox.create(template=template_id) as sandbox:
    print("=== sandbox info ===")
    print(sandbox.get_info())

    print("\n=== java --version ===")
    result = sandbox.commands.run("java --version")
    print(result.stdout)

    print("\n=== mvn --version ===")
    result = sandbox.commands.run("mvn --version")
    print(result.stdout)

    print("\n=== upload & compile HelloSandbox.java ===")
    sandbox.files.write("HelloSandbox.java", java_source)
    result = sandbox.commands.run("javac HelloSandbox.java")

    if result.exit_code != 0:
        print("javac FAILED:")
        print(result.stderr)
        ok = False

    if ok:
        print("javac: compiled successfully")

        print("\n=== run HelloSandbox ===")
        result = sandbox.commands.run("java HelloSandbox")
        if result.exit_code != 0:
            print("java FAILED:")
            print(result.stderr)
            ok = False

    if ok:
        print(result.stdout)

if not ok:
    sys.exit(1)
