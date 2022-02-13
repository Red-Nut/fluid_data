Installation Instructions

clone project with:
    git clone https://github.com/barrenger/fluid_data.git

Create virtual environment in project folder:
    apt install python3.8-venv
    cd fluid_data
    python3 -m venv venv

Install requirements for mysql
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

Activate the virtual environment:
    source venv/bin/activate

Install project requirements:
    pip install -r requirements.txt

If you get "failed building wheel for grpcio" then upgrade pip and retry:
    pip install --upgrade pip
    pip install -r requirements.txt

Create .env file in the settings folder (fluid_data/data_extraction/settings) and define the following variables
    EMAIL_HOST=
    EMAIL_HOST_USER=
    EMAIL_HOST_PASSWORD=

    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    AWS_BUCKET=

    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_HOST=
    DB_PORT=

    SECRET_KEY=

Perform a database migration:
    python manage.py makemigrations data_extraction
    python manage.py migrate

Collect Static
    python manage.py collectstatic

If useing AWS, create temp folder in the main project folder
    mkdir temp

Install redis server
    sudo apt install redis-server

Test to project with:
    python manage.py runserver 0.0.0.0:8000 --settings=data_extraction.settings.dev
