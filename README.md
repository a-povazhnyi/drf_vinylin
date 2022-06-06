# **VINYLIN** — online vinyl store

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/a-povazhnyi/django_vinylin.git
$ cd drf_vinylin
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
```

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies 
create and fill your `.env` file using `.env.example`:
```sh
(venv)$ nano .env
```

Then apply you need to make and apply migrations:
```sh
(venv)$ cd vinylin
(venv)$ python manage.py makemigrations
(venv)$ python manage.py migrate
```

Once migrations have applied, you can start the server:
```sh
(venv)$ python manage.py runserver
```

Use swagger URL to navigate and test the API:
***http://127.0.0.1:8000/swagger/***