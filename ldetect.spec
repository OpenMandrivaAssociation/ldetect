# EDIT IN GIT NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).
%define	major	0.13
%define	minor	4
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	uclibc

Name:		ldetect
Version:	%{major}.%{minor}
Release:	7
Summary:	Light hardware detection tool
Group:		System/Kernel and hardware
License:	GPLv2+
URL:		https://abf.rosalinux.ru/omv_software/ldetect
Source0:	%{name}-%{version}.tar.xz
Patch1:		ldetect-0.13.4-modules.patch
Patch2:		ldetect-0.13.4-sys_driver.patch
BuildRequires:	usbutils
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(libkmod)
BuildRequires:	pkgconfig(libpci)
BuildRequires:	pkgconfig(zlib)
%if %{with uclibc}
BuildRequires:	uClibc++-devel
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
Requires:	ldetect-lst
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
Requires:	ldetect-lst
Requires:	pciids

%description -n uclibc-%{libname}
See %{name}.
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
See %{name}.

%package -n	perl-LDetect
Group:		Development/Perl
Summary:	Perl module for ldetect

%description -n	perl-LDetect
This package provides a perl module for using the ldetect library.

%prep
%setup -q
%apply_patches
%ifarch %arm aarch64
sed -i 's/-fwhole-program//g' Makefile
%endif

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
%make OPTFLAGS="%{uclibc_cflags} -gdwarf-3" LDFLAGS="%{?ldflags}" LIBC=uclibc WHOLE_PROGRAM=1
popd
%endif

%make OPTFLAGS="%{optflags} -Os -gdwarf-3" LDFLAGS="%{?ldflags}" WHOLE_PROGRAM=1

pushd perl
perl Makefile.PL INSTALLDIRS=vendor OPTIMIZE="%{optflags} -Os"
%make
popd

%install
%makeinstall
%if %{with uclibc}
install -m644 uclibc/libldetect.a -D %{buildroot}%{uclibc_root}%{_libdir}/libldetect.a
cp -a uclibc/libldetect.so* %{buildroot}%{uclibc_root}%{_libdir}/
install -m755 uclibc/lspcidrake -D %{buildroot}%{uclibc_root}%{_bindir}/lspcidrake
%endif

%makeinstall_std -C perl

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
%endif

%files -n %{devname}
%doc ChangeLog
%dir %{_includedir}/ldetect
%{_includedir}/ldetect/*.h
%{_libdir}/pkgconfig/ldetect.pc
%{_libdir}/libldetect.a
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libldetect.a
%{uclibc_root}%{_libdir}/libldetect.so
%endif
%{_libdir}/libldetect.so

%files -n perl-LDetect
%{perl_vendorarch}/LDetect.pm
%dir %{perl_vendorarch}/auto/LDetect
%{perl_vendorarch}/auto/LDetect/LDetect.so
