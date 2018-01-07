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

BuildArch:  noarch

Requires: java >= 1.6.0

%if %{use_systemd} == 1
BuildRequires: systemd
%endif

%description
MLSensor agent for sending monitoring data to MonaLisa service

%prep
%setup -q

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

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%config %{_sysconfdir}/%{name}/*
%{_javadir}/%{name}/*
%{_bindir}/*

%if %{use_systemd} == 1
%{_unitdir}/*
%ghost %{_initddir}/*
%else
%{_initddir}/*
%ghost %{_unitdir}/*
%endif

%changelog
* Sun Sep 17 2017 adrian <adrian.sevcenco@cern.ch> - MLSensor
- Initial build.
