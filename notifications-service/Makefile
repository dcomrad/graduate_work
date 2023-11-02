up:
	@echo "Running notifications service ..."
	cd infra && sudo docker compose --env-file=env/general up --build -d

down:
	@echo "Stopping notifications service ..."
	cd infra && sudo docker compose --env-file=env/general down

down-volumes:
	@echo "Stopping notifications service and removing all volumes ..."
	cd infra && sudo docker compose --env-file=env/general down -v