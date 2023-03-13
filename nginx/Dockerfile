FROM nginx:latest
 

RUN rm  /etc/nginx/conf.d/default.conf


COPY ./django.conf /etc/nginx/conf.d/default.conf
COPY ./ssl/* /etc/ssl/
COPY ./pki-validation/* /etc/pki-validation/

EXPOSE 443
