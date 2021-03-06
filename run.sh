#!/bin/sh

es_id=$(sudo podman container list -aqf ancestor=elastic -f status=running);
sudo podman commit $es_id vitamova/elastic;
sudo podman stop -a;
sudo podman build --format=docker -t djangod django_v;
sudo podman build --format=docker -t nginxd nginx;
sudo podman run -d --network vitamova --ip 10.89.0.2 -p 80:80 nginxd;
sudo podman run -d --network vitamova --ip 10.89.0.3 djangod;
sudo podman run -d -e "discovery.type=single-node" --network vitamova --ip 10.89.0.4 localhost/vitamova/elastic;
