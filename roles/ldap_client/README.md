Role: ldap\_client
====
**Description:**
Installs sssd and configures server for LDAP authentication.

**Dependencies:**

* Sudoers will not work unless there are files defined in /etc/sudoers.d/.  The sudoers_users role or ops role handles this.
* Tested on CentOS6 and CentOS 7.

**Usage:**
Add as a role to your playbook, requires you to define one variable called `ldapvpc`, the only correct entries for this are one of the following: "tools" "prod" "dev" "lt" "stg". Heres a commandline example:  `--extra-vars="ldapvc=prod"`.
