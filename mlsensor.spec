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

Requires: java-headless >= 1.6.0
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

getent group %{GROUP} >/dev/null || groupadd -r %{GROUP}
getent passwd %{USER} >/dev/null || \
    useradd -r -g %{GROUP} -d %{HOMEDIR} -s /sbin/nologin \
    -c "MLSensor agent account" %{USER}

/bin/mkdir /var/log/%{USER}
/bin/chown %{USER}:%{GROUP} /var/log/%{USER}

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
* Fri Jan 12 2018 adrian <adrian.sevcenco@cern.ch> - MLSensor rpm
- Initial build.
