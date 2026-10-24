# Band website

Django application for the IBM Skills Network Back-End Development Capstone. It shows songs and photos from the two microservices, supports account sign-in, and lets signed-in users RSVP to concerts.

## Local development

Install `requirements.txt`, then run `python manage.py migrate` and `python manage.py runserver`. The site opens at `http://127.0.0.1:8000/`.

By default, it reads pictures from `http://127.0.0.1:8080/picture` and songs from `http://127.0.0.1:8081/song`. Override the base addresses using `PICTURES_SERVICE_URL` and `SONGS_SERVICE_URL`.

The container runs migrations at startup and serves Django on port 8000. Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and the service URLs when deploying. Create an admin account with `python manage.py createsuperuser` in a trusted environment.

Before running `kubectl apply -f deployment.yml` in a cloud cluster, replace `djangoserver:latest` with the image pushed to your registry and set the two service URLs to your deployed Pictures and Songs addresses. The manifest's host wildcard is intended for the course lab; use specific hosts outside that environment.
