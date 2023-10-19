# Сервис доступа к контенту кинотеатра

# Приложения
* movies - API сервиса онлайн-кинотеатра (FastAPI)
* admin-panel - админка для редактирования контента онлайн-кинотеатра (Django)
* etl - перенос контента из БД Postgres в Elasticsearch

# Запуск из папки infra
* скопировать env.example => env
* запустить docker compose
```
sudo docker compose --env-file=env/general up --build -d
```