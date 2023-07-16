# News Article application

## Setup

The first thing to do is to clone the repository:

```sh
$ https://github.com/rohitmaxxx/news_article.git
$ cd sample-django-app
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv news_venv
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment.

Once `pip` has finished downloading the dependencies:
Add the .env file in news_article and add below variables:

- EMAIL_HOST_USER=''
- EMAIL_HOST_PASSWORD=''
- DEFAULT_FROM_EMAIL=''
- NEWS_API_KEY=''
- KEYWORD_THRESHOLD=900

KEYWORD_THRESHOLD is to prevent user to search same keyword multiple times

Run the following command
```sh
(env)$ cd news_article
(env)$ python manage.py makemigrations
(env)$ python manage.py migrate
(env)$ python manage.py collectstatic
(env)$ python manage.py createsuperuser
(env)$ python manage.py runserver
```

## Walkthrough
Navigate to `http://127.0.0.1:8000/news_article/`.
Now login with superuser credentials. It will got to the admin page becasue of admin creds.
Add a user from admin panel and login on http://127.0.0.1:8000/news_article/ to search news.