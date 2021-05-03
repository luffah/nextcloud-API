ARG NEXTCLOUD_VERSION

FROM nextcloud:$NEXTCLOUD_VERSION-apache

ARG GROUPFOLDERS_VERSION
ADD https://github.com/nextcloud/groupfolders/releases/download/v${GROUPFOLDERS_VERSION}/groupfolders-$GROUPFOLDERS_VERSION.tar.gz /tmp/

RUN true \
	&& tar xf /tmp/groupfolders-$GROUPFOLDERS_VERSION.tar.gz -C /tmp/ \
	&& true
