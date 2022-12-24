[Unit]
Description=MY DB (PG) docker container
Requires=docker.service
After=docker.service
[Service]
Restart=always
ExecStart=/usr/bin/docker start -a my-db
ExecStop=/usr/bin/docker stop -t 2 my-db
TimeoutSec=30
[Install]
WantedBy=multi-user.target