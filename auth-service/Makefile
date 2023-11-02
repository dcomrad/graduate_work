up:
	@echo "Running auth service ..."
	cd infra && sudo docker compose --env-file=env/general up --build -d

down:
	@echo "Stopping auth service ..."
	cd infra && sudo docker compose --env-file=env/general down

down-volumes:
	@echo "Stopping auth service and removing all volumes ..."
	cd infra && sudo docker compose --env-file=env/general down -v