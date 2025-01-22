FROM python:3.12-alpine3.18

ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN set -ex \
    && apk add --no-cache --virtual .build-deps curl postgresql-dev build-base libffi libffi-dev build-base python3-dev py-pip jpeg-dev zlib-dev rsync \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt

ADD . /app

RUN rm -rf /app/setup/ui/
RUN rm -rf /app/.venv

ENV VIRTUAL_ENV=/env
ENV PATH=/env/bin:$PATH

EXPOSE 9418

CMD ["sh", "entrypoint.sh"]