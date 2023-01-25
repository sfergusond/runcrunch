FROM python:3.10.6-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt /app/requirements.txt
RUN apk add g++
RUN apk --no-cache --update-cache add gfortran libopenblas-base libatlas3-base python-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

EXPOSE 8080

# replace APP_NAME with module name
CMD ["gunicorn", "--bind", ":8080", "runcrunch.wsgi"]