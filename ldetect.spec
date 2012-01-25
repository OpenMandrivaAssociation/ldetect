# EDIT IN SVN NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).

%define lib_major 0.12
%define lib_minor 1
%define lib_name %mklibname %{name} %{lib_major}
%define develname %mklibname %name -d

%define build_diet 1

Name:    ldetect
Version: %{lib_major}.%{lib_minor}
Release: 1
Summary: Light hardware detection tool
Source: %{name}-%{version}.tar.xz
Group: System/Kernel and hardware
URL:	  http://www.mandrivalinux.com
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: usbutils => 0.11-2mdk pciutils-devel => 3.0.0-4mdv zlib-devel
BuildRequires: modprobe-devel
%if %{build_diet}
BuildRequires: dietlibc-devel
%endif
Conflicts: drakxtools < 9.2-0.32mdk
License: GPL

%package -n %{lib_name}
Summary: Light hardware detection library
Requires: ldetect-lst common-licenses
Requires: pciids
# (tv) fix upgrade ordering (libpci3 needs to be updaded from 3.0 to 3.1 before ldetect is upgraded):
# (tv) and require a lib w/o double free:
Requires: %{mklibname pci 3} >= 3.1.4-3mdv2010.0
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
The hardware device lists provided by this package are used as a lookup 
table to get hardware auto-detection.

%description -n %develname
see %name

%description -n %{lib_name}
see %name

%prep
%setup -q

%build
%if %{build_diet}
%make CFLAGS="-Os -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64" CC="diet gcc" libldetect.a
cp libldetect.a libldetect-diet.a
make clean
%endif
%make

%install
rm -rf %{buildroot}
%makeinstall
%if %{build_diet}
install -d %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}
install libldetect-diet.a %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

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
%_libdir/*.a
%if %{build_diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif
%_libdir/*.so


