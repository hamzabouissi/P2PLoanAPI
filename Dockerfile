FROM python:3.7-alpine
ADD . /app
WORKDIR /app/
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 apk --update add libxml2-dev libxslt-dev libffi-dev  libgcc openssl-dev curl && \
 apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
RUN adduser --disabled-password --gecos '' myuser
