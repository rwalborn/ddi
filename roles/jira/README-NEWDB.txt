create postgres aurora cluster

connect to cluster and create users like so

psql -h atlassian-aurora.cogj9jonzgb4.us-east-1-beta.rds.amazonaws.com -U DBA -W -d DBD
create user jira with password 'REDACTED' CREATEDB;
create user confluence with password 'REDACTED' CREATEDB;
\q

reconnect as jira user and create db
psql -h atlassian-aurora.cogj9jonzgb4.us-east-1-beta.rds.amazonaws.com -U jira -W -d DBD
CREATE DATABASE jira WITH ENCODING 'UNICODE' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;
\q



reconnect as confluence user
psql -h atlassian-aurora.cogj9jonzgb4.us-east-1-beta.rds.amazonaws.com -U confluence -W -d DBD
CREATE DATABASE confluence WITH ENCODING 'UNICODE' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;
\q


adjust server.xml for elb config
<Connector port="8080"

                   maxThreads="150"
                   minSpareThreads="25"
                   connectionTimeout="20000"

                   enableLookups="false"
                   maxHttpHeaderSize="8192"
                   protocol="HTTP/1.1"
                   useBodyEncodingForURI="true"
                   acceptCount="100"
                   scheme="https"
                   proxyName="jira.ddc.io"
                   proxyPort="443"
                   disableUploadTimeout="true"/>
