%if %{?fedora}%{!?fedora:0} >= 21 || %{?rhel}%{!?rhel:0} >= 7
%global use_systemd 1
%else
%global use_systemd 0
%endif

Summary:    MLSensor
Name:       mlsensor
Version:    1.2.6
Release:    1%{?dist}
License:    none
Group:      System Environment/Daemons

Source0:    %{name}-%{version}.tar.gz
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:  noarch
Provides: mlsensor = %{version}-%{release}

Requires(pre): shadow-utils

Requires: java-headless >= 1.8.0
Requires: curl
Requires: bind-utils

%if %{use_systemd} == 1
BuildRequires: systemd
%endif

%if %{use_systemd} == 0
Requires: daemonize
%endif

%define USER mlsensor
%define GROUP mlsensor
%define HOMEDIR /home/%{USER}

%description
MLSensor agent for sending monitoring data to MonaLisa service

%pre

xrdfs_present=$(command -v xrdfs)
if [ -z "$xrdfs_present" ]; then
    echo -e "!!! xrdfs command was not found in path!\nxrootd-client packages should be installed or the command should be specified by path in mlsensor configuration"
fi

# add user for the service
getent group %{GROUP} >/dev/null || groupadd -r %{GROUP}
getent passwd %{USER} >/dev/null || \
    useradd -r -g %{GROUP} -d %{HOMEDIR} -s /sbin/nologin \
    -c "MLSensor agent account" %{USER}

/bin/mkdir /var/log/%{USER}
/bin/chown %{USER}:%{GROUP} /var/log/%{USER}

# Create udev rules for ipmi access IF ipmitool is found
command -v ipmitool &> /dev/null && {
echo "
KERNEL=="ipmi*", SUBSYSTEM=="ipmi", MODE="20660"
KERNEL=="ipmi*", SUBSYSTEM=="ipmi", GROUP="mlsensor"
" > /etc/udev/rules.d/90-ipmi.rules
udevadm control --reload-rules && systemctl restart systemd-udevd.service && udevadm trigger
}

%post
systemctl daemon-reload
echo "
The mlsensor configuration should be generated in /etc/mlsensor with this command form (generic names to be replaced)
mlsensor-config template_file_name ALICE::SE_NAME::SE_TYPE
systemctl enable mlsensor.service
systemctl start mlsensor.service

"

