.PHONY: shell install extract-oab test coverage db-up db-down

shell:
	poetry run $(SHELL)

install:
	poetry install --no-root

extract-oab:
	poetry run python -c "from question_ingestion.oab import OABQuestionPipeline; OABQuestionPipeline().extract()"

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=. --cov-report=term-missing

db-up:
	docker compose up -d --wait

db-down:
	docker compose down
