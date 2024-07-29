# Vitamova

### About

This is a [Django](https://github.com/django/django) Web Application for intermediate to advanced language learners. The application can be accessed [here](https://www.vitamova.com/).

## Compatability

This application has been tested and run in Ubuntu 24.04 LTS.

## Sections

The application has 3 parts: scrapers, vitalib, and vitamova.

### scrapers

Scrapers are scripts run daily to produce content for the application. These are run as cron jobs.

### vitalib

Vitalib is a [Python](https://www.python.org/) library with functions used regularly in the app to access resources such as AWS, ChatGPT, and the PostgreSQL database.

### vitamova

This is the actual Django application.