.PHONY: format format-check test

format:
	cd java-client && mvn spotless:apply
	cd python-client && ruff check --fix --select I . && ruff format . && ruff check .
	cd go-client && gofmt -w .

format-check:
	cd java-client && mvn spotless:check
	cd python-client && ruff check . && ruff format --check .
	cd go-client && test -z "$$(gofmt -l .)"

test:
	cd java-client && mvn test
	cd python-client && python -m unittest discover -s tests -v
	cd go-client && go vet ./... && go test ./...
