FROM docker.n8n.io/n8nio/n8n:latest

USER root

RUN ls /

RUN cat /etc/os-release