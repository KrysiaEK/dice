FROM python:3.8.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock
RUN pipenv install

COPY . ./

EXPOSE 8000

CMD [ "python", "./manage.py runserver 0.0.0.0:8000" ]

