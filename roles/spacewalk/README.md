### What this role does ### 
This role has 3 modes of operation

* master
* client
* proxy

### variables ###
variables are set in defaults/main.yml
* you may disable node registration by setting 
  * ```registerme: false```
* you may disable installation of oscap scanning tools by setting 
  * ```oscap: false```
* baking will set ```registerme: false``` to keep in line with conventions 
  * ```baking:true```
    * if using in asg you will need 
      * hg/git pull of ddi repo
      * ```/root/bin/sysconfig```
* you may enable master mode by setting
  * ```master:true```
* you may enable proxy mode by setting
  * ```proxy:true```
* client is on by default
  * ```client:true```
* you can install packages during baking by specifying them via
  * ```packages:true```
  and 
  ```
      baking_packages:
         - centos6-x86_64-scl
    ```

### baking ###
When baking you can install packages from the spacewalk repo by including 
```packages:true```

When packages is set to true any packages listed in ```baking_packages``` will be installed
As a final step of baking the systemid of the registration to spacewalk will be removed.
When the machine comes up in launch config running the normal sysconfig script will register spacewalk again.

HOWEVER:  Any special channels will need to be re-added as they will not have persisted to the new registration.
Channels can be added to the node using 

```"spacewalk-channel -a -c centos6-x86_64-scl -u {{ spacewalk_admin_user }} -p {{ spacewalk_admin_pw }}"```

OR by going to the spacewalk admin console and enabling the channel for the machine there.


### master mode ###
Master mode builds the spacewalk master node that serves repository and configuraions.

spacewalk_host variable is set in group_vars to determine fqdn
to use in master mode include with

```
vars_files:
  - ../group_vars/environmentcode
roles:
  - { role: spacewalk, master: true }
```

### proxy mode ###
Proxy builds a spacewalkproxy that brokers connections to the spacewalk master
There is a spacewalkproxy in each VPC

spacewalk_host variable is set in group_vars to determine fqdn
to build a spacewalkproxy

```
vars_files:
  - ../group_vars/environmentcode
roles:
  - { role: spacewalk, proxy: true }
```

### client mode ###
Connects machine to their local spacewalk proxy or spacewalk master directly
registers machine and connects to default child channels
puts node in group based on activation key
( ie:  1-centos7-x86_64-qa )

```
vars_files:
  - ../group_vars/environmentcode
roles:
  - spacewalk
```