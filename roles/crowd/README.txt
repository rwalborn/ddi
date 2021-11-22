create postgres aurora cluster

connect to cluster and create users like so

psql -h db-atlassian-tools.cmgtqqi0jns8.us-east-1.rds.amazonaws.com -U DBA -W -d atlassian
create user crowd with password 'REDACTED' CREATEDB;

\q

reconnect as crowd user and create db
psql -h db-atlassian-tools.cmgtqqi0jns8.us-east-1.rds.amazonaws.com -U crowd -W -d atlassian
CREATE DATABASE crowd WITH ENCODING 'UNICODE' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;
\q


adjust crowd/apache-tomcat/conf/server.xml for elb config

        <Connector acceptCount="100"
                   connectionTimeout="20000"
                   disableUploadTimeout="true"
                   enableLookups="false"
                   maxHttpHeaderSize="8192"
                   maxThreads="150"
                   minSpareThreads="25"
                   port="8095"
                   redirectPort="8443"
scheme="https" proxyName="testcrowd.doubledowninteractive.com" proxyPort="443"
                   useBodyEncodingForURI="true"
                   URIEncoding="UTF-8"
                   compression="on"
                   compressableMimeType="text/html,text/xml,application/xml,text/plain,text/css,application/json,application/javascript,application/x-javascript" />


make sure /mnt/atlassian/crowd-home/crowd.properties  has localhost for crowd.server.url and application.login.url


session.tokenkey=session.tokenkey
crowd.server.url=http\://localhost\:8095/crowd/services/
application.name=crowd
http.timeout=30000
session.isauthenticated=session.isauthenticated
application.login.url=http\://localhost\:8095/crowd
session.validationinterval=0
