.PHONY: help

help:
	@echo "Usage:"
	@echo "		make consumer								Run a consumer service locally"
	@echo "		make producer								Run a producer service locally"
	@echo	"		make dockerbuild						Build docker image"
	@echo	"		make docs										Run local documentation server"
	@echo	"		make test										CI: Run tests"
	@echo	"		make check									CI: Lint the code"
	@echo	"		make format									CI: Format the code"
	@echo	"		make dockerbuild						Build the docker image"
	@echo	"		make dockerrun							Run the docker image"
	@echo	"		make composebuild						Build with compose.yml"
	@echo	"		make composerun							Run with compose.yml"
	@echo	"		make allci									Run all CI steps (check, format, test)"

consumer:
	uv run src/consumer.py

producer:
	uv run src/producer.py

test:
	@echo "not implemented"

check:
	uv run ruff check $$(git diff --name-only --cached -- '*.py')

format:
	uv run ruff format $$(git diff --name-only --cached -- '*.py')

docs:
	uvx --with mkdocstrings --with mkdocs-material --with mkdocstrings-python --with mkdocs-include-markdown-plugin mkdocs serve

dockerbuild:
	docker build -t scheduler-service .

dockerbuild-dev:
	docker build -t scheduler-service -f .devcontainer/Dockerfile .

dockerrun:
	docker run scheduler-service

allci:
	$(MAKE) check
	$(MAKE) format
	$(MAKE) test
