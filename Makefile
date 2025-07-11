.PHONY: help docs

help:
	@echo "Usage:"
	@echo "	make consumer             Run a consumer service locally"
	@echo "	make producer             Run a producer service locally"
	@echo "	make docs                 Run local documentation server"
	@echo "	make test                 CI: Run tests"
	@echo "	make check                CI: Lint the code"
	@echo "	make format               CI: Format the code"
	@echo "	make allci                Run all CI steps (check, format, test)"
	@echo ""
	@echo "Docker Commands:"
	@echo "	make docker-build         Build the docker image"
	@echo "	make docker-build-dev     Build the dev docker image"
	@echo "	make docker-run           Run the docker container"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "	make compose-run          Start services with compose"
	@echo "	make compose-stop         Stop services"
	@echo "	make compose-stop-clean   Stop services and clean volumes"
	@echo "	make show-logs            Show all container logs"
	@echo "	make show-consumer-logs   Show consumer logs"
	@echo "	make show-producer-logs   Show producer logs"
	@echo "	make show-pg-logs         Show postgres logs"
	@echo "	make show-rabbit-logs     Show rabbitmq logs"
	@echo ""
	@echo "Container CLI Access:"
	@echo "	make cli-consumer         Access consumer container shell"
	@echo "	make cli-producer         Access producer container shell"
	@echo "	make cli-postgres         Access postgres container shell"
	@echo "	make cli-rabbit           Access rabbitmq container shell"

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
	uvx --with mkdocstrings --with mkdocs-material --with mkdocstrings-python --with mkdocs-include-markdown-plugin --with mkdocs-mermaid2-plugin mkdocs serve

docker-build:
	docker build -t chronos .

docker-build-dev:
	docker build -t chronos -f .devcontainer/Dockerfile .

docker-run:
	docker run scheduler-service

compose-run:
	docker compose up -d

compose-stop:
	docker compose down

compose-stop-clean:
	docker compose down -v --remove-orphans

show-logs:
	docker compose logs -f

show-consumer-logs:
	docker compose logs -f consumer 

show-producer-logs:
	docker compose logs -f producer

show-pg-logs:
	docker compose logs -f postgres

show-rabbit-logs:
	docker compose logs -f rabbitmq

cli-consumer:
	docker compose exec consumer bash

cli-producer:
	docker compose exec producer bash

cli-postgres:
	docker compose exec postgres bash

cli-rabbit:
	docker compose exec rabbitmq bash


allci:
	$(MAKE) check
	$(MAKE) format
	$(MAKE) test
