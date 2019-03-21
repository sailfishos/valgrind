#specfile originally created for Fedora, modified for Mer
Summary: Tool for finding memory management bugs in programs
Name: valgrind
Version: 3.14.0
Release: 1
Source0: http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
License: GPLv2
URL: http://www.valgrind.org/
Group: Development/Debuggers
ExclusiveArch: %{ix86} %{arm}
BuildRequires: pkgconfig
Requires: glibc-debuginfo

%ifarch %{ix86}
%define valarch x86
%define valsecarch %{nil}
%endif
%ifarch %{arm}
%define valarch arm
%define valsecarch %{nil}
%endif

%description
Valgrind is a tool to help you find memory-management problems in your
programs. When a program is run under Valgrind\'s supervision, all
reads and writes of memory are checked, and calls to
malloc/new/free/delete are intercepted. As a result, Valgrind can
detect a lot of problems that are otherwise very hard to
find/diagnose.

%package extratools
Summary: Additional tools for Valgrind (requires Perl)
Requires: valgrind = %{version}-%{release}

%description extratools
Additional tools for Valgrind. Includes callgrind and ms_print.
These depend on Perl support so might pull in lot of dependencies.

%package devel
Summary: Development files for valgrind
Group: Development/Debuggers
Requires: valgrind = %{version}-%{release}

%description devel
Header files and libraries for development of valgrind aware programs
or valgrind plugins.

# valgrind enforces usage of -Wl,--build-id=none 
# and debug packages requires build-id, so disable them
%define debug_package %{nil}

%prep
%setup -q -n %{name}-%{version}/%{name}

%build

# not a good idea to build valgrind with fortify, as it does not link glibc
RPM_OPT_FLAGS="`echo " %{optflags} " | sed 's/ -m\(64\|3[21]\) / /g;s/ -fexceptions / /g;s/^ //;s/ $//' | \
    sed s/-Wp,-D_FORTIFY_SOURCE=2// | sed s/-D_FORTIFY_SOURCE=2// | sed s/-fstack-protector//`"

# valgrind's instruction compiler does not work on thumb hosts
RPM_OPT_FLAGS="`echo " $RPM_OPT_FLAGS " | sed 's/ -mthumb / /g'`"

export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
autoreconf -fi
export GDB=/usr/bin/gdb

%configure CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS"
make %{_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall

%if "%{valsecarch}" != ""
pushd $RPM_BUILD_ROOT%{_libdir}/valgrind/
rm -f *-%{valsecarch}-* || :
for i in *-%{valarch}-*; do
  j=`echo $i | sed 's/-%{valarch}-/-%{valsecarch}-/'`
  ln -sf ../../lib/valgrind/$j $j
done
popd
%endif

rm -f $RPM_BUILD_ROOT%{_libdir}/valgrind/*.supp.in

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING
%{_bindir}/valgrind
%{_bindir}/valgrind-di-server
%{_bindir}/valgrind-listener
%{_bindir}/vgdb
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*[^ao]
%{_libdir}/valgrind/[^l]*o

%files extratools
%defattr(-,root,root)
%{_bindir}/callgrind_annotate
%{_bindir}/callgrind_control
%{_bindir}/cg_annotate
%{_bindir}/cg_diff
%{_bindir}/cg_merge
%{_bindir}/ms_print

%files devel
%defattr(-,root,root)
%{_includedir}/valgrind
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.a
%{_libdir}/pkgconfig/*

