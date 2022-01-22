FROM python:3.8.12-alpine3.15
COPY . /app
WORKDIR /app
RUN apk add --no-cache libc-dev
RUN pip install -U pip
RUN pip install -r requirements.txt -i https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
CMD ["python", "server.py"]