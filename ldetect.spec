# EDIT IN SVN NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).

%define lib_major 0.7
%define lib_minor 3
%define lib_name %mklibname %{name} %{lib_major}
%define develname %mklibname %name -d

Name:    ldetect
Version: %{lib_major}.%{lib_minor}
Release: %mkrel 1
Summary: Light hardware detection tool
Source: %{name}-%{version}.tar.bz2
Group: System/Kernel and hardware
URL:	  http://www.mandrivalinux.com
BuildRoot: %_tmppath/%{name}-buildroot
BuildRequires: usbutils => 0.11-2mdk pciutils-devel zlib-devel modprobe-devel
Conflicts: drakxtools < 9.2-0.32mdk
License: GPL

%package -n %{lib_name}
Summary: Light hardware detection library
Requires: ldetect-lst common-licenses
Requires: pciids
Group: System/Libraries

%package -n %develname
Summary: Development package for ldetect
Requires: %{lib_name} = %{version}
Provides: ldetect-devel = %version, libldetect-devel = %version
Obsoletes: ldetect-devel
Group: Development/C
Conflicts: %{mklibname ldetect 0.6}-devel
Obsoletes: %mklibname %name 0.7 -d

%description
The hardware device lists provided by this package are used as lookup 
table to get hardware autodetection

%description -n %develname
see %name

%description -n %{lib_name}
see %name

%prep
%setup -q

%build
%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %{lib_name} -p /sbin/ldconfig

%postun -n %{lib_name} -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc AUTHORS
%_bindir/*

%files -n %{lib_name}
%defattr(-,root,root)
%_libdir/*.so.*

%files -n %develname
%defattr(-,root,root)
%doc ChangeLog
%_includedir/*
%_libdir/*.so


