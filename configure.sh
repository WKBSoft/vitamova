SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )";
cp $SCRIPTPATH"/website_server.service" "/etc/systemd/system/website_server.service";
systemctl daemon-reload;
systemctl enable website_server;
systemctl start website_server;