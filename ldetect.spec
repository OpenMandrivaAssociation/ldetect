# EDIT IN GIT NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).
%define major 0.13
%define minor 11
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

%bcond_with uclibc

%ifarch aarch64
%global whoprog	0
%else
%global whoprog	1
%endif

Name:		ldetect
Version:	%{major}.%{minor}
Release:	12
Summary:	Light hardware detection tool
Group:		System/Kernel and hardware
License:	GPLv2+
URL:		https://abf.io/software/ldetect
Source0:	%{name}-%{version}.tar.xz
Patch0:		ldetect-0.13.11-usb.ids-location.patch
BuildRequires:	usbutils
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(libkmod)
BuildRequires:	pkgconfig(libpci)
BuildRequires:	pkgconfig(zlib)
%if %{with uclibc}
BuildRequires:	uClibc++-devel
BuildRequires:	uClibc-devel
BuildRequires:	uclibc-kmod-devel
BuildRequires:	uclibc-pciutils-devel
BuildRequires:	uclibc-zlib-devel
%endif

%description
The hardware device lists provided by this package are used as a lookup 
table to get hardware auto-detection.

%if %{with uclibc}
%package -n	uclibc-%{name}
Summary:	Light hardware detection tool (uClibc build)
Group:		System/Kernel and hardware

%description -n	uclibc-%{name}
The hardware device lists provided by this package are used as a lookup 
table to get hardware auto-detection.
%endif

%package -n	%{libname}
Summary:	Light hardware detection library
Group:		System/Libraries
Requires:	hwdata
Requires:	common-licenses
Requires:	pciids
# (tv) fix upgrade ordering (libpci3 needs to be updaded from 3.0 to 3.1 before ldetect is upgraded):
# (tv) and require a lib w/o double free:
Conflicts:	%{mklibname pci 3} < 3.1.4-3mdv2010.0

%description -n %{libname}
See %{name}.

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	Light hardware detection library linked against uClibc
Group:		System/Libraries
Requires:	hwdata
Requires:	pciids

%description -n uclibc-%{libname}
See %{name}.

%package -n	uclibc-%{devname}
Group:		Development/C
Summary:	Development package for ldetect
Requires:	%{devname} = %{EVRD}
Requires:	uclibc-%{libname} = %{EVRD}
Provides:	uclibc-ldetect-devel = %{EVRD}
Conflicts:	%{devname} < 0.13.11-3

%description -n uclibc-%{devname}
See %{name}.
%endif

%package -n	%{devname}
Group:		Development/C
Summary:	Development package for ldetect
Requires:	%{libname} = %{EVRD}
Provides:	ldetect-devel = %{EVRD}

%description -n %{devname}
See %{name}.

%package -n	perl-LDetect
Group:		Development/Perl
Summary:	Perl module for ldetect

%description -n	perl-LDetect
This package provides a perl module for using the ldetect library.

%prep
%autosetup -p1

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
ln -s ../* .
popd
%endif

%build
%if %{with uclibc}
pushd uclibc
# XXX: lto1: internal compiler error: in should_move_die_to_comdat, at dwarf2out.c:6974
%make_build OPTFLAGS="%{uclibc_cflags}" LDFLAGS="%{?ldflags}" LIBC=uclibc WHOLE_PROGRAM=%{whoprog}
popd
%endif

%make_build INCLUDES="$(pkg-config --cflags libkmod libpci)" OPTFLAGS="%{optflags}" LDFLAGS="%{?ldflags}" WHOLE_PROGRAM=%{whoprog}

pushd perl
perl Makefile.PL INSTALLDIRS=vendor OPTIMIZE="%{optflags}"
%make_build
popd

%install
%make_install lib=%{_lib}
%if %{with uclibc}
install -m644 uclibc/libldetect.a -D %{buildroot}%{uclibc_root}%{_libdir}/libldetect.a
cp -a uclibc/libldetect.so* %{buildroot}%{uclibc_root}%{_libdir}/
install -m755 uclibc/lspcidrake -D %{buildroot}%{uclibc_root}%{_bindir}/lspcidrake
%endif

%make_install -C perl

%check
%if ! %cross_compiling
# If lspcidrake doesn't crash, things aren't awful
LD_LIBRARY_PATH=`pwd` ./lspcidrake
%endif

%files
%doc AUTHORS
%{_bindir}/lspcidrake

%if %{with uclibc}
%files -n uclibc-%{name}
%doc AUTHORS
%{uclibc_root}%{_bindir}/lspcidrake
%endif

%files -n %{libname}
%{_libdir}/libldetect.so.%{major}
%{_libdir}/libldetect.so.%{major}.%{minor}

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/libldetect.so.%{major}
%{uclibc_root}%{_libdir}/libldetect.so.%{major}.%{minor}

%files -n uclibc-%{devname}
%{uclibc_root}%{_libdir}/libldetect.a
%{uclibc_root}%{_libdir}/libldetect.so
%endif

%files -n %{devname}
%doc ChangeLog
%dir %{_includedir}/ldetect
%{_includedir}/ldetect/*.h
%{_libdir}/pkgconfig/ldetect.pc
%{_libdir}/libldetect.a
%{_libdir}/libldetect.so

%files -n perl-LDetect
%{perl_vendorarch}/LDetect.pm
%dir %{perl_vendorarch}/auto/LDetect
%{perl_vendorarch}/auto/LDetect/LDetect.so
