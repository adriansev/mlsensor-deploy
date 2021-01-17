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

BuildRequires: systemd

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

/bin/mkdir -p /var/log/%{USER}
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

mkdir -p %{buildroot}/%{_unitdir}/
cp mlsensor.service %{buildroot}/%{_unitdir}/

/bin/find $RPM_BUILD_ROOT \( -type f -o -type l \) -print | sed "s#^$RPM_BUILD_ROOT/*#/#" > RPM-FILE-LIST

%clean
rm -rf %{buildroot}

%files -f RPM-FILE-LIST
%defattr(-,root,root)
%config %{_sysconfdir}/%{name}/*

%changelog
