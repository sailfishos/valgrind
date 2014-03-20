#specfile originally created for Fedora, modified for Mer
Summary: Tool for finding memory management bugs in programs
Name: valgrind
Version: 3.9.0
Release: 1
Source0: http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
License: GPLv2
URL: http://www.valgrind.org/
Group: Development/Debuggers
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
ExclusiveArch: %{ix86} %{arm}
BuildRequires: pkgconfig

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
    sed s/-Wp,-D_FORTIFY_SOURCE=2// | sed s/-D_FORTIFY_SOURCE=2//`"

export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
autoreconf -fi
export GDB=/usr/bin/gdb
%configure CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS"
make %{_smp_mflags}

# Ensure there are no unexpected file descriptors open,
# the testsuite otherwise fails.
cat > close_fds.c <<EOF
#include <stdlib.h>
#include <unistd.h>
int main (int argc, char *const argv[])
{
  int i, j = sysconf (_SC_OPEN_MAX);
  if (j < 0)
    exit (1);
  for (i = 3; i < j; ++i)
    close (i);
  execvp (argv[1], argv + 1);
  exit (1);
}
EOF
gcc $RPM_OPT_FLAGS -o close_fds close_fds.c

# XXX pth_cancel2 hangs on x86_64
#echo 'int main (void) { return 0; }' > none/tests/pth_cancel2.c

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall
mkdir docs.installed
mv $RPM_BUILD_ROOT%{_datadir}/doc/valgrind/* docs.installed/
rm -f docs.installed/*.ps

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

%check
make check || :
echo ===============TESTING===================
# tests are almost useless (due to missing glibc-debuginfo at least),
# and in case of another platform. But about half - should pass.
./close_fds make regtest || :
echo ===============END TESTING===============

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING NEWS README_*
%doc docs.installed/html docs.installed/*.pdf
%{_bindir}/*
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*[^ao]
%{_libdir}/valgrind/[^l]*o
%{_mandir}/man1/*

%files devel
%defattr(-,root,root)
%{_includedir}/valgrind
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.a
%{_libdir}/pkgconfig/*

