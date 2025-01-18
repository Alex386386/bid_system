FROM python:3.10-alpine

RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /

COPY requirements.txt ./

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]