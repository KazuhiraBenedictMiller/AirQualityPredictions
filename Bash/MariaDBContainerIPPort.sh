#!/bin/bash

# Print current directory
echo "Current directory: $(pwd) and Current .env file path: $(realpath ./.env)"

# Retrieve container IP address using Docker inspect command
container_ip=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mariadb)
container_port=$(sudo docker port mariadb | awk -F: '{print $2}')

# Check if .env file exists
if [[ -f ./.env ]]; then
    # Check if IP address already set in .env file
    if ! grep -q '^MARIADB_CONTAINERIP=' ./.env; then
        echo "MARIADB_CONTAINERIP=$container_ip" >> ./.env
        echo "Added MARIADB_CONTAINERIP=$container_ip to .env file"
    else
        echo "MARIADB_CONTAINERIP already exists in .env file, skipping"
    fi
        
    # Check if port already set in .env file
    if ! grep -q '^MARIADB_CONTAINERPORT=' ./.env; then
        echo "MARIADB_CONTAINERPORT=$container_port" >> ./.env
        echo "Added MARIADB_CONTAINERPORT=$container_port to .env file"
    else
        echo "MARIADB_CONTAINERPORT already exists in .env file, skipping"
    fi
else
    echo "No .env file found, skipping"
fi


