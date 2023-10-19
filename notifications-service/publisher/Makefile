PROJECT_FOLDERS= bin libs tests

.PHONY: init
init:
	@echo "Installing..."
	@poetry install

.PHONY: lint-fix
lint-fix:	
	@echo "Running black autofixes..."
	@poetry run black .

	@echo "Running isort autofixes..."
	@poetry run isort .

	@echo "Running toml-sort autofixes..."
	@poetry run toml-sort --in-place pyproject.toml

.PHONY: lint
lint:	
	@echo "Running isort autofixes..."
	@poetry run pylint ./notifications	

.PHONY: docker-tests
docker-tests:	
	@echo "Running tests ..."
	@docker-compose -f docker-compose.unit_tests.yml --env-file=.env.dev up --build \
		--abort-on-container-exit \
		--exit-code-from tests
	@docker-compose -f docker-compose.functional_tests.yml --env-file=.env.dev up --build \
		--abort-on-container-exit \
		--exit-code-from tests	
	
.PHONY: tests-cov
tests-cov:	
	@echo "Running tests coverages ..."
	@poetry run pytest --cov tests/unit
	@poetry run pytest --cov tests/functional	


.PHONY: docker-up-build-dev
docker-up-build-dev:	
	@echo "Running app ..."
	docker compose -f docker-compose.dev.yml --env-file=.env.dev up --build

.PHONY: docker-up-build-prod
docker-up-build-prod:	
	@echo "Running app ..."
	@docker compose -f docker-compose.prod.yml --env-file=.env.prod up --build

.PHONY: docker-down
docker-down:	
	@echo "Stopping app ..."
	@docker compose -f docker-compose.prod.yml --env-file=.env.prod down

.PHONY: docker-prune
docker-prune:	
	@echo "Cleaning docker containers and volumes ..."
	@docker container prune
	@docker volume prune

	
	


