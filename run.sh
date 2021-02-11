sudo podman stop -a;
sudo podman build --format=docker -t djangod django_v;
sudo podman build --format=docker -t nginxd nginx;
sudo podman run -d --network cni-podman1 --ip 10.89.0.2 -p 80:80 nginxd;
sudo podman run -d --network cni-podman1 --ip 10.89.0.3 djangod;
