FROM python:3.9.5
WORKDIR /home/chp/chp-backend

COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=config.settings
ARG SECRET_KEY
# a secret key just for development build
ENV SECRET_KEY="anunsecuresecrectkey"

ARG IS_BUILD=TRUE

COPY . .
COPY .env .env

RUN python manage.py collectstatic --noinput

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
