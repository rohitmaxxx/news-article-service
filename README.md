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
(env)$ pip install -r requirement.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment.

Once `pip` has finished downloading the dependencies:
Add the .env file in news_article and add below variables. NEWS_API_KEY value is mandatory:

- EMAIL_HOST_USER=''
- EMAIL_HOST_PASSWORD=''
- DEFAULT_FROM_EMAIL=''
- NEWS_API_KEY=''
- KEYWORD_THRESHOLD=900

KEYWORD_THRESHOLD is to prevent user to search same keyword multiple times and email setup to send password to user when adding.

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


### Development Time

The breakdown of time spent on project is as follows:

- Requirement analysis: [2 days]
- UI development: [3 day]
- Development and implementation: [10 days]
- Testing and bug fixing: [3 days]
- Documentation and finalization: [2 days]

### Overall Experience

Working on this project has been a fulfilling and rewarding experience. The project provided an opportunity to apply and enhance our skills in Django development.
I was facing some following challanges:
- How to get latest news article by date becasue if already have some article for that date then articles again will come same.
- Manage filters was very difficult becasue in given apis all filter data was not include in response data so it was hard handler at local
