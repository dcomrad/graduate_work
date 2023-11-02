up:
	@echo "Running movies service ..."
	cd infra && sudo docker compose --env-file=env/general up --build -d

down:
	@echo "Stopping movies service ..."
	cd infra && sudo docker compose --env-file=env/general down

down-volumes:
	@echo "Stopping movies service and removing all volumes ..."
	cd infra && sudo docker compose --env-file=env/general down -v