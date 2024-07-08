FROM docker.elastic.co/elasticsearch/elasticsearch:7.11.0

ENV AWS_ACCESS_KEY_ID $aws_access_id
ENV AWS_SECRET_ACCESS_KEY $aws_secret_key

RUN bin/elasticsearch-plugin install --batch repository-s3
RUN /usr/share/elasticsearch/bin/elasticsearch-keystore create

RUN echo $AWS_ACCESS_KEY_ID | /usr/share/elasticsearch/bin/elasticsearch-keystore add --stdin s3.client.default.access_key
RUN echo $AWS_SECRET_ACCESS_KEY | /usr/share/elasticsearch/bin/elasticsearch-keystore add --stdin s3.client.default.secret_key

