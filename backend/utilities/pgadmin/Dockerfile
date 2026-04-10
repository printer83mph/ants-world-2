FROM dpage/pgadmin4

USER root

COPY docker.servers.json /pgadmin4/servers.json
RUN chmod -R 755 /pgadmin4

USER pgadmin
