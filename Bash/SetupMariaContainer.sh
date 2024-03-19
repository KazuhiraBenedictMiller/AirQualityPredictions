#!/bin/bash

# Print current directory
echo "Current directory: $(pwd) and Current .env file path: $(realpath ./.env)"

# Load variables from .env file
if [ -f ./.env ]; then
    source ./.env
fi

sudo docker exec -i mariadb mariadb -u $MARIADB_ROOTUSER -p$MARIADB_ROOTPASSWORD <<EOF
CREATE USER '$MARIADB_USER'@'%' IDENTIFIED BY '$MARIADB_PASSWORD';
GRANT ALL PRIVILEGES ON *.* TO '$MARIADB_USER'@'%' IDENTIFIED BY '$MARIADB_PASSWORD' WITH GRANT OPTION;
CREATE DATABASE $MARIADB_DBNAME;
FLUSH PRIVILEGES;
exit
EOF