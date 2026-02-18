#!/bin/bash
python manage.py migrate
gunicorn vcs_project.wsgi --log-file -
