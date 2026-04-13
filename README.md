# HiradHub

Образовательная платформа для школ, объединяющая учеников и учителей через структурированные учебные маршруты, цифровую библиотеку и инструменты сообщества.

Создана с использованием Django, HTMX и Tailwind CSS.

---

## Возможности

**Для учеников**

* Прохождение пошаговых учебных roadmap’ов, созданных учителями
* Доступ к библиотеке книг, видео и подкастов, отсортированных по категориям и классам
* Создание заметок, привязанных к шагам roadmap или материалам библиотеки
* Получение очков и повышение уровня (10 уровней: от Newcomer до Hiradcore)
* Участие в рейтинге учеников

**Для учителей**

* Загрузка книг, видеоматериалов и подкастов в библиотеку
* Создание и управление учебными roadmap’ами
* Получение отдельного рейтинга на основе загруженных материалов и активности учеников
* Необходима верификация директором школы для доступа к загрузке

**Для директоров**

* Подтверждение учителей своей школы
* Создание и управление школьными сообществами
* Просмотр заявок от учителей прямо в профиле

**Платформа**

* Переключение тёмной и светлой темы
* Живой поиск по пользователям, постам, заметкам и книгам
* Система сообществ (публичные и приватные)
* Типы постов: обычный пост, вопрос (с принятым ответом), статья
* Лайки, комментарии и избранное через HTMX без перезагрузки страницы

---

## Технологический стек

| Слой           | Технология                                 |
| -------------- | ------------------------------------------ |
| Backend        | Python 3.11, Django 4.x                    |
| Frontend       | Django Templates, Tailwind CSS (CDN), HTMX |
| База данных    | SQLite (разработка), PostgreSQL (продакшн) |
| Аутентификация | Кастомный AbstractUser с ролями            |
| Шрифт          | Sora (Google Fonts)                        |

---

## Структура проекта

```
hirad_hub/          # настройки Django проекта
user/               # CustomUser, TeacherProfile, DirectorProfile, School
library/            # Book, Video, Podcast, Category, Topic
post/               # Post (post/question/article), Comment, Like, Favorite
note/               # Note с привязкой к шагам и ресурсам
roadmap/            # Roadmap, Step, StepResource, UserProgress
gamification/       # сигналы, логика очков и уровней
community/          # Community, CommunityMembership, CommunityPost
main/               # Главная, Dashboard, Leaderboard, Search
```

---

## Локальный запуск

**Требования:** Python 3.10+, pip, virtualenv

### 1. Клонирование репозитория

```bash
git clone https://github.com/forskie/hiradhub.git
cd hiradhub
```

### 2. Создание и активация виртуального окружения

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

Создать файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Если `.env` не используется, временно можно указать `SECRET_KEY` напрямую в `settings.py`.

### 5. Применение миграций

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

Открыть `http://127.0.0.1:8000` в браузере.

### 8. Начальные данные (опционально)

Войти в админ-панель `/admin` и создать:

* `School` — школы
* `Category` — категории библиотеки (например, школьные материалы, национальная литература)
* `Topic` — темы для фильтрации

---

## Роли

| Роль          | Назначение                                                |
| ------------- | --------------------------------------------------------- |
| Ученик        | Самостоятельная регистрация `/register/`                  |
| Учитель       | Регистрация `/register/teacher/`, требуется подтверждение |
| Директор      | Назначается через админ-панель                            |
| Администратор | Django superuser                                          |

---

## Система уровней

У учеников и учителей отдельные системы уровней.

**Ученики** (10 уровней, 0 — 100,000 очков)

Newcomer > Reader > Curious > Connoisseur > Researcher > Analyst > Erudite > Intellectual > Thinker > Hiradcore

**Учителя** (10 уровней, 0 — 100,000 очков)

Novice > Apprentice > Adept > Expert > Master > Sage > Guru > Mentor > Luminary > Hiradmand

Очки начисляются за прохождение roadmap’ов, загрузку материалов, написание заметок и постов, а также за полученные лайки.

---

## Лицензия

Проект создан как работа для академической олимпиады.

---

*HiradHub — разработано @forskie*



======================================================================================
=================================== Eglish============================================
======================================================================================



# HiradHub

An educational platform for schools, connecting students and teachers through structured learning paths, a digital library, and community tools.

Built with Django, HTMX, and Tailwind CSS.

---

## Features

**For Students**
- Follow step-by-step learning roadmaps created by teachers
- Access a library of books, videos, and podcasts organized by category and school grade
- Take notes linked to roadmap steps or library materials
- Earn points and rank up through 10 levels (Newcomer to Hiradcore)
- Compete on a dedicated student leaderboard

**For Teachers**
- Upload books, video lessons, and podcasts to the library
- Create and manage learning roadmaps with structured steps
- Earn a separate teacher rank based on materials uploaded and student engagement
- Require verification from a school director before gaining upload access

**For Directors**
- Verify teachers from their school
- Create and manage school communities
- View pending teacher registrations directly from their profile

**Platform**
- Dark/light theme toggle
- Live search across users, posts, notes, and books
- Community system with public and private groups
- Post types: regular post, question (with accepted answer), article
- HTMX-powered likes, comments, and favorites — no page reloads

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django 4.x |
| Frontend | Django Templates, Tailwind CSS (CDN), HTMX |
| Database | SQLite (development), PostgreSQL (production) |
| Auth | Custom AbstractUser with role-based access |
| Font | Sora (Google Fonts) |

---

## Project Structure

```
hirad_hub/          # Django project settings
user/               # CustomUser, TeacherProfile, DirectorProfile, School
library/            # Book, Video, Podcast, Category, Topic
post/               # Post (post/question/article), Comment, Like, Favorite
note/               # Note with step and resource linking
roadmap/            # Roadmap, Step, StepResource, UserProgress
gamification/       # Signals, score constants, level logic
community/          # Community, CommunityMembership, CommunityPost
main/               # Home, Dashboard, Leaderboard, Search
```

---

## Local Setup

**Requirements:** Python 3.10+, pip, virtualenv

### 1. Clone the repository

```bash
git clone https://github.com/forskie/hiradhub.git
cd hiradhub
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

If you don't have a `.env` setup, you can temporarily set `SECRET_KEY` directly in `settings.py` for local development.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

### 8. Set up initial data (optional)

Log in to the admin panel at `/admin` and create:
- `School` entries for your schools
- `Category` entries for the library (e.g. School Materials, National Literature)
- `Topic` entries for filtering

---

## Roles

| Role | How to assign |
|---|---|
| Student | Self-registration at `/register/` |
| Teacher | Self-registration at `/register/teacher/` — requires director/admin verification |
| Director | Assigned manually via admin panel |
| Admin | Django superuser |

---

## Rank System

Students and teachers have separate rank systems.

**Students** (10 levels, 0 — 100,000 pts)

Newcomer > Reader > Curious > Connoisseur > Researcher > Analyst > Erudite > Intellectual > Thinker > Hiradcore

**Teachers** (10 levels, 0 — 100,000 pts)

Novice > Apprentice > Adept > Expert > Master > Sage > Guru > Mentor > Luminary > Hiradmand

Points are earned by completing roadmap steps, uploading materials, writing notes and posts, and receiving likes.

---

## License

This project was created as an academic competition (olympiad) entry.

---

*HiradHub — built by [@forskie](https://github.com/forskie)*
