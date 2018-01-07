%if %{?fedora}%{!?fedora:0} >= 21 || %{?rhel}%{!?rhel:0} >= 7
%global use_systemd 1
%else
%global use_systemd 0
%endif

Summary:	MLSensor
Name:		mlsensor
Version:	1.0
Release:	1%{?dist}
License:	none
Group:		System Environment/Daemons

Source0: 	%{name}-%{version}.tar.gz
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: java >= 1.6.0

%description
MLSensor agent for sending monitoring data to MonaLisa service

%prep
%setup -q

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{_javadir}
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}
mkdir -p %{buildroot}/%{_initddir}

cp mlsensor_etc/*  %{buildroot}/%{_sysconfdir}/%{name}/
cp mlsensor_jars/* %{buildroot}/%{_javadir}/%{name}/
cp bin/*           %{buildroot}/%{_bindir}/


# For Sysv
cp mlsensord %{buildroot}/%{_initddir}/

# For systemd
## sed -e "s/__DESCRIPTION__/%{name}/" -e "s|__JAR__|%{_datadir}/%{name}/%{name}.jar|" -e "s|__USER__|%{name}|" -e "s|__CONFIGFILE__|%{_sysconfdir}/%{name}/application.properties|" < systemd/myservice.service.template > systemd/%{name}.service
## cp systemd/%{name}.service %{buildroot}/usr/lib/systemd/system/%{name}.service

%clean
rm -rf %{buildroot}


%files -f RPM-FILE-LIST
%defattr(-,root,root)
%config %{_sysconfdir}/%{name}/mlsensor_env
%config %{_sysconfdir}/%{name}/mlsensor.properties.tmp
%{_javadir}/%{name}/*.jar



%changelog
* Sun Sep 17 2017 adrian <adrian.sevcenco@cern.ch> - MLSensor
- Initial build.
