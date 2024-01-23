#################################################################
####################### BUILD STAGE #############################
#################################################################
FROM snakepacker/python:all as builder

ARG MODE=prod

RUN python3.11 -m venv /usr/share/python3/app

# Setup python env
COPY ./requirements/ /etc/requirements/

RUN apt-get update && apt-get install -yq build-essential && \
    apt-get clean && apt-get autoclean && \
    rm -rf /var/cache/* && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/share/python3/app/bin/pip install -U pip setuptools wheel && \
    /usr/share/python3/app/bin/pip install --no-cache-dir -r /etc/requirements/$MODE.txt

RUN find-libdeps /usr/share/python3/app > /usr/share/python3/app/pkgdeps.txt

#################################################################
####################### TARGET STAGE ############################
#################################################################
FROM snakepacker/python:3.11

ARG USER=app
ARG HOST=0.0.0.0
ARG PORT=8010

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST=$HOST
ENV PORT=$PORT

COPY --from=builder /usr/share/python3/app /usr/share/python3/app

RUN cat /usr/share/python3/app/pkgdeps.txt | xargs apt-install

COPY ./app/ /home/$USER/app/

# Setup app env
RUN useradd -U -s /bin/bash $USER && \
    chown -R $USER:$USER /home/$USER/

WORKDIR /home/$USER/app

USER $USER

EXPOSE $PORT