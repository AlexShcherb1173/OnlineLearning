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

### Лицензия
Свободное использование в образовательных целях.
