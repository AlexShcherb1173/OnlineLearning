# OnlineLearning — платформа онлайн-обучения (Django + DRF)

### OnlineLearning — учебный проект на Django 5 + DRF, реализующий функционал пользователей, курсов, уроков и истории платежей.
#### Проект демонстрирует работу с кастомной моделью пользователя, сериализаторами, viewset’ами, generic-классами, фильтрацией и вложенными данными.

### Содержание

- [Функционал](#функционал)
- [Технологии](#технологии)
- [Установка и запуск](#установка-и-запуск)
- [Миграции и фикстуры](#миграции-и-фикстуры)
- [Структура проекта](#структура-проекта)
- [API эндпоинты](#api-эндпоинты)
  - [Пользователи](#пользователи)
  - [Курсы и уроки](#курсы-и-уроки)
  - [Платежи](#платежи)
- [Модели](#модели)
- [Роли и права доступа](#роли-и-права-доступа)
- [Админ-панель](#админ-панель)
- [Форматирование кода](#форматирование-кода)
- [Лицензия](#лицензия)

### Функционал

#### Пользователи
кастомная модель User, авторизация по email  
дополнительные поля: телефон, город, аватар  
просмотр и редактирование профиля  
просмотр истории платежей пользователя  
#### Курсы и уроки
модель Course + вложенные Lesson  
вывод количества уроков курса (lessons_count)  
вложенный вывод списка уроков (lessons)  
CRUD для курса через ModelViewSet  
CRUD для уроков через generics APIView  
#### Платежи
модель Payment с поддержкой:  
оплаты курса или урока  
суммы  
способа оплаты (наличные / перевод)  
CheckConstraint: либо курс, либо урок, но не оба  
фильтрация платежей:  
по курсу  
по уроку  
по способу оплаты  
сортировка по дате оплаты  
вывод истории платежей профиля  
### Технологии
Python 3.13  
Django 5.x  
Django REST Framework  
PostgreSQL  
python-dotenv  
Pillow (для изображений)  
flake8 / black / isort  
### Установка и запуск
1️⃣ Клонируем репозиторий  
git clone https://github.com/<your_name>/OnlineLearning.git  
cd OnlineLearning  

2️⃣ Создаем виртуальное окружение  
python -m venv .venv  
source .venv/bin/activate   # Linux/Mac  
.venv\Scripts\activate      # Windows  

3️⃣ Устанавливаем зависимости  
pip install -r requirements.txt  

4️⃣ Настраиваем .env  

Создайте .env в корне:  

DJANGO_SECRET_KEY=dev-secret  
DJANGO_DEBUG=True  

POSTGRES_DB=OnlineLearning_db  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_HOST=127.0.0.1  
POSTGRES_PORT=5432  

SMTP_HOST=smtp.example.com  
SMTP_USER=  
SMTP_PASSWORD=  
SMTP_USE_TLS=True  

5️⃣ Применяем миграции  
python manage.py migrate  

6️⃣ Создаем суперпользователя  
python manage.py createsuperuser  

7️⃣ Запускаем сервер  
python manage.py runserver  

### Миграции и фикстуры

Загрузка тестовых пользователей, курсов, уроков и платежей:

python manage.py loaddata users  
python manage.py loaddata courses  
python manage.py loaddata lessons  
python manage.py loaddata payments  

### Структура проекта
OnlineLearning/  
│  
├── config/                 # настройки Django  
├── users/                  # кастомный пользователь + платежи + API  
├── lms/                    # курсы, уроки, API  
├── media/                  # загружаемые изображения  
├── .flake8                 # конфиг линтера  
├── pyproject.toml          # конфиг black/isort  
└── README.md               # этот файл  

### API эндпоинты
#### Пользователи
###### Список пользователей
GET /api/users/
###### Редактирование пользователя
PUT/PATCH /api/users/<id>/
###### Профиль пользователя
GET /api/users/profiles/<id>/  
История платежей в профиле
автоматически включена как поле payments
##### Профили пользователей и права доступа
В проекте реализована логика разграничения доступа к профилям пользователей.
###### Общие правила
Любой авторизованный пользователь может просматривать профиль любого пользователя.  
Редактировать профиль можно только свой собственный.  
При просмотре чужого профиля скрывается часть полей.  
###### Эндпоинт профиля
Просмотр и редактирование профиля пользователя:  
GET    /api/users/profiles/<id>/  
PUT    /api/users/profiles/<id>/  
PATCH  /api/users/profiles/<id>/  
Доступные данные при просмотре  
Просмотр собственного профиля  
При запросе GET /api/users/profiles/<id>/, где <id> совпадает с id текущего пользователя,   
возвращается полная информация профиля, включая:    
id 
email  
first_name  
last_name  
phone  
city 
avatar  
payments — история платежей пользователя  
Эти данные сериализуются через «полный» сериализатор профиля.  
###### Просмотр чужого профиля
При запросе GET /api/users/profiles/<id>/ для чужого пользователя возвращается только общая,   
публичная информация:  
id  
email  
first_name  
city  
avatar  
При этом не включаются:    
фамилия (last_name)  
телефон (phone)  
история платежей (payments)  
любые чувствительные поля (пароль и т.п.)  
Эти данные сериализуются через отдельный публичный сериализатор.  
###### Редактирование профиля
PUT /api/users/profiles/<id>/  
PATCH /api/users/profiles/<id>/  
Разрешено только владельцу профиля (когда <id> совпадает с request.user.id).  
При попытке изменить чужой профиль возвращается:  
{  
  "detail": "Вы можете редактировать только свой профиль."  
}  

#### Курсы и уроки
##### Курсы (ViewSet)
###### Список курсов
GET /api/lms/courses/
###### Получить курс
GET /api/lms/courses/<id>/  
Ответ включает:  
lessons_count  
lessons: список уроков  
###### Создать курс
POST /api/lms/courses/
###### Обновить курс
PUT/PATCH /api/lms/courses/<id>/
###### Удалить курс
DELETE /api/lms/courses/<id>/
##### Уроки (generic APIView)
###### Список и создание
GET /api/lms/lessons/  
POST /api/lms/lessons/
###### Детальная работа с уроком
GET /api/lms/lessons/<id>/  
PUT/PATCH /api/lms/lessons/<id>/  
DELETE /api/lms/lessons/<id>/  
#### Платежи
Список платежей с фильтрацией  
GET /api/users/payments/

##### Фильтры:
?course=1  
?lesson=2  
?payment_method=cash  
?ordering=paid_at | -paid_at  

##### Детальный платеж  
GET /api/users/payments/<id>/
##### Обновление платежа
PUT/PATCH /api/users/payments/<id>/
##### Удаление платежа
DELETE /api/users/payments/<id>/

### Модели
#### User  с полями:  
email (уникальный)  
phone  
city  
avatar  
username — необязательный

AUTH_USER_MODEL активирован  
#### Course с полями
title  
preview  
description  
связи: lessons (related_name)  

#### Lesson с полями
course (FK)  
title  
description  
preview  
video_link  

#### Payment с полями
user  
paid_at  
course (nullable)  
lesson (nullable)  
amount  
payment_method (choices)  
CheckConstraint: ровно один объект (course или lesson)

### Роли и права доступа

В проекте OnlineLearning реализована ролевая модель доступа,   основанная на механизмах Django групп и на дополнительной логике в DRF permissions.
Определено три роли: Администратор, Модератор, Пользователь.  
Роли назначаются через админ-панель,   никаких специальных API-эндпоинтов для ролей не предусмотрено.

#### Администратор (admin)
Администратор — это пользователь со свойством is_staff=True или is_superuser=True.  
##### Права администратора:  
просмотр всех курсов и уроков;  
создание курсов и уроков;  
редактирование любых курсов и уроков;  
удаление любых курсов и уроков;  
просмотр всех пользователей и платежей;  
полный доступ ко всем API-эндпоинтам;  
доступ к админ-панели Django.  
Администратор обладает максимальными правами.  
#### Модератор (moderator)
Модератор — это пользователь, который состоит в группе moderators.  
Группа создаётся через административную панель Django (admin).  
Пользователь становится модератором после добавления в группу moderators.  
##### Права модератора:
просмотр любых курсов и уроков;  
редактирование любых курсов и уроков.  
Ограничения модератора:  
не может создавать курсы и уроки;  
не может удалять курсы и уроки;  
не имеет доступа к административной панели (если не является staff).  
Модератор управляет содержимым, но не структурой данных.
#### Пользователь (user)
Пользователь — это любой авторизованный пользователь, который не является модератором или администратором.  
##### Права пользователя:  
просмотр своих курсов и уроков;  
редактирование своих курсов и уроков;  
удаление своих курсов и уроков;  
создание курсов и уроков (если разрешено логикой проекта);  
просмотр истории собственных платежей;  
редактирование собственного профиля.  
##### Ограничения пользователя:  
не видит чужие курсы и уроки;  
не может редактировать или удалять объекты других пользователей;  
не имеет доступа к административной панели.  
Пользователь работает только со своими данными.  
##### Механизм определения прав доступа  
Проверка роли пользователя выполняется на основе:    
Администратор  
user.is_staff или user.is_superuser  
Модератор  
user.groups.filter(name="moderators").exists()  
Пользователь  
все остальные авторизованные пользователи  
##### На уровне проектного кода реализованы следующие permission-классы:
IsModerator — проверка принадлежности к группе moderators;  
IsModeratorOrAdmin — доступ модераторам и администраторам;  
IsOwner — доступ только владельцу объекта.  
Эти правила комбинируются в контроллерах с использованием операторов  
& (И), | (ИЛИ), ~ (НЕ).  
Например:    
permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsOwner]  
Владение объектами  
Для моделей Course и Lesson введено поле владельца:  
owner = models.ForeignKey(settings.AUTH_USER_MODEL, ...)  
Это позволяет:  
привязывать создаваемые объекты к текущему пользователю;  
ограничивать доступ к редактированию и просмотру объектами владельца.  
Привязка происходит автоматически:  
def perform_create(self, serializer):  
    serializer.save(owner=self.request.user)  
Также в get_queryset() контроллеров реализовано ограничение отображаемых данных:  
обычный пользователь видит только свои курсы и уроки;  
модератор видит все;  
администратор видит всё.  
#### Матрица прав

| Действие                 | Пользователь | Модератор | Администратор |  
|--------------------------|--------------|-----------|----------------|  
| Просмотр своих объектов  | ✔            | ✔         | ✔              |  
| Просмотр чужих объектов  | ✘            | ✔         | ✔              |  
| Создание курсов/уроков   | опционально* | ✘         | ✔              |  
| Редактирование своих     | ✔            | ✔         | ✔              |  
| Редактирование чужих     | ✘            | ✔         | ✔              |  
| Удаление своих           | ✔            | ✘         | ✔              |  
| Удаление чужих           | ✘            | ✘         | ✔              |  
| Доступ к админке         | ✘            | ✘         | ✔              |  

* В текущей реализации проекта создавать курсы/уроки может только администратор.

### Админ-панель
Доступно:
Пользователи (с кастомным UserAdmin)  
Курсы и вложенные уроки  
Уроки  
Платежи (с фильтрами по курсу, уроку, пользователю и способу оплаты)  

### Форматирование кода
Проект использует:  
black  
isort  
flake8  
Запуск:  
black .  
isort .  
flake8  

### Deploy & CI/CD (Production)

Этот проект использует GitHub Actions + Docker Compose   для автоматического деплоя на удалённый Linux-сервер по SSH.
Docker управляет контейнерами  
systemd (опционально) — процессом деплоя  
GitHub Actions — сборкой, тестами и доставкой кода  

#### Требования к серверу
Удалённый сервер (Ubuntu 20.04+ рекомендуется):  
Docker ≥ 24  
Docker Compose v2  
SSH-дoступ (по ключу)

Открытые порты:
80 — nginx
443 — (если планируется HTTPS)  

Пользователь с правами sudo

##### Установка Docker и Compose  
sudo apt update  
sudo apt install -y ca-certificates curl gnupg    
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER  
newgrp docker
docker --version  
docker compose version  

#### Структура на сервере

Проект разворачивается в каталоге:  
/opt/onlinelearning

Минимально ожидаемая структура:  

/opt/onlinelearning  
├── docker-compose.prod.yaml  
├── Dockerfile  
├── manage.py  
├── nginx/  
│   └── nginx.conf  
├── deploy/  
│   └── deploy.sh  
├── .env.docker        # ❗ хранится только на сервере  
└── .tmp/              # временные файлы деплоя  

#### Подготовка SSH
1. Создай SSH-ключ (локально)  
ssh-keygen -t ed25519 -C "github-deploy"  

2. Добавь публичный ключ на сервер  
ssh-copy-id user@SERVER_IP

Проверь вход:  
ssh user@SERVER_IP

#### GitHub Secrets

В репозитории GitHub открой:  
Settings → Secrets and variables → Actions → New repository secret  

Добавь следующие секреты:

Имя	Описание  
SSH_HOST--------------	IP или домен сервера  
SSH_PORT--------------	Обычно 22  
SSH_USER--------------	Пользователь на сервере  
SSH_PRIVATE_KEY---	Приватный ключ id_ed25519  

⚠️ Важно: ключ добавляется целиком, включая строки BEGIN/END.

#### Конфигурация окружения (.env.docker)

Файл не хранится в git и создаётся только на сервере:  

nano /opt/onlinelearning/.env.docker  

Пример:

DJANGO_SECRET_KEY=super-secret-key  
DJANGO_DEBUG=False  
DJANGO_ALLOWED_HOSTS=example.com,www.example.com  

POSTGRES_DB=onlinelearning  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_HOST=db  
POSTGRES_PORT=5432  

REDIS_HOST=redis  
REDIS_PORT=6379  
REDIS_DB=0  

TIME_ZONE=Europe/Amsterdam  
LANGUAGE_CODE=en-us  

#### CI/CD Workflow (GitHub Actions)  

##### Workflow делает следующее:
Checkout кода  
Запуск тестов (pytest)  
Архивация только файлов из git  
Копирование архива на сервер по SSH  
Безопасная замена кода в /opt/onlinelearning  
Запуск deploy/deploy.sh  
docker compose up -d  
Триггер workflow  

##### Workflow запускается автоматически:

при push в ветку main (или feature, если указано)  
либо вручную (если добавлен workflow_dispatch)  

#### deploy.sh (что делает)

##### Скрипт deploy/deploy.sh:  

Проверяет окружение  
Пересобирает Docker-образы  
Поднимает инфраструктуру (Postgres, Redis)  
Выполняет миграции  
Запускает:  

Django (Gunicorn)  
Celery  
Celery Beat  
Nginx  

Показывает статус контейнеров  

#### Запуск вручную на сервере:    

cd /opt/onlinelearning  
bash deploy/deploy.sh  

#### Проверка после деплоя
Контейнеры  
docker compose -f docker-compose.prod.yaml --env-file .env.docker ps  

Ожидаемый статус:  
web — Up  
nginx — Up  
db — Healthy  
redis — Healthy  
celery — Up  
celery_beat — Up  

#### Проверка API  
curl http://SERVER_IP/  

Ответ:  
OK  

#### Swagger:  

http://SERVER_IP/api/docs/swagger/  

#### Тесты и Celery в CI

В CI используется режим:  

CELERY_TASK_ALWAYS_EAGER=True  
CELERY_TASK_EAGER_PROPAGATES=True  

Это позволяет:  
запускать тесты без Redis  
выполнять Celery-задачи синхронно  
избежать падений в GitHub Actions  

#### systemd: автозапуск и управление деплоем  

В продакшене systemd управляет деплоем,  
а Docker — контейнерами.  
Это даёт:

автозапуск после перезагрузки сервера  
единый контроль (start / stop / restart / status)  
безопасный деплой через docker compose up -d  

##### systemd unit-файл  

Создай файл на сервере:  
sudo nano /etc/systemd/system/onlinelearning.service  
/etc/systemd/system/onlinelearning.service  
[Unit]  
Description=OnlineLearning Docker Stack  
After=docker.service  
Requires=docker.service  
  
[Service]  
Type=oneshot  
RemainAfterExit=yes  
WorkingDirectory=/opt/onlinelearning  
  
ExecStart=/usr/bin/docker compose \  
  -f docker-compose.prod.yaml \  
  --env-file .env.docker \  
  up -d  
  
ExecStop=/usr/bin/docker compose \  
  -f docker-compose.prod.yaml \  
  --env-file .env.docker \  
  down  
  
TimeoutStartSec=0  
  
[Install]  
WantedBy=multi-user.target  

##### Активация systemd-сервиса  
sudo systemctl daemon-reload  
sudo systemctl enable onlinelearning  
sudo systemctl start onlinelearning  

##### Проверка статуса:  
 
sudo systemctl status onlinelearning  

##### Управление деплоем через systemd  
<u>Действие</u> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<u>Команда </u>    <br>Запуск&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sudo systemctl start onlinelearning  
Остановка	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sudo systemctl stop onlinelearning  
Перезапуск	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sudo systemctl restart onlinelearning  
Статус	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sudo systemctl status onlinelearning  
Логи	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;journalctl -u onlinelearning -f  
##### Как это работает вместе с CI/CD
  
GitHub Actions обновляет код в /opt/onlinelearning  
deploy.sh пересобирает образы и контейнеры  
systemd гарантирует:  
автозапуск после reboot  
стабильный продакшен-процесс  

Важно: systemd не следит за кодом, он управляет состоянием приложения.

#### Важно помнить

❌ .env.docker никогда не коммитится  
❌ секреты не хранятся в репозитории  
✅ git archive гарантирует чистый релиз  
✅ деплой идёт атомарно (через stage-директорию)  
✅ Docker volumes не монтируют несуществующие файлы  