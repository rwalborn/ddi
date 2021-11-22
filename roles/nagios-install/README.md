nagios-install
--
This role installs nagios and it's dependencies from yum and pip packages.
By default if nagios.sslselfsigned is true, which is the default, a self signed SSL certificate and key will be placed in /etc/httpd/ssl.  The key and cert paths can be changed with variables.  This does no actual configuration of nagios or apache, and does not enable them.  The nagios-conf role is used to configure apache and nagios after running this role.
