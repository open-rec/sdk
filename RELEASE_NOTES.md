# sdk v0.2.0

Released: 2026-10-18

Part of the coordinated OpenRec v0.2.0 source release.

## Changes since v0.1.0

- Align Java, Go and Python recommendation diagnostics and HTTP error handling.
- Tolerate unknown Python response fields and reject null Go response envelopes.
- Expose Java HTTP configuration and share cross-language contract fixtures.

## Installation and compatibility

Java requires JDK 21 and com.openrec:rec-proto:0.2.0; the client artifact is com.openrec:rec-client:0.2.0. Python metadata is openrec-client==0.2.0. The Go module additionally uses go-client/v0.2.0 for go get github.com/open-rec/sdk/go-client@v0.2.0. HTTP failures now raise/return errors in Go/Python; callers must handle them explicitly.

See the [distribution upgrade and rollback instructions](https://github.com/open-rec/openrec/blob/v0.2.0/RELEASE_NOTES.md) for the complete compatible component set and persisted configuration migrations.

## Validation and publication

The [validation record](https://github.com/open-rec/openrec/blob/v0.2.0/release/VALIDATION.md) distinguishes release checks from maintainer-reported prior CI and integration results. GitHub Actions publishes source archives and SHA-256 checksums; Maven Central, PyPI and versioned container registries are not populated by this workflow.
