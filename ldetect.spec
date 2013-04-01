# EDIT IN GIT NOT IN SOURCE PACKAGE (NO PATCH ALLOWED).
%define	major	0.13
%define	minor	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	uclibc

Name:		ldetect
Version:	%{major}.%{minor}
Release:	2
Summary:	Light hardware detection tool
Group:		System/Kernel and hardware
License:	GPLv2+
URL:		https://abf.rosalinux.ru/proyvind/ldetect
Source0:	%{name}-%{version}.tar.xz
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

%changelog
* Wed Jan 31 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.13.1-1
- new version:
	o various minor bug fixes & refactoring
	o fix minor memleak
	o make template implementations etc. internal
	o use std::map for usbNames, yielding a ~36% performance increase
	  (libstdc++ only, using uClibc++'s std::map implementation suffers
	  insane performance hit, so stick to old C implementation for now...)
	o reduce size quite a bit by dropping unused functionality from
	  usbNames class
	o rename intf 'class' to 'interface'
	o rewrite names.{h,cpp} into a proper C++ 'usbNames' class
	o move more stuff into common classes with common interfaces
	o kill error_and_die()
	o also check return value of ifstream::eof() as ifstream::getline() has
	  different behaviour for return value in uClibc++
	o work around broken implementation of ostream fill & setw in uClibc++

