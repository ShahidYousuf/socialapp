# socialapp
A mini social app for making and organising friends

# Features

• API to search other users by email and name(paginate up to 10 records per page).
  
  a) If search keyword matches exact email then return user associated with the email.
  
  b) If the search keyword contains any part of the name then return a list of all users. eg:- Amarendra, Amar, aman, Abhirama are three users and if users search with "am" then all of these users should be shown in the search result because "am" substring is part of all of these names.
  
  c) There will be only one search keyword that will search either by name or email.

• API to send/accept/reject friend request

• API to list friends(list of users who have accepted friend request)

• List pending friend requests(received friend request)

• Users can not send more than 3 friend requests within a minute.

# Tech Stack

- Python, Django, Django Rest Framework, MySQL

# How to run the application

#### 1. Install the required Python Virtual Environment

```bash
virtualenv env_socialapp -p python3.11
```

#### 2. Activate the environment

```bash
source env_socialapp/bin/activate
```

#### 3. Clone the repo, and move to the socialapp folder of the repo code.

```bash
git clone git@github.com:ShahidYousuf/socialapp.git
cd socialapp
```

#### 4. Make sure you have MySQL version 5.7 installed, assuming you have it, create a database for the project, for example.

```mysql
CREATE DATABASE social_db;
```

#### 5. Create an .env file for accessing the project secrets with the following content.

```bash
touch .env
```
Make sure to populate the values for `DB_NAME`, `DB_USER` and `DB_PASSWORD` respectively for project MySQL database name, database user and database password.

#### 6. Install the project requirements, making sure you are in the project top level folder (folder containing `manage.py` script)

```bash
pip install -r requirements.txt
```
This will install all the requirements, if you face any issues during installation, please make sure you have all the dev libs install for python and mysql.

#### 7. Migrate the project DB migrations, which will create the db schema and tables.

```bash
python manage.py migrate
```

#### 8. If migrations have run successfully, you can run the app using from the development server like this

```bash
python manage.py runserver
```
This will create a development server for the app at http://localhost:8000 by default, if you have anything running on this port, make sure the use another port or stop the process running at 8000
#### 9. Go to your browser http://localhost:8000/api and browse the apis, you will be greeted with a page like below.

![Sample API Home page](https://github.com/ShahidYousuf/socialapp/blob/master/app_home.png)


#### Thanks you, for any queries, please reach out at shahidyousuf77@gmail.com



