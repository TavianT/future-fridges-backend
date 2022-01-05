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

## Create users

To create regular users once the server is up and running go to http://localhost:8000/admin from there log in with the super user created above. Then click on add user as seen on the image below:

![img](https://i.imgur.com/ztI5XvA.png) 

## Test data

To add the test data to the database the database file will need to be create see above migrate command, then run `sqlite3 db.sqlite3 < sqlite_test_scripts/SQL_FILE`

The scripts provided should be ran in this order for the best result:

- create_suppliers

- create_items

- create_fridge_contents
