FROM python:3.5.2-alpine

COPY ./ /opt/local/src/VestaService/

RUN pip install /opt/local/src/VestaService/

USER 1000

CMD cp /opt/local/src/VestaService/celeryconfig.py /tmp

CMD celery worker -A VestaService.stub -l info -b amqp://guest@amqp/
