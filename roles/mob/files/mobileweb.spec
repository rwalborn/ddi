Name:           mobileweb
Version:        %{version}
Release:        1
Summary:        Mobile Web
License:        DDI
BuildArch:      x86_64
Source0:        none

%description
Mobile Web based on %{branch} branch at changeset %{changeset}


%post
test -x /bin/systemctl && systemctl stop httpd || service httpd stop
test -x /bin/systemctl && systemctl start httpd || service httpd start


%clean
rm -rf %{buildroot}


%files
%defattr(0644,root,root,0755)
/home/webapps/casino/current
/etc/httpd/conf.d
