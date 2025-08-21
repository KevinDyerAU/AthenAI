#!/bin/sh
# Export environment variables passed in (Neo4j and alert configs are expected)
printenv | sed 's/=.*/="&"/' >/etc/environment

# Start cron in foreground and tail log
cron && tail -f /var/log/cron.log
