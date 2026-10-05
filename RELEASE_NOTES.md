# sdk v0.1.0

Released: 2026-10-05

Java, Go and Python clients. First coordinated OpenRec source release.

## Features

- Batched user, item and event ingestion with versioned mutation-compatible fields.
- Typed item and user recommendation methods plus the legacy item endpoint.
- Request IDs, recommendation diagnostics and explicit HTTP/application error handling.
- Shared Java rec-proto types and cross-language field-contract verification.
- Standalone unit tests for all three clients.

## Installation and compatibility

Java requires JDK 21 and `com.openrec:rec-proto:0.1.0`; the client artifact is `com.openrec:rec-client:0.1.0`. Python package metadata is `openrec-client==0.1.0`; Go sources are in `go-client`.

Build/install from the tagged source. The Go submodule also has a `go-client/v0.1.0` tag for `go get github.com/open-rec/sdk/go-client@v0.1.0`. This release does not publish packages to Maven Central or PyPI. Push batches are not atomic; preserve entity/event IDs when retrying. Clients must handle HTTP 503 until recommendation warmup completes.

## Validation and known boundaries

See this repository's README for build/test commands and deployment requirements. The coordinated release's [validation record](https://github.com/open-rec/openrec/blob/v0.1.0/release/VALIDATION.md) distinguishes checks executed for this release from historical integration evidence.

This initial release establishes a versioned source baseline. Source archives and checksums are published; external package registries and container registries are not populated by the source-release workflow. Upgrade the complete compatible distribution, retain data/checkpoints/artifacts, and preserve prior component refs for rollback.
