FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
#RUN mv /usr/share/nginx/html /usr/share/nginx/downloads
#RUN rm /usr/share/nginx/downloads/*
COPY ./target/nginx/download.conf /etc/nginx/conf.d/
COPY ./target/contrib/start_nginx.sh /usr/local/bin/
RUN /bin/chmod u+x /usr/local/bin/start_nginx.sh
RUN /bin/chown nginx:nginx /usr/local/bin/start_nginx.sh
EXPOSE 80
CMD ["/bin/sh", "-c", "start_nginx.sh"]