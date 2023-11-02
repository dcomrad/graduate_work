up:
	@echo "Running ugc service ..."
	cd infra && sudo docker compose --env-file=env/general up --build -d

down:
	@echo "Stopping ugc service ..."
	cd infra && sudo docker compose --env-file=env/general down

down-volumes:
	@echo "Stopping ugc service and removing all volumes ..."
	cd infra && sudo docker compose --env-file=env/general down -v