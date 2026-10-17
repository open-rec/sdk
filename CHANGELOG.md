# Changelog

## Unreleased

- Align Go/Python recommendation diagnostics and HTTP errors with Java (HTTP failures now raise/return errors instead of empty responses).
- Tolerate unknown Python response fields; reject null Go response envelopes.
- Expose Java HTTP configuration, normalize endpoint slashes, and update IDE language level to Java 21.
- Enforce Alibaba Java, PEP 8 Python, and gofmt formatting with shared contract fixtures.

## 0.1.0 — 2026-10-05

First coordinated release. See [release notes](RELEASE_NOTES.md) for features, compatibility and known limitations.
