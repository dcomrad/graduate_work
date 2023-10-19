# UGC сервис

# Приложения
* ugc - API сервиса UGC (FastAPI)
* etl-progress - агрегация и перенос данных о текущем прогрессе просмотра из Kafka в Redis

# Запуск из папки infra 
* скопировать env.example => env
* запустить docker compose
```
sudo docker compose --env-file=env/general up --build -d
```
* запустить bash скрипт для инициализации MongoDB кластера
```
sudo bash configure-mongo.sh
```