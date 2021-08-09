FROM python:3.9.3-slim

ARG USER=app
ARG HOST=0.0.0.0
ARG PORT=8010

ENV PYTHONUNBUFFERED 1
ENV HOST=$HOST
ENV PORT=$PORT

RUN useradd -m -U -s /bin/bash $USER && \
    chown -R $USER:$USER /home/$USER/

COPY ./app/ /home/$USER/app/
COPY ./requirements.txt /home/$USER/app/

WORKDIR /home/$USER/app

RUN pip install --no-cache-dir -r requirements.txt

USER $USER

EXPOSE $PORT