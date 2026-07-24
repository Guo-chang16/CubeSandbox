// Copyright (c) 2024 Tencent Inc.
// SPDX-License-Identifier: Apache-2.0

// HelloSandbox.java
// Compile: javac HelloSandbox.java
// Run:     java HelloSandbox
public class HelloSandbox {
    public static void main(String[] args) {
        System.out.println("=== CubeSandbox Java Runtime ===");
        System.out.println("Java version: " + System.getProperty("java.version"));
        System.out.println("Java home:    " + System.getProperty("java.home"));
        System.out.println("OS:           " + System.getProperty("os.name"));
        System.out.println("User:         " + System.getProperty("user.name"));
        System.out.println("Workspace:    " + System.getProperty("user.dir"));
    }
}
