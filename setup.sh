sudo dnf install git;
sudo dnf install podman;
git clone https://github.com/WKBSoft/vitamova.git;
sudo podman run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.11.0;
es_id=$(sudo podman container list -aqf ancestor=elasticsearch -f status=running);
sudo podman commit $es_id vitamova/elastic;
sudo podman stop $es_id;
sudo podman network create vitamova --subnet 10.89.0.0/24;
echo "Give the name of the S3 bucket you will use for this project";
read s3_bucket;
echo "Provide your AWS credentials. First write your access key ID";
read aws_access_id;
echo "Provide your AWS secret access key";
read aws_access_key;