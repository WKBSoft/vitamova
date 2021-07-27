#!/bin/sh

sudo podman stop -a;
sudo podman build --format=docker -t djangod django_v;
sudo podman build --format=docker -t nginxd nginx;
sudo podman build --format=docker -t databased database;
sudo podman build --format=docker -t snapshotd snapshot;
sudo podman run -d --network vitamova --ip 10.89.0.2 -p 80:80 nginxd;
sudo podman run -d --network vitamova --ip 10.89.0.3 djangod;
sudo podman run -d -e "discovery.type=single-node" --network vitamova --ip 10.89.0.4 databased;
sudo podman run -d --network vitamova --ip 10.89.0.5 snapshotd;
