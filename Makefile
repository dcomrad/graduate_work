# Сервис аутентификации
auth-up:
	make -C auth-service up

auth-down:
	make -C auth-service down

auth-down-volumes:
	make -C auth-service down-volumes

# Сервис контента
movies-up:
	make -C movies-service up

movies-down:
	make -C movies-service down

movies-down-volumes:
	make -C movies-service down-volumes

# Сервис уведомлений
notifications-up:
	make -C notifications-service up

notifications-down:
	make -C notifications-service down

notifications-down-volumes:
	make -C notifications-service down-volumes

# Все сервисы
all-up: auth-up movies-up notifications-up

all-down: auth-down movies-down notifications-down

all-down-volumes: auth-down-volumes movies-down-volumes notifications-down-volumes