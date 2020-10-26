# TOP: Refugee Sprint REPO (Georgetown Team, Fall 2020)

This repo contains the code for an app built to help facilitate connecting refugees entering the United States with various non-profit resources. The app is intended to leverage open source solutions to the issue of database construction and management around cataloging, and making publicly available, a list of non-profits offering various services to aid refugees. The database used here is OpenStreetMaps and the app relies heavily on various OSM Python Wrappers.

### Programs needed to run:

Python3

Familiarity with the Terminal


To run the app locally, download all files from this repository into a local directory and then follow the directions for your operating system.

## Mac: 
*(Drawn largely from the following resources: http://blog.sahildiwan.com/posts/flask-and-postgresql-app-deployed-on-heroku/ and https://www.codementor.io/@engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb)*

1. If you do not have homebrew, open a Terminal and run the following:

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

2. In Terminal, run the following to download PostgreSQL (There will be quite a lot of output, but you can disregard. For the third line, you may need to use 'sudo psql postgres' depending on your system configuration):

brew install postgresql

brew services start postgresql

3. Setup a user with database creation permissions (pay attention to inserts for username and password designations):

psql postgres

CREATE ROLE insert_desired_user_name WITH LOGIN PASSWORD 'insert_password';

postgres=# ALTER ROLE patrick CREATEDB; 

postgres=# \q

4. Time to create the database. From Terminal run (using user_name we just created):

psql postgres -U insert_created_user_name

CREATE DATABASE top_app;

\q

5. Change directories in the Terminal to the outer most 'top_app' folder and run the following:

. venv/bin/activate

cd top_app/

python3

6. With Python running, run the following:

from __init__ import db

db.create_all()

quit()

7. And now the table for registering Users is created within the Database! Open the file called '__init__.py' within the top_app folder and change the line that reads: 

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///top_app"

to 

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/top_app"

8. From the Terminal, change directories to outer most folder labeled 'top_app' and run the following:

. launch_ap.sh

9. A line should appear the local address (e.g. it will say 'Running on http://127.0.0.1:5000/'). Copy and paste the address into an incognito browser to view and test the app.




## For Ubuntu 20.04

1. Download PostgreSQL using the command line instructions found here: https://www.postgresql.org/download/linux/ubuntu/

2. Open Terminal and run the following:

sudo -i -u postgres

createdb top_app

3. From the terminal, change directories into the top_app directory, activate the virtual environment, and start Python3:

cd top_app/

. venv/bin/activate

cd top_app/

Python3

4. From within Python3, run the following:

from __init__ import db

db.create_all()

quit()

5. And now the table for registering Users is created within the Database! In the Terminal, change directories back to the outer most folder labeled 'top_app' and run the following command to launch the app:

. launch_app.sh

6. A line should appear the local address (e.g. it will say 'Running on http://127.0.0.1:5000/'). Copy and paste the address into an incognito browser to view and test the app.



### Other useful links:
https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart