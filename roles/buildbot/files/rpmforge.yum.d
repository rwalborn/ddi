### Name: RPMforge RPM Repository for RHEL 6 - dag
### URL: http://rpmforge.net/
[rpmforge]
name = RHEL $releasever - RPMforge.net - dag
baseurl = http://apt.sw.be/redhat/el6/en/$basearch/rpmforge
mirrorlist = http://apt.sw.be/redhat/el6/en/mirrors-rpmforge
#mirrorlist = file:///etc/yum.repos.d/mirrors-rpmforge
enabled = 1
protect = 0
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag
gpgcheck = 0

[rpmforge-extras]
name = RHEL $releasever - RPMforge.net - extras
baseurl = http://apt.sw.be/redhat/el6/en/$basearch/extras
mirrorlist = http://apt.sw.be/redhat/el6/en/mirrors-rpmforge-extras
#mirrorlist = file:///etc/yum.repos.d/mirrors-rpmforge-extras
enabled = 1
protect = 0
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag
gpgcheck = 0

[rpmforge-testing]
name = RHEL $releasever - RPMforge.net - testing
baseurl = http://apt.sw.be/redhat/el6/en/$basearch/testing
mirrorlist = http://apt.sw.be/redhat/el6/en/mirrors-rpmforge-testing
#mirrorlist = file:///etc/yum.repos.d/mirrors-rpmforge-testing
enabled = 0
protect = 0
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag
gpgcheck = 0
