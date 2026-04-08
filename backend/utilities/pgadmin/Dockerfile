FROM dpage/pgadmin4

USER root

RUN mkdir -p /pgadmin4 && \
    cat > /pgadmin4/servers.json << 'EOF'
{
  "Servers": {
    "1": {
      "Name": "AntsWorld",
      "Group": "Servers",
      "Host": "db",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "antsworld",
      "Password": "password",
      "SSLMode": "prefer",
      "DBRestrictionList": []
    }
  }
}
EOF

RUN chmod -R 755 /pgadmin4

USER pgadmin
