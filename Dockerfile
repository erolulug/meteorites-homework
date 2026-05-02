FROM alpine:3.21

RUN apk add --no-cache bash jq

WORKDIR /app
COPY . /app

RUN chmod +x /app/bin/meteorites

ENTRYPOINT ["/app/bin/meteorites"]

