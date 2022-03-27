FROM python:3.10-slim as base_stage

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock
RUN pipenv install

COPY . ./

EXPOSE 8000

COPY start-local.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]