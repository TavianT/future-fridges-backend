# future-fridges-backend

## How to run

### Prerequites

Python version 3.8 is needed to run this without any issues (3.9 might work but It hasn't been tested)

### Installation

#### (Optional) set up venv

`python3 -m venv env`

#### Install dependancies

`pip install django`

`pip install djangorestframework`

#### Start server

`python manage.py migrate`

`python manage.py createsuperuser` (Input email, name and password)

`python manage.py runserver`
