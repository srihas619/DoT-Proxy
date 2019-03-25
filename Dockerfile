FROM python:3.7-alpine
MAINTAINER Prathisrihas srihas619@gmail.com

RUN pip install pyyaml
WORKDIR /app
COPY dot_proxy.py .
EXPOSE 53/tcp

ENTRYPOINT ["python","-u","dot_proxy.py"]