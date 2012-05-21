# EDIT IN SVN NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).
%define Werror_cflags %nil

%define	major	0.12
%define	minor	1
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_with	diet
%bcond_without	uclibc

Name:		ldetect
Version:	%{major}.%{minor}
Release:	2
Summary:	Light hardware detection tool
Group:		System/Kernel and hardware
License:	GPLv2+
URL:		http://www.mandrivalinux.com
Source0:	%{name}-%{version}.tar.xz
Patch0:		ldetect-0.12.1_modalias_kmod.patch
Patch1:		ldetect-0.12.1-pci.patch
BuildRequires:	usbutils
BuildRequires:	pkgconfig(libkmod)
BuildRequires:	pkgconfig(libpci)
BuildRequires:	pkgconfig(zlib)
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif

%description
The hardware device lists provided by this package are used as a lookup 
table to get hardware auto-detection.

%package -n	%{libname}
Summary:	Light hardware detection library
Group:		System/Libraries
Requires:	ldetect-lst
Requires:	common-licenses
Requires:	pciids
# (tv) fix upgrade ordering (libpci3 needs to be updaded from 3.0 to 3.1 before ldetect is upgraded):
# (tv) and require a lib w/o double free:
Conflicts:	%{mklibname pci 3} < 3.1.4-3mdv2010.0

%description -n %{libname}
see %{name}

%package -n	%{devname}
Group:		Development/C
Summary:	Development package for ldetect
Requires:	%{libname} = %{EVRD}
Provides:	ldetect-devel = %{EVRD}

%description -n %{devname}
see %{name}

%prep
%setup -q
%apply_patches

%build
%if %{with diet}
%make CFLAGS="-Os -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64" CC="diet gcc" libldetect.a
cp libldetect.a libldetect-diet.a
make clean
%endif

%if %{with uclibc}
%make CFLAGS="%{uclibc_cflags}" LDFLAGS="%{?ldflags}" CC="%{uclibc_cc}"
cp libldetect.a libldetect-uclibc.a
make clean
%endif

%make

%install
%makeinstall
%if %{with diet}
install libldetect-diet.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif
%if %{with uclibc}
install libldetect-uclibc.a -D %{buildroot}%{uclibc_root}%{_libdir}/libldetect.a
%endif

%files
%doc AUTHORS
%{_bindir}/*

%files -n %{libname}
%{_libdir}/*.so.%{major}
%{_libdir}/*.so.%{major}.%{minor}

%files -n %{devname}
%doc ChangeLog
%{_includedir}/*
%{_libdir}/*.a
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libldetect.a
%endif
%{_libdir}/*.so