* Mon Jan  7 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.13.0-1
- disable -fwhole-program for uclibc build as compiler currently breaks with it
- reenable zlib support for uclibc build
- drop no longer supported dietlibc build
- switch back from mageia fork to latest version from upstream:
	o bump max devices number per bus from 100 to 300 (mga#8320) 
	o add pkgconfig file
	o install headers into dedicated directory
	o move functions from drakx perl module into a dedicated ldetect perl
	  module so that it'll be easier to maintain and also since no stable
	  API nor ABI can be expected in any near future
	o implement a C++ stream class for zlib
	o use names from dmi rather than the patterns matched against
	o store names of pci classes in a hash map for faster lookups
	o rewrite in C++

* Tue Oct 4 2012 Alexander Kazancev <kazancas@mandriva.org> 0.12.5-1
- Change sync from Mageia 
- make ldetect 3x faster (and even faster on machines quite quite a lot
of devices such as servers)
(modalias_init) split it out of modalias_resolve_module()
(modalias_cleanup) move libkmod related cleanups here
(hid_probe,find_modules_through_aliases) only initialize libkmod once
(which reduces user time from 0.26 to 0.08s & elapsed time from 0.28 to
0.9s)

- fix retrieving info about USB devices with kernel-3.5+
http://svnweb.mageia.org/soft/ldetect/trunk/usb.c?revision=5447&view=markup&pathrev=5447
poke in /sys/kernel/debug/usb/devices instead of /proc/bus/usb/devices
(needs "mount -t debugfs none /sys/kernel/debug")


* Mon Jun 18 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.12.4-1
+ Revision: 806125
- package uclibc build of lspcidrake
- zlib & lzma support is disabled for dietlibc & uclibc builds
- new version:
	o add support for building with -fwhole-program and use it by default
	o fix generated usbclass.c & pciclass.c to have functions matching
	  their prototypes

* Sat Jun 16 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.12.3-2
+ Revision: 806008
- build with -fvisibility=hidden, otherwise things get crashy (currently too lazy
  to investigate and determine exactly why.. :p)

* Fri Jun 15 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.12.3-1
+ Revision: 805916
- fix missing description for uclibc package
- don't disable -Werror flags
- build dynamically linked uClibc library
- build with %%optflags %% ldflags
- handle building of uclibc & dietlibc libraries better
- new version:
	o replace deprecated kmod_module_get_filtered_blacklist()
	o add support for building without zlib support

* Tue May 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.12.2-1
+ Revision: 800059
- new version
- build both uclibc & dietlibc builds

  + Andrey Bondrov <abondrov@mandriva.org>
    - Generate PCI classes info using ids from pcutils header instead of deprecated kernel header, add ldetect-0.12.1-pci patch

* Sat Mar 17 2012 Matthew Dawkins <mattydaw@mandriva.org> 0.12.1-1
+ Revision: 785450
- fixed build
- minor is 1 not 2
- added patch0 for kmod-5 includedir
- cleaned up spec
- there is also a format not a string error unresolved

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - build against uClibc in stead of dietlibc
    - ldetect now uses libkmod rather than libmodprobe
    - use a conflicts rather than requires to ensure new enough libpci
    - drop conflicts on ancient drakxtools version
    - use pkgconfig() dependencies
    - use %%bcond
    - update license
    - cleanups
    - new version

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.11.1-5
+ Revision: 666066
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.11.1-4mdv2011.0
+ Revision: 606398
- rebuild

  + Shlomi Fish <shlomif@mandriva.org>
    - Add a missing a, a full stop and a hyphen to the description.

* Tue Dec 01 2009 Thierry Vignaud <tv@mandriva.org> 0.11.1-3mdv2010.1
+ Revision: 472329
- do not crash if there're more than 100 PCI devices
- further use libpci in order to check for PCIe capability
- adjust comment

* Thu Oct 08 2009 Thierry Vignaud <tv@mandriva.org> 0.11.0-3mdv2010.0
+ Revision: 456029
- make sure to require a recent enough libpci3 (#54258)

* Thu Oct 01 2009 Thierry Vignaud <tv@mandriva.org> 0.11.0-2mdv2010.0
+ Revision: 452017
- reduce memory footprint

* Wed Sep 30 2009 Thierry Vignaud <tv@mandriva.org> 0.10.0-2mdv2010.0
+ Revision: 451794
- do not display random revisions for USB devices
- retrieve PCI capabilities in order to better identify PCI Express devices

* Mon Sep 28 2009 Thierry Vignaud <tv@mandriva.org> 0.9.1-2mdv2010.0
+ Revision: 450498
- fix inverted test for choosing between '8139cp' & '8139too' drivers (#53349)

* Wed Sep 23 2009 Thierry Vignaud <tv@mandriva.org> 0.9.0-2mdv2010.0
+ Revision: 448049
- display PCI revision (#42576)
- try harder to fetch the right driver between '8139cp' & '8139too'
  according to PCI revision

* Wed Sep 23 2009 Pascal Terjan <pterjan@mandriva.org> 0.8.6-1mdv2010.0
+ Revision: 447799
- Parse only once usb.ids (avoids displaying Duplicate errors)

* Mon Sep 14 2009 Thierry Vignaud <tv@mandriva.org> 0.8.5-5mdv2010.0
+ Revision: 440371
- do not display any warning when driver field is empty in
  /proc/bus/usb/devices (#53412)
- fix freed memory usage in criteria_from_dmidecode and entries_matching_criteria
- fix const warnings in dmi.c

* Tue Sep 01 2009 Thierry Vignaud <tv@mandriva.org> 0.8.4-4mdv2010.0
+ Revision: 423612
+ rebuild (emptylog)

* Tue Sep 01 2009 Thierry Vignaud <tv@mandriva.org> 0.8.4-3mdv2010.0
+ Revision: 423610
- fix upgrade ordering (libpci3 needs to be updaded from 3.0 to 3.1 before
  ldetect is upgraded) (#53347)

* Wed Jul 08 2009 Thierry Vignaud <tv@mandriva.org> 0.8.4-2mdv2010.0
+ Revision: 393575
- rebuild with latest pciutils

* Thu Jun 25 2009 Pascal Terjan <pterjan@mandriva.org> 0.8.4-1mdv2010.0
+ Revision: 389144
- fix freed memory usage in usb_probe and pci_probe
- use usb.ids to fill unknown strings

* Mon Apr 20 2009 Pascal Terjan <pterjan@mandriva.org> 0.8.3-1mdv2009.1
+ Revision: 368404
- fix parsing of /proc/bus/usb/device I: lines and use the class
  of the first interface used by a driver instead of the first
  interface (or first one like before when none is used).
  That fixed presenting something as usb_storage even if the
  device is ignored by usb_storage driver and handled on another
  interface by option driver
- ignore usb interfaces not active

* Mon Apr 06 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.8.2-1mdv2009.1
+ Revision: 364338
- 0.8.2:
  * don't use strchrnul which is not available in dietlibc
  * fix memory corruption in hid parsing

* Fri Apr 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.8.1-1mdv2009.1
+ Revision: 363841
- 0.8.1:
- enumerate hid bus
- fixes some memory leaks

* Sun Mar 29 2009 Olivier Blin <blino@mandriva.org> 0.8.0-2mdv2009.1
+ Revision: 362052
- 0.8.0
- do not use random string as device description
- use /sys/bus/usb/devices instead of /sys/class/usb_device
  (disabled in recent kernel) to find modalias
  (this breaks ABI because we now need to keep port number)

* Tue Feb 10 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.27-2mdv2009.1
+ Revision: 339097
- rebuild for new pciutils-3.1.2

* Thu Feb 05 2009 Luiz Fernando Capitulino <lcapitulino@mandriva.com> 0.7.27-1mdv2009.1
+ Revision: 337816
- 0.7.27

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 0.7.26-3mdv2009.0
+ Revision: 264770
- rebuild early 2009.0 package (before pixel changes)

* Tue Jun 10 2008 Oden Eriksson <oeriksson@mandriva.com> 0.7.26-2mdv2009.0
+ Revision: 217574
- rebuilt against dietlibc-devel-0.32

* Tue Jun 10 2008 Thierry Vignaud <tv@mandriva.org> 0.7.26-1mdv2009.0
+ Revision: 217498
- adapt to pciutils-3.x API

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Thu Apr 03 2008 Olivier Blin <blino@mandriva.org> 0.7.25-1mdv2008.1
+ Revision: 192070
- 0.7.25
- correctly use usbdev busnum and devnum when finding USB device in
  sysfs to get its modalias (#38721)

* Thu Mar 20 2008 Pixel <pixel@mandriva.com> 0.7.24-1mdv2008.1
+ Revision: 189156
- 0.7.23:
- lspcidrake.c: when faking probe (ie -p, -u, --dmidecode), do not do real probe

* Fri Feb 29 2008 Olivier Blin <blino@mandriva.org> 0.7.23-1mdv2008.1
+ Revision: 176792
- 0.7.23
- fix segfault on x86_64

* Thu Feb 28 2008 Olivier Blin <blino@mandriva.org> 0.7.22-1mdv2008.1
+ Revision: 176427
- 0.7.22
- really use modules.alias file from kernel or ldetect-lst

* Wed Feb 27 2008 Olivier Blin <blino@mandriva.org> 0.7.21-1mdv2008.1
+ Revision: 175899
- build dietlibc version with -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64 to be able to use dirent
- 0.7.21
- add back /bin/gzip support, and prefer it if available
  (and be 6 hundredths of second faster...)
- do not ignore subsequent modaliases if resolving one fails
- find modules from USB modaliases as well (#38158, useful when module
  is a dkms one, or during install where modules are not autoloaded,
  this could allow to remove most modules from usbtable)

* Wed Jan 02 2008 Thierry Vignaud <tv@mandriva.org> 0.7.20-2mdv2008.1
+ Revision: 140638
- rebuild with latest libpci
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Fri Sep 28 2007 Olivier Blin <blino@mandriva.org> 0.7.20-1mdv2008.0
+ Revision: 93761
- 0.7.20
- fix modalias fd leak (thanks to Anssi for the report

* Wed Sep 19 2007 Olivier Blin <blino@mandriva.org> 0.7.19-1mdv2008.0
+ Revision: 90895
- 0.7.19
- replace '-' characters from USB drivers with '_' to be compliant
  with modnames from modaliases (partially fixes #33029)

* Tue Sep 11 2007 Olivier Blin <blino@mandriva.org> 0.7.18-1mdv2008.0
+ Revision: 84471
- 0.7.18
- use ldetect-lst aliases from /lib/module-init-tools/, not from /usr
- do not read modules.dep (lspcidrake is now twice faster)

* Sun Sep 09 2007 Olivier Blin <blino@mandriva.org> 0.7.17-1mdv2008.0
+ Revision: 83427
- 0.7.17
- use module aliases from first match only

* Fri Sep 07 2007 Olivier Blin <blino@mandriva.org> 0.7.16-1mdv2008.0
+ Revision: 81779
- 0.7.16
- fallback on ldetect-lst's dkms-modules.alias if no alias is found
 (to find modules available in dkms packages)
- use ldetect's preferred-modules.alias file before other aliases files

* Mon Aug 27 2007 Thierry Vignaud <tv@mandriva.org> 0.7.15-1mdv2008.0
+ Revision: 71969
- fix soname

* Mon Aug 27 2007 Thierry Vignaud <tv@mandriva.org> 0.7.14-2mdv2008.0
+ Revision: 71947
- use gcc instead of ld again

* Mon Aug 27 2007 Thierry Vignaud <tv@mandriva.org> 0.7.13-2mdv2008.0
+ Revision: 71906
- fix overwriting pcitable results from modaliases
- use visibility in order to enforce exported ABI and to reduce code size

* Wed Aug 22 2007 Olivier Blin <blino@mandriva.org> 0.7.12-2mdv2008.0
+ Revision: 69163
- 0.7.12
- prefer ldetect-lst's modules.alias if more recent
  (to detect modular IDE controllers when run from old kernels)

* Mon Aug 20 2007 Olivier Blin <blino@mandriva.org> 0.7.11-2mdv2008.0
+ Revision: 67451
- 0.7.11: revert '_' characters substitution

* Mon Aug 20 2007 Thierry Vignaud <tv@mandriva.org> 0.7.10-2mdv2008.0
+ Revision: 67220
- rebuild

* Thu Aug 16 2007 Thierry Vignaud <tv@mandriva.org> 0.7.10-1mdv2008.0
+ Revision: 64349
- fallback to ldetect-lst's modules.alias if kernel's modules.alias cannot be
  found (eg: installer)
- plug some minor memory leaks

* Thu Aug 16 2007 Thierry Vignaud <tv@mandriva.org> 0.7.9-2mdv2008.0
+ Revision: 64325
- fix zlib conversion which introduced a crash (#32590)

* Wed Aug 15 2007 Olivier Blin <blino@mandriva.org> 0.7.8-2mdv2008.0
+ Revision: 63560
- build dietlibc library with -Os
- 0.7.8: use zlib to read gzipped files instead of piping gzip command

* Tue Aug 14 2007 Olivier Blin <blino@mandriva.org> 0.7.7-2mdv2008.0
+ Revision: 63353
- add dietlibc static library

* Tue Aug 14 2007 Olivier Blin <blino@mandriva.org> 0.7.7-1mdv2008.0
+ Revision: 63215
- package static library
- buildrequire mdoprobe-devel
- 0.7.7
- remove old 8139too/gdth hardcoded rules (already in modules.alias)
- replace '_' characters with '-' to be compliant with pcitable and list_modules.pm

* Mon Aug 13 2007 Thierry Vignaud <tv@mandriva.org> 0.7.6-2mdv2008.0
+ Revision: 62691
- rebuild with shared modprobe library

* Tue Aug 07 2007 Thierry Vignaud <tv@mandriva.org> 0.7.6-1mdv2008.0
+ Revision: 59871
- better error managment:
  o exit() is not nice error managment in a library
  o print fatal error on stderr (pixel)
- don't free before printing (pixel)

* Mon Aug 06 2007 Thierry Vignaud <tv@mandriva.org> 0.7.5-1mdv2008.0
+ Revision: 59402
- handle pcitable without description field

* Mon Aug 06 2007 Thierry Vignaud <tv@mandriva.org> 0.7.4-1mdv2008.0
+ Revision: 59342
- kill most quirks since they are obsolete now that we resolve modaliases
  (which bring in wildcard support)

* Mon Aug 06 2007 Thierry Vignaud <tv@mandriva.org> 0.7.3-4mdv2008.0
+ Revision: 59266
- versionnate module-init-tools-devel buildrequires
- fix buildrequires
- reuse modprobe code in order to resolve modaliases
- rebuild with latest pciutils

* Tue Jun 26 2007 Thierry Vignaud <tv@mandriva.org> 0.7.2-2mdv2008.0
+ Revision: 44545
- new devel library policy

* Mon May 14 2007 Thierry Vignaud <tv@mandriva.org> 0.7.2-1.1mdv2008.0
+ Revision: 26722
- don't link with zlib since it's not needed

* Mon May 07 2007 Pixel <pixel@mandriva.com> 0.7.1-1mdv2008.0
+ Revision: 23997
- new release, 0.7.1 (build with zlib which is needed by libpci)

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - add zlib to buildrequires (see #30672, source needs to be patched in svn too..)


* Fri Mar 09 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.7.0-5mdv2007.1
+ Revision: 138796
- require pciids instead of /usr/share/pci.ids

* Thu Mar 08 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.7.0-4mdv2007.1
+ Revision: 138469
- ldetect engine now requires pci.ids
- fix conflict on x86_64

* Wed Feb 28 2007 Pixel <pixel@mandriva.com> 0.7.0-3mdv2007.1
+ Revision: 127029
- add explicit conflict on previous lib

* Mon Feb 26 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.7.0-2mdv2007.1
+ Revision: 126045
- versionnate provides

* Mon Feb 26 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.7.0-1mdv2007.1
+ Revision: 125975
- switch to pciutils as PCI enumerating backend
- use pciutils in order to get device descriptions from
  /usr/share/pci.ids
- export pci_domain and class (PCI class as reported by pciutils)
- bump major due to ABI changes

* Wed Jan 10 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.6.7-1mdv2007.1
+ Revision: 107141
- fix warnings on parsing /proc/bus/usb/devices with kernel-2.6.20

* Mon Nov 06 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.6.6-1mdv2007.0
+ Revision: 76952
- Import ldetect

* Mon Nov 06 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.6.6-1mdv2007.1
- fix parsing /proc/bus/usb/devices with large "parent device" field
  (veryy rare case)

* Thu Jul 13 2006 Olivier Blin <oblin@mandriva.com> 0.6.5-1mdv2007.0
- dmidecode >= 2.7 support
- fix freeing a reference to a constant string (fredl)

* Thu Jan 05 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 0.6.4-1mdk
- add support for pci domains

* Sat Aug 06 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.6.3-1mdk
- prevent spurious warnings for strange USB interfaces

* Tue May 17 2005 Thierry Vignaud <tvignaud@mandriva.com> 0.6.2-1mdk
- do not try to run dmidecode when not root

* Thu Mar 31 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.6.1-1mdk
- fix SATA detection of latest NVidia controllers

* Mon Mar 14 2005 Pixel <pixel@mandrakesoft.com> 0.6.0-1mdk
- add dmitable parsing and use
- libldetect.so instead of libldetect.a
- libification

* Thu Feb 17 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.5.5-1mdk
- handle a few more special cases (gdth, snd-vx222, 8139too, and agp bridges)
- detect new VIA SATA controllers like kernel does

* Tue Dec 07 2004 Pixel <pixel@mandrakesoft.com> 0.5.4-1mdk
- all PCI_CLASS_BRIDGE_CARDBUS cards are yenta_socket (says kudzu)

* Fri Oct 29 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.5.3-1mdk
- keep existing description string if already reported by USB devices
  when usbtable description is empty (eg: freebox)

* Fri Jun 18 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.5.2-1mdk
- display driver reported by the kernel rather than "unknown"

