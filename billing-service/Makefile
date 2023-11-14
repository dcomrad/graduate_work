up:
	@echo "Running billing service ..."
	cd infra && sudo docker compose --env-file=env/general up --build -d

down:
	@echo "Stopping billing service ..."
	cd infra && sudo docker compose --env-file=env/general down

down-volumes:
	@echo "Stopping billing service and removing all volumes ..."
	cd infra && sudo docker compose --env-file=env/general down -v

dev-up:
	@echo "Running billing service in a development mode ..."
	cd infra && sudo docker compose -f docker-compose.yaml -f docker-compose-dev.yaml --env-file=env/general up --build -d

dev-down:
	@echo "Stopping billing service in a development mode ..."
	cd infra && sudo docker compose -f docker-compose.yaml -f docker-compose-dev.yaml --env-file=env/general down

dev-down-volumes:
	@echo "Stopping billing service and removing all volumes in a development mode ..."
	cd infra && sudo docker compose -f docker-compose.yaml -f docker-compose-dev.yaml --env-file=env/general down -v

dev-test-up:
	@echo "Running tests for billing service ..."
	cd infra && sudo docker compose -f docker-compose.yaml -f docker-compose-test.yaml --env-file=env/general up --build -d

dev-test-down:
	@echo "Cleaning from test staff ..."
	cd infra && sudo docker compose -f docker-compose.yaml -f docker-compose-test.yaml --env-file=env/general down -v