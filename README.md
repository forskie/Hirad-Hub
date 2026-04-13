## HiradHub

Образовательная платформа для школ, построенная вокруг структурированных учебных маршрутов (roadmaps), цифровой библиотеки и геймификации прогресса.

Цель системы — сделать обучение измеримым, направленным и визуально прогрессирующим.

---

## Технологический стек

| Слой           | Технология                                 |
| -------------- | ------------------------------------------ |
| Backend        | Python 3.11, Django 4.x                    |
| Frontend       | Django Templates, Tailwind CSS (CDN), HTMX |
| База данных    | SQLite (dev), PostgreSQL (prod)            |
| Аутентификация | Custom `AbstractUser` с ролями             |
| Шрифт          | Sora (Google Fonts)                        |

---

## Возможности платформы

### Ученики

* Прохождение пошаговых roadmap’ов, созданных учителями
* Доступ к библиотеке (книги, видео, подкасты) с категоризацией
* Заметки, привязанные к шагам и материалам
* Система уровней и очков (10 уровней от Newcomer до Hiradcore)
* Рейтинги и лидерборды

### Учителя

* Создание и управление roadmap’ами
* Загрузка материалов в библиотеку
* Аналитика активности учеников
* Верификация через директора школы

### Директора

* Управление школьными сообществами
* Подтверждение учителей
* Просмотр заявок и структуры школы

### Общая функциональность

* Посты (обычные / вопросы / статьи)
* Лайки, комментарии, избранное (HTMX без перезагрузки)
* Поиск по всей системе
* Темная / светлая тема
* Публичные и приватные сообщества

---

## Архитектура проекта

```
hirad_hub/   # core settings
user/        # users, roles, school, profiles
library/     # books, videos, podcasts, categories, topics
post/        # posts, questions, articles, favorites
note/        # notes tied to roadmap steps/resources
roadmap/     # roadmaps, steps, progress tracking
gamification/# XP, levels, signals
community/   # communities and memberships
main/        # dashboard, search, leaderboard
```

---

## Локальный запуск

### Требования

* Python 3.10+
* pip
* virtualenv

### 1. Клонирование

```bash
git clone https://github.com/forskie/hirad-hub.git
cd hiradhub
```

### 2. Виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Миграции

```bash
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 6. Запуск

```bash
python manage.py runserver
```

Открыть: `http://127.0.0.1:8000`

---

## Роли системы

| Роль          | Описание                                 |
| ------------- | ---------------------------------------- |
| Ученик        | Основной пользователь обучения           |
| Учитель       | Создает контент и roadmap’ы              |
| Директор      | Управляет школой и подтверждает учителей |
| Администратор | Полный доступ (Django superuser)         |

---

## Система прогресса

### Ученик

10 уровней, 0–100 000 XP:

Newcomer → Reader → Curious → Connoisseur → Researcher → Analyst → Erudite → Intellectual → Thinker → Hiradcore

### Учитель

Novice → Apprentice → Adept → Expert → Master → Sage → Guru → Mentor → Luminary → Hiradmand

### Источники XP

* прохождение roadmap’ов
* публикация заметок
* загрузка материалов
* активность и лайки

---

## Проблема, которую решает система

Современное обучение часто страдает от отсутствия:

* видимого прогресса
* структурированного пути обучения
* обратной связи по результату

Это приводит к:

* потере мотивации
* прокрастинации
* фрагментированному обучению

HiradHub решает это через:

* roadmap-структуру обучения
* визуализацию прогресса
* систему наград и уровней
* централизованную библиотеку знаний

---

## Лицензия

Проект создан как работа для академической олимпиады.

---

## HiradHub

Разработано @forskie
