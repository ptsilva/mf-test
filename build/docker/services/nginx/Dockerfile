FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./build/docker/services/nginx/nginx.conf /etc/nginx/conf.d
