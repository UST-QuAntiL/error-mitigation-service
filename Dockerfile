FROM python:3.8-slim

MAINTAINER Martin Beisel "martin.beisel@iaas.uni-stuttgart.de"

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt-get update
RUN apt-get install -y gcc python3-dev
RUN pip install -r requirements.txt
COPY . /app

ENTRYPOINT [ "python" ]

CMD ["app.py" ]