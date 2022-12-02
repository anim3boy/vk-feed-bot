FROM python:3.9-alpine3.17 

WORKDIR /usr/src/app 
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/sh", "start.sh"]

