# First
Quotes of African origin, especially Afropop artists. Provide verified contributed annotations.

# Distinctiveness

This app is crowd sourced quotes from afropop music, annotation to those quotes and suggestions to improve related annotation from users who are culture lovers. 
An unauthenticated user is able to view quotes, and their charts, an authenticated user is able to submit a quote: title of the material, the author, the quote and a link to author image from the web. A user can also annotate an unannotated quote, which can be reviewed and approved. 
While an authenticated user has a profile with earned points (more on that in complexity) and upvote/like an annotation, this is frankly the only similarity to other projects.



# Complexity

The apps complexity comes from the fact that it:

1- keeps tracks of numbers

The app is gamified in a way as users earn points (Annotation IQ) when they, write verified annotation, reveiw others annotation.
The app also charts the quotes and their ensuring annotation ordering by the number of views each quote had earned. 

2- community administration

After a new annotation is submitted it is shown on every authenticated users review dashboard, list where they are asked if they can review or pass. 
An annotation needs 2 reviewers apart from the author to be verified and therefor published.

3- connects to an external api

In the in app charts sections, quotes also have a link to listen to the song it was excerpted over on youtube. Using the youtube data api, the app can search on youtube and bring the closest match to the song. 

4- In app search

users can also search through quotes database using keywords.

# Files

/migrations - DB migration files
/static - javascript, css files 
/templates - html template files
/apps.py - app config
/models.py - Model Object definitions
/views.py - views classes and methods
/urls.py - url pattern definition fro app afroquotes
/youtube_charts.py - youtube web api helper functions
/manage.py - entry point 
/wsgi.py - WSGI config for the project
/settings.py - Django settings for quotes project


# How to run

- Pull the repo and cd into the repo
- download docker for desktop if you dont already have and start docker
- Run docker-compose up -d --build
This will create 2 docker containers: db and app
the server is now running
- Migrations 
- Run docker-compose exec app python manage.py migrate
this will run migrations
To confirm go to localhost:8000
You can now create a user account
To create cms superuser administrator account
- Run docker-compose exec app python manage.py createsuperuser
and follow the prompts.
Now you can go to localhost:8000/admin to login as admin user.
