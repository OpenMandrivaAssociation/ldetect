# EDIT IN SVN NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).
%define	major	0.12
%define	minor	4
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	diet
%bcond_without	uclibc

Name:		ldetect
Version:	%{major}.%{minor}
Release:	1
Summary:	Light hardware detection tool
Group:		System/Kernel and hardware
License:	GPLv2+
URL:		http://www.mandrivalinux.com
Source0:	%{name}-%{version}.tar.xz
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

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	Light hardware detection library linked against uClibc
Group:		System/Libraries
Requires:	ldetect-lst
Requires:	pciids

%description -n uclibc-%{libname}
see %{name}
%endif

%package -n	%{devname}
Group:		Development/C
Summary:	Development package for ldetect
Requires:	%{libname} = %{EVRD}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{EVRD}
%endif
Provides:	ldetect-devel = %{EVRD}

%description -n %{devname}
see %{name}

%prep
%setup -q

%if %{with diet}
mkdir -p diet
pushd diet
ln -s ../* .
popd
%endif

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
ln -s ../* .
popd
%endif

%build
%if %{with diet}
pushd diet
%make CFLAGS="-Os -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64 -fvisibility=hidden" CC="diet gcc" libldetect.a
popd
%endif

%if %{with uclibc}
pushd uclibc
%make CFLAGS="%{uclibc_cflags} -fvisibility=hidden" LDFLAGS="%{?ldflags}" CC="%{uclibc_cc}"
popd
%endif

%make CFLAGS="%{optflags} -Os -fvisibility=hidden" LDFLAGS="%{?ldflags}"

%install
%makeinstall
%if %{with diet}
install -m644 diet/libldetect.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif
%if %{with uclibc}
install -m644 uclibc/libldetect.a -D %{buildroot}%{uclibc_root}%{_libdir}/libldetect.a
cp -a uclibc/libldetect.so* %{buildroot}%{uclibc_root}%{_libdir}/
%endif

%files
%doc AUTHORS
%{_bindir}/*

%files -n %{libname}
%{_libdir}/*.so.%{major}
%{_libdir}/*.so.%{major}.%{minor}

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/*.so.%{major}
%{uclibc_root}%{_libdir}/*.so.%{major}.%{minor}
%endif

%files -n %{devname}
%doc ChangeLog
%{_includedir}/*
%{_libdir}/*.a
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libldetect.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libldetect.a
%{uclibc_root}%{_libdir}/*.so
%endif
%{_libdir}/*.so
