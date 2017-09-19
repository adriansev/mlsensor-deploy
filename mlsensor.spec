%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

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

%build

%install

%clean

%files -f RPM-FILE-LIST
%defattr(-,root,root)
%config %{_sysconfdir}/%{name}/mlsensor_env
%config %{_sysconfdir}/%{name}/mlsensor.properties.tmp
%{_javadir}/%{name}/*.jar



%changelog
* Sun Sep 17 2017 adrian <adrian.sevcenco@cern.ch> - MLSensor
- Initial build.
