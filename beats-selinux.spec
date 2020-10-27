# vim: sw=4:ts=4:/et

%global with_selinux 1
%global selinuxtype targeted


Name:               beats-selinux
Version:            1.0
Release:            7%{?dist}
Summary:            SELinux policy module for various beats

Group:              System Environment/Base     
License:            GPLv2+  
URL:                https://git.im.jku.at/summary/packages!beats-selinux.git
Source0:            beats.te
Source1:            beats.if
Source2:            filebeat.te
Source3:            filebeat.fc
Source4:            filebeat.if
Source5:            auditbeat.te
Source6:            auditbeat.fc
Source7:            auditbeat.if
Source8:            journalbeat.te
Source9:            journalbeat.fc
Source10:           journalbeat.if
Source11:           metricbeat.te
Source12:           metricbeat.fc
Source13:           metricbeat.if

BuildRequires:      selinux-policy-devel >= 3.13
BuildConflicts:     selinux-policy-devel < 3.13
BuildRequires:      policycoreutils-devel
Requires:           policycoreutils
Requires:           selinux-policy-%{selinuxtype}
Requires:           libselinux-utils
Requires:           selinux-policy >= 3.13
Conflicts:          selinux-policy < 3.13
Requires(post):     policycoreutils
Requires(post):     selinux-policy-%{selinuxtype}
Requires(postun):   policycoreutils
BuildArch:          noarch
%{?selinux_requires}

%if 0%{?with_selinux}
# This ensures that the *-selinux package and all it’s dependencies are not pulled
# into containers and other systems that do not use SELinux
Requires:        (%{name} if selinux-policy-%{selinuxtype})
%endif



%description
This package installs and sets up the SELinux policy security module for beats.

%prep
%setup -c -n %{name} -T
cp %{SOURCE0} %{SOURCE1} %{SOURCE2} %{SOURCE3} \
   %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} \
   %{SOURCE8} %{SOURCE9} %{SOURCE10} %{SOURCE11} \
   %{SOURCE12} %{SOURCE13} \
 .

%build
make -f /usr/share/selinux/devel/Makefile beats.pp || exit
make -f /usr/share/selinux/devel/Makefile filebeat.pp || exit
make -f /usr/share/selinux/devel/Makefile journalbeat.pp || exit
make -f /usr/share/selinux/devel/Makefile auditbeat.pp || exit
make -f /usr/share/selinux/devel/Makefile metricbeat.pp || exit

%install

%if 0%{?with_selinux}

install -d %{buildroot}%{_datadir}/selinux/packages
install -m 644 beats.pp %{buildroot}%{_datadir}/selinux/packages
install -m 644 filebeat.pp %{buildroot}%{_datadir}/selinux/packages
install -m 644 journalbeat.pp %{buildroot}%{_datadir}/selinux/packages
install -m 644 auditbeat.pp %{buildroot}%{_datadir}/selinux/packages
install -m 644 metricbeat.pp %{buildroot}%{_datadir}/selinux/packages
install -d %{buildroot}%{_datadir}/selinux/devel/include/contrib
install -m 644 filebeat.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -m 644 journalbeat.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -m 644 auditbeat.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -m 644 beats.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -m 644 metricbeat.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/
install -d %{buildroot}/etc/selinux/targeted/contexts/users/
%endif

%if 0%{?with_selinux}

%pre 
%selinux_relabel_pre -s %{selinuxtype}

%post
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/beats.pp
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/filebeat.pp
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/journalbeat.pp
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/auditbeat.pp
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/metricbeat.pp

if /usr/sbin/selinuxenabled ; then
	if [ $1 -eq 1 ]; then
	    semanage port -p tcp -t logstash_port_t -a 5044
	    semanage port -p tcp -t kafka_port_t -a 9092
	fi;
    semanage port -p tcp -t elasticsearch_port_t -m 9200
fi;

exit 0
 
%postun
if [ $1 -eq 0 ]; then
	if /usr/sbin/selinuxenabled ; then
	    semanage port -p tcp -t logstash_port_t -d 5044
	    semanage port -p tcp -t kafka_port_t -d 9092
	    semanage port -p tcp -t elasticsearch_port_t -d 9200

	    %selinux_modules_uninstall -s %{selinuxtype} filebeat
	    %selinux_modules_uninstall -s %{selinuxtype} journalbeat
	    %selinux_modules_uninstall -s %{selinuxtype} auditbeat
	    %selinux_modules_uninstall -s %{selinuxtype} metricbeat
	    %selinux_modules_uninstall -s %{selinuxtype} beats
    fi;
fi;
exit 0

%posttrans
%selinux_relabel_post -s %{selinuxtype}
# if with_selinux
%endif
%files
%defattr(-,root,root,-)
%{_datadir}/selinux/packages/beats.pp
%{_datadir}/selinux/packages/filebeat.pp
%{_datadir}/selinux/packages/journalbeat.pp
%{_datadir}/selinux/packages/auditbeat.pp
%{_datadir}/selinux/packages/metricbeat.pp
%{_datadir}/selinux/devel/include/contrib/beats.if
%{_datadir}/selinux/devel/include/contrib/filebeat.if
%{_datadir}/selinux/devel/include/contrib/journalbeat.if
%{_datadir}/selinux/devel/include/contrib/auditbeat.if
%{_datadir}/selinux/devel/include/contrib/metricbeat.if

%changelog
* Tue Oct 27 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-7
- add new metricbeat.te : add init_status workaround
- add new requires to the spec file, ensures that the *-selinux package 
- and all it’s dependencies are not pulled
- into containers and other systems that do not use SELinux
- (based on https://fedoraproject.org/wiki/SELinux/IndependentPolicy)

* Tue Oct 27 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-6
- add new metricbeat.te 
* Tue Oct 27 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-5
- add dontaudit sys_ptrace everywhere
- drop permissive
* Tue Oct 21 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-4
- fix on port add
* Tue Oct 20 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-3
- minor spec fixes based on https://fedoraproject.org/wiki/SELinux/IndipendentPolicy
- minor spec fixes based on https://fedoraproject.org/wiki/SELinux/IndipendentPolicy
* Wed Jul  1 2020 Elia Pinto <pinto.elia@gmail.com> - 1.0-2
- Added metricbeat policy
- Fixed filebeat policy on CentOS 8
* Wed Jan 17 2018 fuero <fuerob@gmail.com> - 1.0-1
- Initial version
