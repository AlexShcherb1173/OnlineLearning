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

## 🚀 Запуск проекта через Docker Compose

Для удобного запуска всех частей проекта используется **docker-compose**.  
Это позволяет поднять backend, базу данных, Redis и Celery одной командой без ручного управления контейнерами.

---
### Требования
- Установлен Docker Desktop
- Включён движок **Linux containers** (Docker Desktop обычно сам)
- В корне проекта лежат файлы:
  - `Dockerfile`
  - `docker-compose.yaml`
  - `.env` 
  - `requirements.txt`
### 📦 Используемые сервисы

В `docker-compose.yaml` описаны следующие сервисы:

- **backend** — Django REST API
- **db** — PostgreSQL
- **redis** — брокер сообщений для Celery
- **celery** — Celery worker
- **celery_beat** — Celery Beat (планировщик задач)

Все сервисы используют переменные окружения из файла `.env`.

---

### 📄 Переменные окружения

В корне проекта должен находиться файл `.env`.

Шаблон файла — `.env.sample`:

```env
# === Django ===
DJANGO_SECRET_KEY=CHANGE_ME
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# === I18N ===
LANGUAGE_CODE=ru
TIME_ZONE=Europe/Amsterdam

# === PostgreSQL ===
POSTGRES_DB=OnlineLearning_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# === SMTP ===
SMTP_BACKEND=django.core.mail.backends.smtp.EmailBackend
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=CHANGE_ME
SMTP_PASSWORD=CHANGE_ME

DJANGO_DEFAULT_ADMIN_EMAIL=superadmin@example.com
DJANGO_DEFAULT_ADMIN_PASSWORD=CHANGE_ME

# === Stripe ===
STRIPE_SECRET_KEY=sk_test_CHANGE_ME
STRIPE_PUBLISHABLE_KEY=pk_test_CHANGE_ME
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/payments/success/
STRIPE_CANCEL_URL=http://127.0.0.1:8000/payments/cancel/

# === Redis ===
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```
⚠️ Важно:

файл .env не должен попадать в репозиторий  
в Docker-хосты POSTGRES_HOST и REDIS_HOST автоматически переопределяются на db и redis  

### ▶️ Запуск проекта  
Скопировать шаблон окружения:

cp .env.sample .env
Заполнить файл .env актуальными значениями

#### Запустить проект:

docker compose up --build
После запуска сервисы будут доступны:

Backend (Django):
👉 http://127.0.0.1:8000/

Swagger / OpenAPI (если включён):
👉 http://127.0.0.1:8000/api/schema/swagger-ui/

#### ⏹ Остановка проекта

docker compose down
#### ♻️ Полный перезапуск с очисткой данных
Удаляет контейнеры и том с базой данных:

docker compose down -v
docker compose up --build
#### 🔍 Проверка работоспособности сервисов
Django backend

docker compose logs -f backend
PostgreSQL

docker compose logs -f db
Redis

docker compose exec redis redis-cli ping  
#### Ожидаемый ответ:  

nginx  

PONG  
Celery worker  

docker compose logs -f celery  
Celery Beat  

docker compose logs -f celery_beat  
#### ✅ Результат
После запуска одной командой:

Django API доступен

PostgreSQL подключён

Redis работает

Celery обрабатывает фоновые задачи

Celery Beat запускает периодические задачи

Проект полностью готов к локальной разработке и тестированию.

### Лицензия
Свободное использование в образовательных целях.
