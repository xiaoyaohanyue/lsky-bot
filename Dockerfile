FROM python:3.12-alpine AS Builder

WORKDIR /app
COPY . .

RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        libffi-dev \
        libmagic \
        bash \
        && pip install --upgrade pip \
        && pip install --no-cache-dir -r requirements.txt \
        && pyinstaller --onefile main.py

FROM alpine

WORKDIR /app

COPY --from=Builder /app/dist/main /app/main
COPY --from=Builder /app/conf/.env.example /app/conf/.env

RUN apk add --no-cache libmagic

CMD ["./main"]



