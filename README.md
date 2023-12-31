# future-fridges-backend

## How to run

### Prerequisites

Python version 3.8 is needed to run this without any issues (3.9 might work but It hasn't been tested)

### Installation

#### (Optional) set up venv

`python3 -m venv env`

#### Install dependancies

`pip install -r requirements.txt`

#### Start server

`python manage.py migrate`

`python manage.py createsuperuser` (Input email, name and password)

`python manage.py runserver`

### Create users

To create regular users once the server is up and running go to http://localhost:8000/admin from there log in with the super user created above. Then click on add user as seen on the image below:

![img](https://i.imgur.com/ztI5XvA.png) 

### Test data

**At least 2 regular users need to be created from admin site for this to work without error**

To add the test data to the database the database file will need to be create see above migrate command, then run `sqlite3 db.sqlite3 < sqlite_test_scripts/SQL_FILE`

The scripts provided should be ran in this order for the best result:

- create_suppliers

- create_items

- create_fridge_contents

## Azure instructions

The azure endpoint is `https://future-fridges.azurewebsites.net` for example to go to the admin page the the web address would be `https://future-fridges.azurewebsites.net/admin`

the log in for the admin page is:

email address: `admin@admin.com`
password: `admin`

The log in for the users is:

Head Chef:

email: `testchef@gmail.com`

Chef:

email: `yaboi@yeahman.com`

Delivery Driver:

email: `toko@yami.com`

password (for all users): `akashiseijuro`