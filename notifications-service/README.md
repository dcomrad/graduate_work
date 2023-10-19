# Сервис уведомлений

# Приложения
* admin-panel - админка для редактирования шаблонов уведомлений, мгновенной
отправки и планирования отправки уведомлений (Django) 
* publisher - API сервиса уведомлений (FastAPI)
* worker - отправка уведомлений

# Запуск из папки infra
* скопировать env.example => env
* запустить docker compose
```
sudo docker compose --env-file=env/general up --build -d
```