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
Provides: mlsensor = %{Version}

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

# Create udev rules for ipmi access
echo "
KERNEL=="ipmi*", SUBSYSTEM=="ipmi", MODE="20660"
KERNEL=="ipmi*", SUBSYSTEM=="ipmi", GROUP="mlsensor"
" > /etc/udev/rules.d/90-ipmi.rules

udevadm control --reload-rules && systemctl restart systemd-udevd.service && udevadm trigger


%post
systemctl daemon-reload
echo "
The mlsensor configuration should be generated in /etc/mlsensor with this form (generic names to be replaced)
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
2021-01-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config, mlsensor.service, mlsensor.spec,
mlsensor_etc/mlsensor.properties.tmp: update ML jar files (multiple
improvements, query of multiple local servers); update configuration
template and configuration script; add to spec file the udev rule
for mlsensor permission to ipmi device

2021-01-14  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: update spec version

2021-01-14  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensord: remove mlsensord :: no longer needed, service is
systemd based

2021-01-14  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* : remove outside of proper dir jar files

2021-01-13  Costin Grigoras <costing@gmail.com>

* : allow monXrdSpace to publish its own node names

2021-01-13  Costin Grigoras <costing@gmail.com>

* : allow monXrdSpace to report its own node names

2021-01-13  Costin Grigoras <costing@gmail.com>

* : log monXrdSpace configuration

2021-01-13  Costin Grigoras <costing@gmail.com>

* : bug fix, one more try?

2021-01-13  Costin Grigoras <costing@gmail.com>

* : default report node name instead of `localhost` (when only
indicating port numbers)

2021-01-13  Costin Grigoras <costing@gmail.com>

* : fix monXrdSpace command + query several endpoints

2020-12-14  Costin Grigoras <costing@gmail.com>

* : Bump ML modules and ApMon to the same as in JAliEn

2020-11-28  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: spec file:: remove dependency on xrootd-client (for
cases like eos) and just warn if xrdfs not found

2020-11-27  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config: mlsensor_config :: comment out settings that
were changed as defaults in template config

2020-11-27  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* README.md, bin/mlsensor_config, mlsensor.spec,
mlsensor_etc/mlsensor.properties.tmp: update the configuration
script and configuration template

2020-05-14  Costin Grigoras <costing@gmail.com>

* : Merge pull request #1 from costing/master Bump ML modules to add the cpu_usage parameter

2019-03-06  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config: mlsensor_config :: remove permanent from the
ip listing as routable ip can be assigned by dhcp

2019-03-06  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.service: mlsensor.service :: start after network is
enabled

2018-08-21  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config: mlsensor_config : dirname is in /usr/bin/

2018-08-21  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: mlsensor.spec :: so ... we DO NOT need an exit in
the middle of PRE

2018-06-29  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* create_rpm: add create_rpm script

2018-06-29  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config: mlsensor_config rewrite using new facilities
of alimonitor

2018-01-15  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.service: mlsensor.service : AssertPathExists belongs to
Unit

2018-01-13  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: mlsensor.spec : fix dist value for el7

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: mlsensor.spec : requires java-headless

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensord: mlsensord : let the ipv6 test run even if it fails

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensord: mlsensord : use tmp for mlsensor home and prefer ipv4

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensord: mlsensord :: fix wrong check

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: spec file fix

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensord: mlsensord : make proper demonization for sysvinit

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.spec: mlsensor.spec : add daemonize for sysvinit and
fixes

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor_etc/mlsensor.properties.tmp: mlsensor.properties.tmp :
use proper path for monDiskIOStat.configFile

2018-01-12  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.service: mlsensor.service : use /tmp as home

2018-01-10  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor.service, mlsensor.spec, mlsensord: fixes for services

2018-01-08  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config, mlsensor.spec: rebased to master as main dev
branch + improvements

2018-01-08  Adrian Sevcenco <adriansev@users.noreply.github.com>

* README.md: Update README.md

2018-01-08  Adrian Sevcenco <adriansev@users.noreply.github.com>

* README.md: Create README.md

2018-01-08  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* mlsensor_etc/mlsensor.properties.tmp: mlsensor.properties.tmp :
set the output log to /var/log/mlsensor/MLSensor%g.log

2018-01-08  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* create_targz, mlsensor.service, mlsensor.spec, mlsensord: wip not
bad but should be tested

2018-01-07  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* {usr/bin => bin}/mlsensor_config, create_targz,
etc/mlsensor/mlsensor_env, mlsensor.spec, {etc/mlsensor =>
mlsensor_etc}/mlsensor.properties.tmp, etc/rc.d/init.d/mlsensord =>
mlsensord, usr/bin/MLSensor, usr/bin/mlsensord.info: rpm wip

2017-09-19  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* create_targz, etc/mlsensor/mlsensor.properties.tmp,
etc/mlsensor/mlsensor_env, etc/rc.d/init.d/mlsensord,
mlsensor.spec, usr/bin/MLSensor, usr/bin/mlsensor_config,
usr/bin/mlsensord.info: create system structure of files

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/MLSensor, bin/mlsensor_config, deploy_mlsensor: make use of
usr/bin

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensord: create proper sysvinit directory

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* deploy_mlsensor: fix dir in deploy

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* etc/mlsensor.properties.tmp, etc/mlsensor_env: mlsensor dir in etc

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* deploy_mlsensor: deploy_mlsensor :: adapt script to the new
structure

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensord: sysvinit file for root/rpm installed mlsensor

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* bin/mlsensor_config: configuration script for mlsensor settings
file

2017-09-17  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* etc/{mlsensor.properties => mlsensor.properties.tmp}: rename
mlsensor.properties to mlsensor.properties.tmp

2017-03-20  Adrian Sevcenco <adrian.sevcenco@cern.ch>

* initial commit with all MLSensor content