%prep
%setup -q

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{_sysconfdir}/%{name}
cp mlsensor_etc/*  %{buildroot}/%{_sysconfdir}/%{name}/

mkdir -p %{buildroot}/%{_javadir}/%{name}/
cp mlsensor_jars/* %{buildroot}/%{_javadir}/%{name}/

mkdir -p %{buildroot}/%{_bindir}/
cp bin/* %{buildroot}/%{_bindir}/

%if %{use_systemd} == 1
mkdir -p %{buildroot}/%{_unitdir}/
cp mlsensor.service %{buildroot}/%{_unitdir}/
%else
mkdir -p %{buildroot}/%{_initddir}
cp mlsensord %{buildroot}/%{_initddir}/
%endif

/bin/find $RPM_BUILD_ROOT \( -type f -o -type l \) -print | sed "s#^$RPM_BUILD_ROOT/*#/#" > RPM-FILE-LIST

%clean
rm -rf %{buildroot}

%files -f RPM-FILE-LIST
%defattr(-,root,root)
%config %{_sysconfdir}/%{name}/*

%changelog
* Sun Jan 17 2021 Adrian Sevcenco
- conditionaly add udev ipmi permission on presence of ipmitool

* Sun Jan 17 2021 Adrian Sevcenco
- fix mlsensor.service, add changelog to rpm spec

* Sun Jan 17 2021 Adrian Sevcenco
- update ML jar files (multiple improvements, query of multiple local servers);
- update configuration template and configuration script;
- add to spec file the udev rule for mlsensor permission to ipmi device

* Thu Jan 14 2021 Adrian Sevcenco
- update spec version

* Thu Jan 14 2021 Adrian Sevcenco
- remove mlsensord :: no longer needed, service is systemd based

* Thu Jan 14 2021 Adrian Sevcenco
- remove outside of proper dir jar files

* Wed Jan 13 2021 Costin Grigoras
- allow monXrdSpace to publish its own node names

* Wed Jan 13 2021 Costin Grigoras
- allow monXrdSpace to report its own node names

* Wed Jan 13 2021 Costin Grigoras
- log monXrdSpace configuration

* Wed Jan 13 2021 Costin Grigoras
- bug fix, one more try?

* Wed Jan 13 2021 Costin Grigoras
- default report node name instead of `localhost` (when only indicating port numbers)

* Wed Jan 13 2021 Costin Grigoras
- fix monXrdSpace command + query several endpoints

* Mon Dec 14 2020 Costin Grigoras
- Bump ML modules and ApMon to the same as in JAliEn

* Sat Nov 28 2020 Adrian Sevcenco
- spec file:: remove dependency on xrootd-client (for cases like eos) and just warn if xrdfs not found

* Fri Nov 27 2020 Adrian Sevcenco
- mlsensor_config :: comment out settings that were changed as defaults in template config

* Fri Nov 27 2020 Adrian Sevcenco
- update the configuration script and configuration template

* Thu May 14 2020 Costin Grigoras
- Merge pull request #1 from costing/master

* Wed May 13 2020 Costin Grigoras
- Bump ML modules to add the cpu_usage parameter

* Wed Mar 06 2019 Adrian Sevcenco
- mlsensor_config :: remove permanent from the ip listing as routable ip can be assigned by dhcp

* Wed Mar 06 2019 Adrian Sevcenco
- mlsensor.service :: start after network is enabled

* Tue Aug 21 2018 Adrian Sevcenco
- mlsensor_config : dirname is in /usr/bin/

* Tue Aug 21 2018 Adrian Sevcenco
- mlsensor.spec :: so ... we DO NOT need an exit in the middle of PRE

* Fri Jun 29 2018 Adrian Sevcenco
- add create_rpm script

* Fri Jun 29 2018 Adrian Sevcenco
- mlsensor_config rewrite using new facilities of alimonitor

* Mon Jan 15 2018 Adrian Sevcenco
- mlsensor.service : AssertPathExists belongs to Unit

* Sat Jan 13 2018 Adrian Sevcenco
- mlsensor.spec : fix dist value for el7

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.spec : requires java-headless

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : let the ipv6 test run even if it fails

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : use tmp for mlsensor home and prefer ipv4

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord :: fix wrong check

* Fri Jan 12 2018 Adrian Sevcenco
- spec file fix

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : make proper demonization for sysvinit

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.spec : add daemonize for sysvinit and fixes

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.properties.tmp : use proper path for monDiskIOStat.configFile

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.service : use /tmp as home

* Wed Jan 10 2018 Adrian Sevcenco
- fixes for services

* Tue Aug 21 2018 Adrian Sevcenco
- mlsensor_config : dirname is in /usr/bin/

* Tue Aug 21 2018 Adrian Sevcenco
- mlsensor.spec :: so ... we DO NOT need an exit in the middle of PRE

* Fri Jun 29 2018 Adrian Sevcenco
- add create_rpm script

* Fri Jun 29 2018 Adrian Sevcenco
- mlsensor_config rewrite using new facilities of alimonitor

* Mon Jan 15 2018 Adrian Sevcenco
- mlsensor.service : AssertPathExists belongs to Unit

* Sat Jan 13 2018 Adrian Sevcenco
- mlsensor.spec : fix dist value for el7

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.spec : requires java-headless

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : let the ipv6 test run even if it fails

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : use tmp for mlsensor home and prefer ipv4

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord :: fix wrong check

* Fri Jan 12 2018 Adrian Sevcenco
- spec file fix

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensord : make proper demonization for sysvinit

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.spec : add daemonize for sysvinit and fixes

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.properties.tmp : use proper path for monDiskIOStat.configFile

* Fri Jan 12 2018 Adrian Sevcenco
- mlsensor.service : use /tmp as home

* Wed Jan 10 2018 Adrian Sevcenco
- fixes for services
