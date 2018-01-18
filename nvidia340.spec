## I love OpenSource :-(

## NOTE: When modifying this .spec, you do not necessarily need to care about
##       the %simple stuff. It is fine to break them, I'll fix it when I need them :)
## - Anssi

# %simple mode can be used to transform an arbitrary nvidia installer
# package to rpms, similar to %atibuild mode in fglrx.
# Macros version, rel, nsource, pkgname, distsuffix should be manually defined.
%define simple 0
%{?_without_simple: %global simple 0}
%{?_with_simple: %global simple 1}

%define name nvidia340

%if !%simple
# When updating, please add new ids to ldetect-lst (merge2pcitable.pl)
%define version  340.106
%define rel 1
# the highest supported videodrv abi
%define videodrv_abi 23
%endif

%define priority 9851

%define pkgname32 NVIDIA-Linux-x86-%{version}
%define pkgname64 NVIDIA-Linux-x86_64-%{version}

# For now, backportability is kept for 2008.0 forwards.

%define drivername nvidia340
%define driverpkgname x11-driver-video-%{drivername}
%define modulename %{drivername}
# for description and documentation
%define cards GeForce 8xxx, 9xxx and 100 to 415 cards
%define xorg_extra_modules %{_libdir}/xorg/extra-modules
%define nvidia_driversdir %{_libdir}/%{drivername}/xorg
%define nvidia_extensionsdir %{_libdir}/%{drivername}/xorg
%define nvidia_modulesdir %{_libdir}/%{drivername}/xorg
%define nvidia_libdir %{_libdir}/%{drivername}
%define nvidia_libdir32 %{_prefix}/lib/%{drivername}
%define nvidia_bindir %{nvidia_libdir}/bin
# The entry in Cards+ this driver should be associated with, if there is
# no entry in ldetect-lst default pcitable:
# cooker ldetect-lst should be up-to-date
%define ldetect_cards_name %nil

# NVIDIA cards not listed in main ldetect-lst pcitable are not likely
# to be supported by nv which is from the same time period. Therefore
# mark them as not working with nv. (main pcitable entries override
# our entries)
%if %simple
# nvidia/vesa
%define ldetect_cards_name NVIDIA GeForce 420 series and later
%endif

%define biarches x86_64

%if !%simple
%ifarch %{ix86}
%define nsource %{SOURCE0}
%define pkgname %{pkgname32}
%endif
%ifarch x86_64
%define nsource %{SOURCE1}
%define pkgname %{pkgname64}
%endif
%endif

# Other packages should not require any NVIDIA libraries, and this package
# should not be pulled in when libGL.so.1 is required
%define __noautoprov 'libGL\\.so\\.1(.*)|devel\\(libGL(.*)|\\.so'
%define common_requires_exceptions ^libGL\\.so\\|^libGLcore\\.so\\|^libnvidia.*\\.so

%ifarch %{biarches}
# (anssi) Allow installing of 64-bit package if the runtime dependencies
# of 32-bit libraries are not satisfied. If a 32-bit package that requires
# libGL.so.1 is installed, the 32-bit mesa libs are pulled in and that will
# pull the dependencies of 32-bit nvidia libraries in as well.
%define __noautoreq %common_requires_exceptions\\|^lib.*so\\.[^(]\\+\\(([^)]\\+)\\)\\?$
%else
%define __noautoreq %common_requires_exceptions
%endif

# https://devtalk.nvidia.com/default/topic/523762/libnvidia-encode-so-310-19-has-dependency-on-missing-library/
%define __noautoreqfiles libnvidia-encode.so.%{version}

Summary:	NVIDIA proprietary X.org driver and libraries, 340.xx series
Name:		%{name}
Version:	%{version}
Release:	%{rel}
%if !%simple
Source0:	ftp://download.nvidia.com/XFree86/Linux-x86/%{version}/%{pkgname32}.run
Source1:	ftp://download.nvidia.com/XFree86/Linux-x86_64/%{version}/%{pkgname64}.run
# GPLv2 source code; see also http://cgit.freedesktop.org/~aplattner/
Source2:	ftp://download.nvidia.com/XFree86/nvidia-settings/nvidia-settings-%{version}.tar.bz2
Source3:	ftp://download.nvidia.com/XFree86/nvidia-xconfig/nvidia-xconfig-%{version}.tar.bz2
# Script for building rpms of arbitrary nvidia installers (needs this .spec appended)
Source4:	nvidia-mdvbuild-skel
Source5:	ftp://download.nvidia.com/XFree86/nvidia-modprobe/nvidia-modprobe-%{version}.tar.bz2
Source6:	ftp://download.nvidia.com/XFree86/nvidia-persistenced/nvidia-persistenced-%{version}.tar.bz2
Source100:	nvidia340.rpmlintrc
Patch2:		NVIDIA-Linux-x86_64-346.35-kernel-3.18-fix.patch
# include xf86vmproto for X_XF86VidModeGetGammaRampSize, fixes build on cooker
Patch3:		nvidia-settings-include-xf86vmproto.patch
Patch8:		nvidia-persistenced-319.17-add-missing-libtirpc-link.patch
Patch9:		NVIDIA-Linux-x86_64-340.104-kernel-4.11.patch
Patch10:	NVIDIA-Linux-x86_64-340.104-kernel-4.14.patch
%endif
License:	Freeware
URL:		http://www.nvidia.com/object/unix.html
Group:		System/Kernel and hardware
ExclusiveArch:	%{ix86} x86_64
%if !%simple
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(vdpau) >= 0.9
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(xv)
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(xxf86vm)
%endif
BuildRequires:	rpm-build >= 1:5.3.12

%description
Source package of the NVIDIA proprietary driver. Binary
packages are named x11-driver-video-nvidia-%{drivername}.

%package -n %{driverpkgname}
Summary:	NVIDIA proprietary X.org driver and libraries 304.xx
Group:		System/Kernel and hardware
Requires(post):	update-alternatives >= 1.9.0
Requires(postun):	update-alternatives >= 1.9.0
Requires:	x11-server-common
# Proprietary driver handling rework:
Conflicts:	harddrake < 10.4.163
Conflicts:	drakx-kbd-mouse-x11 < 0.21
Conflicts:	x11-server-common < 1.3.0.0-17
Suggests:	%{drivername}-doc-html = %{version}
# for missing libwfb.so
Conflicts:	x11-server-common < 1.4
# Proper support for versioned kmod() was added in 2008.1:
Requires:	kmod(%{modulename}) = %{version}
# At least mplayer dlopens libvdpau.so.1, so the software will not pull in
# the vdpau library package. We ensure its installation here.
# (vdpau package exists in main on 2009.0+)
Requires:	%{_lib}vdpau1
Conflicts:	x11-server-common < 1.6.0-11
%if !%simple
# Conflict with the next videodrv ABI break.
# The NVIDIA driver supports the previous ABI versions as well and therefore
# a strict version-specific requirement would not be enough.
### This is problematic as it can cause removal of xserver instead (Anssi 04/2011)
###Conflicts:	xserver-abi(videodrv-%(echo $((%{videodrv_abi} + 1))))
%endif
# Obsoletes for naming changes:
Obsoletes:	nvidia < 1:%{version}-%{release}
Provides:	nvidia = 1:%{version}-%{release}
Obsoletes:	nvidia97xx < %{version}-%{release}
Provides:	nvidia97xx = %{version}-%{release}
%ifarch %{biarches}
Suggests:	%{driverpkgname}-32bit = %{version}-%{release}
%endif
Conflicts:	%{drivername}-cuda-opencl <= 325.15-1

%description -n %{driverpkgname}
NVIDIA proprietary X.org graphics driver, related libraries and
configuration tools for %cards,
including the associated Quadro cards.

NOTE: You should use XFdrake to configure your NVIDIA card. The
correct packages will be automatically installed and configured.

If you do not want to use XFdrake, see README.manual-setup.

This NVIDIA driver should be used with %cards,
including the associated Quadro cards.

%ifarch %{biarches}
%package -n %{driverpkgname}-32bit
Summary:	32-bit compatibility libraries for the NVIDIA proprietary driver
Group:		System/Kernel and hardware
Conflicts:	%{drivername}-cuda-opencl <= 325.15-1

%description -n %{driverpkgname}-32bit
32-bit compatibility libraries for the NVIDIA proprietary driver.
%endif

%package -n dkms-%{drivername}
Summary:	NVIDIA kernel module for %cards
Group:		System/Kernel and hardware
Requires:	dkms >= 2.2.0.3.1-3.20130827.8
Requires(post):	dkms >= 2.2.0.3.1-3.20130827.8
Requires(preun):	dkms >= 2.2.0.3.1-3.20130827.8
Obsoletes:	dkms-nvidia < 1:%{version}-%{release}
Provides:	dkms-nvidia = 1:%{version}-%{release}
Obsoletes:	dkms-nvidia97xx < %{version}-%{release}
Provides:	dkms-nvidia97xx = %{version}-%{release}

%description -n dkms-%{drivername}
NVIDIA kernel module for %cards. This
is to be used with the %{driverpkgname} package.

%package -n %{drivername}-devel
Summary:	NVIDIA OpenGL/CUDA development liraries and headers
Group:		Development/C
Requires:	%{driverpkgname} = %{version}-%{release}
Requires:	%{drivername}-cuda-opencl = %{version}-%{release}
Obsoletes:	nvidia-devel < 1:%{version}-%{release}
Provides:	nvidia-devel = 1:%{version}-%{release}
Obsoletes:	nvidia97xx-devel < %{version}-%{release}
Provides:	nvidia97xx-devel = %{version}-%{release}
Requires:	%{_lib}vdpau-devel

%description -n %{drivername}-devel
NVIDIA OpenGL/CUDA headers for %cards.
This package is not required for normal use.

%package -n %{drivername}-cuda-opencl
Summary:	CUDA and OpenCL libraries for NVIDIA proprietary driver
Group:		System/Kernel and hardware
Provides:	%{drivername}-cuda = %{version}-%{release}
# Proper support for versioned kmod() was added in 2008.1:
Requires:	kmod(%{modulename}) = %{version}
Conflicts:	nvidia < 1:195.36.15-4
%if "%_lib" == "lib64"
Provides:	libnvcuvid.so.1()(64bit)
%ifarch %biarches
Provides:	libnvcuvid.so.1
%endif
%else
Provides:	libnvcuvid.so.1
%endif

%description -n %{drivername}-cuda-opencl
Cuda and OpenCL libraries for NVIDIA proprietary driver.
This package is not required for normal use, it provides
libraries to use NVIDIA cards for High Performance Computing (HPC).

# HTML doc splitted off because of size, for live cds:
%package -n %{drivername}-doc-html
Summary:	NVIDIA html documentation (%{drivername})
Group:		System/Kernel and hardware
Requires:	%{driverpkgname} = %{version}-%{release}

%description -n %{drivername}-doc-html
HTML version of the README.txt file provided in package
%{driverpkgname}.

%prep
#define _default_patch_fuzz 2
# No patches applied when %simple is set
%if %simple
%setup -q -c -T
%else
%setup -q -c -T -a 2 -a 3 -a 5 -a 6
cd nvidia-settings-%{version}
%patch3 -p1
cd ..
cd nvidia-persistenced-%{version}
%patch8 -p1
cd ..
%endif

sh %{nsource} --extract-only

%if !%simple
cd %{pkgname}
%patch2 -p1
%patch9 -p1
%patch10 -p1
cd ..
%endif

rm -rf %{pkgname}/usr/src/nv/precompiled

%if %simple
# for old releases
mkdir -p %{pkgname}/kernel
%endif

# (tmb) nuke nVidia provided dkms.conf as we need our own
rm -f %{pkgname}/kernel/dkms.conf
rm -f %{pkgname}/kernel/uvm/dkms.conf.fragment

# install our own dkms.conf
cat > %{pkgname}/kernel/dkms.conf <<EOF
PACKAGE_NAME="%{drivername}"
PACKAGE_VERSION="%{version}-%{release}"
BUILT_MODULE_NAME[0]="nvidia"
DEST_MODULE_LOCATION[0]="/kernel/drivers/char/drm"
DEST_MODULE_NAME[0]="%{modulename}"
%ifarch x86_64
BUILT_MODULE_NAME[1]="nvidia-uvm"
BUILT_MODULE_LOCATION[1]="uvm/"
DEST_MODULE_LOCATION[1]="/kernel/drivers/char/drm"
%endif
MAKE[0]="make CC=gcc SYSSRC=\${kernel_source_dir} module"
%ifarch x86_64
MAKE[0]+="; make CC=gcc SYSSRC=\${kernel_source_dir} -C uvm module KBUILD_EXTMOD=\${dkms_tree}/%{drivername}/%{version}-%{release}/build/uvm"
%endif
CLEAN="make -f Makefile.kbuild clean"
%ifarch x86_64
CLEAN+="; make -C uvm clean"
%endif
AUTOINSTALL="yes"
EOF

cat > README.install.urpmi <<EOF
This driver is for %cards.

Use XFdrake to configure X to use the correct NVIDIA driver. Any needed
packages will be automatically installed if not already present.
1. Run XFdrake as root.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.

If you do not want to use XFdrake, see README.manual-setup.
EOF

cat > README.manual-setup <<EOF
This file describes the procedure for the manual installation of this NVIDIA
driver package. You can find the instructions for the recommended automatic
installation in the file 'README.install.urpmi' in this directory.

- Open %{_sysconfdir}/X11/xorg.conf and make the following changes:
  o Change the Driver to "nvidia" in the Device section
  o Make the line below the only 'glx' related line in the Module section,
    adding it if it is not already there:
      Load "glx"
  o Remove any 'ModulePath' lines from the Files section
- Run "update-alternatives --set gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf" as root.
- Run "ldconfig -X" as root.
EOF

%if !%simple
rm nvidia-settings-%{version}/src/*/*.a ||:

%build
%setup_compile_flags

# (tpg) needed for patch 6
# i couldn't push this to patch 6 because of fuzz error
# even with fuzz 2 this does not work
# drop this if upstream will accept patches
pushd nvidia-settings-%{version}
sed -i -e 's#nv_warning_msg([^)]*err_str);#nv_warning_msg(*err_str, "%s");#g' src/gtk+-2.x/ctkdisplayconfig-utils.c
popd

# (tpg) need to provide a patch to fix format error
export CFLAGS="%{optflags} -Wno-error=format-security"

%make -C nvidia-settings-%{version}/src/libXNVCtrl
%make -C nvidia-settings-%{version} STRIP_CMD=true
%make -C nvidia-xconfig-%{version} STRIP_CMD=true
%make -C nvidia-modprobe-%{version} STRIP_CMD=true
%make -C nvidia-persistenced-%{version} STRIP_CMD=true

# %simple
%endif

%install
cd %{pkgname}

# dkms
install -d -m755 %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}

# menu entry
install -d -m755 %{buildroot}%{_datadir}/%{drivername}
cat > %{buildroot}%{_datadir}/%{drivername}/%{disttag}-nvidia-settings.desktop <<EOF
[Desktop Entry]
Name=NVIDIA Display Settings
Comment=Configure NVIDIA X driver
Exec=%{_bindir}/nvidia-settings
Icon=%{drivername}-settings
Terminal=false
Type=Application
Categories=GTK;Settings;HardwareSettings;
EOF

install -d -m755 %{buildroot}%{_datadir}/applications
touch %{buildroot}%{_datadir}/applications/%{disttag}-nvidia-settings.desktop

# icons
install -d -m755 %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
%if !%simple
convert nvidia-settings.png -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{drivername}-settings.png
convert nvidia-settings.png -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{drivername}-settings.png
convert nvidia-settings.png -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png
%else
# no imagemagick
[ -e nvidia-settings.png ] || cp -a usr/share/pixmaps/nvidia-settings.png .
install -m644 nvidia-settings.png %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png
%endif

error_fatal() {
	echo "Error: $@." >&2
	exit 1
}

error_unhandled() {
	echo "Warning: $@." >&2
	echo "Warning: $@." >> warns.log
%if !%simple
	# cause distro builds to fail in case of unhandled files
	exit 1
%endif
}

parseparams() {
	for value in $rest; do
		local param=$1
		[ -n "$param" ] || error_fatal "unhandled parameter $value"
		shift
		eval $param=$value

		[ -n "$value" ] || error_fatal "empty $param"

		# resolve libdir based on $arch
		if [ "$param" = "arch" ]; then
			case "$arch" in
			NATIVE)		nvidia_libdir=%{nvidia_libdir};;
			COMPAT32)	nvidia_libdir=%{nvidia_libdir32};;
			*)		error_fatal "unknown arch $arch"
			esac
		fi
	done
}

add_to_list() {
%if !%simple
	# on distro builds, only use .manifest for %doc files
	[ "${2#%doc}" = "${2}" ] && return
%endif
	local list="$1.files"
	local entry="$2"
	echo $entry >> $list
}

install_symlink() {
	local pkg="$1"
	local dir="$2"
	mkdir -p %{buildroot}$dir
	ln -s $dest %{buildroot}$dir/$file
	add_to_list $pkg $dir/$file
}

install_lib_symlink() {
	local pkg="$1"
	local dir="$2"
	case "$file" in
	libvdpau_*.so)
		# vdpau drivers => not put into -devel
		;;
	*.so)
		pkg=nvidia-devel;;
	esac
	install_symlink $pkg $dir
}

install_file_only() {
	local pkg="$1"
	local dir="$2"
	mkdir -p %{buildroot}$dir
	# replace 0444 with more usual 0644
	[ "$perms" = "0444" ] && perms="0644"
	install -m $perms $file %{buildroot}$dir
}

install_file() {
	local pkg="$1"
	local dir="$2"
	install_file_only $pkg $dir
	add_to_list $pkg $dir/$(basename $file)
}

get_module_dir() {
	local subdir="$1"
	case "$subdir" in
	extensions*)	echo %{nvidia_extensionsdir};;
	drivers/)	echo %{nvidia_driversdir};;
	/)		echo %{nvidia_modulesdir};;
	*)		error_unhandled "unhandled module subdir $subdir"
			echo %{nvidia_modulesdir};;
	esac
}

for file in nvidia.files nvidia-devel.files nvidia-cuda.files nvidia-dkms.files nvidia-html.files; do
	rm -f $file
	touch $file
done

# install files according to .manifest
cat .manifest | tail -n +9 | while read line; do
	arch=
	style=
	subdir=
	dest=
	nvidia_libdir=

	rest=${line}
	file=${rest%%%% *}
	rest=${rest#* }
	perms=${rest%%%% *}
	rest=${rest#* }
	type=${rest%%%% *}
	[ "${rest#* }" = "$rest" ] && rest= || rest=${rest#* }

	case "$type" in
	CUDA_LIB)
		parseparams arch subdir
		install_file nvidia-cuda $nvidia_libdir/$subdir
		;;
	CUDA_SYMLINK)
		parseparams arch subdir dest
		install_lib_symlink nvidia-cuda $nvidia_libdir/$subdir
		;;
	EXPLICIT_PATH)
		parseparams dest
		install_file nvidia %{_datadir}/nvidia
    		;;
	NVCUVID_LIB)
		parseparams arch subdir
		install_file nvidia-cuda $nvidia_libdir/$subdir
		;;
	NVCUVID_LIB_SYMLINK)
		parseparams arch dest
		install_lib_symlink nvidia $nvidia_libdir
		;;
	OPENCL_LIB)
		parseparams arch subdir
		install_file nvidia-cuda $nvidia_libdir/$subdir
		;;
	OPENCL_LIB_SYMLINK)
		parseparams arch subdir dest
		install_lib_symlink nvidia-cuda $nvidia_libdir/$subdir
		;;
	OPENCL_WRAPPER_LIB)
		parseparams arch subdir
		install_file nvidia-cuda $nvidia_libdir/$subdir
		;;
	OPENCL_WRAPPER_SYMLINK)
		parseparams arch subdir dest
		install_lib_symlink nvidia-cuda $nvidia_libdir/$subdir
		;;
	OPENGL_LIB)
		parseparams arch
		install_file nvidia $nvidia_libdir
		;;
	OPENGL_SYMLINK)
		parseparams arch dest
		install_lib_symlink nvidia $nvidia_libdir
		;;
	TLS_LIB)
		parseparams arch style subdir
		install_file nvidia $nvidia_libdir/$subdir
		;;
	TLS_SYMLINK)
		parseparams arch style subdir dest
		install_lib_symlink nvidia $nvidia_libdir/$subdir
		;;
	UTILITY_LIB)
		# backward-compatibility
		[ -n "${rest}" ] || rest="NATIVE $rest"
		parseparams arch subdir
		install_file nvidia $nvidia_libdir/$subdir
		;;
	UTILITY_LIB_SYMLINK)
		# backward-compatibility
		[ "${rest#* }" != "$rest" ] || rest="NATIVE $rest"
		parseparams arch dest
		install_lib_symlink nvidia $nvidia_libdir
		;;
	VDPAU_LIB|VDPAU_WRAPPER_LIB)
		parseparams arch subdir
		# on 2009.0+, only install libvdpau_nvidia.so
		case $file in *libvdpau_nvidia.so*);; *) continue; esac
		install_file nvidia $nvidia_libdir/$subdir
		;;
	VDPAU_SYMLINK|VDPAU_WRAPPER_SYMLINK)
		parseparams arch subdir dest
		# on 2009.0+, only install libvdpau_nvidia.so
		case $file in *libvdpau_nvidia.so*);; *) continue; esac
		install_lib_symlink nvidia $nvidia_libdir/$subdir
		;;
	XLIB_STATIC_LIB)
		install_file nvidia-devel %{nvidia_libdir}
		;;
	XLIB_SHARED_LIB)
		install_file nvidia %{nvidia_libdir}
		;;
	XLIB_SYMLINK)
		parseparams dest
		install_lib_symlink nvidia %{nvidia_libdir}
		;;
	LIBGL_LA)
		# (Anssi) we don't install .la files
		;;
	XMODULE_SHARED_LIB|GLX_MODULE_SHARED_LIB)
		parseparams subdir
		install_file nvidia $(get_module_dir $subdir)
		;;
	XMODULE_NEWSYM)
		# symlink that is created only if it doesn't already
		# exist (i.e. as part of x11-server)
		case "$file" in
		libwfb.so)
		# 2008.1+ has this one already
			continue
			;;
		*)
			error_unhandled "unknown XMODULE_NEWSYM type file $file, skipped"
			continue
		esac
		parseparams subdir dest
		install_symlink nvidia $(get_module_dir $subdir)
		;;
	XMODULE_SYMLINK|GLX_MODULE_SYMLINK)
		parseparams subdir dest
		install_symlink nvidia $(get_module_dir $subdir)
		;;
	VDPAU_HEADER)
		# already in vdpau-devel
		continue
		parseparams subdir
		install_file_only nvidia-devel %{_includedir}/%{drivername}/$subdir
		;;
	OPENGL_HEADER|CUDA_HEADER)
		parseparams subdir
		install_file_only nvidia-devel %{_includedir}/%{drivername}/$subdir
		;;
	ENCODEAPI_LIB|NVIFR_LIB)
		parseparams arch dest
		install_file nvidia $nvidia_libdir/$subdir
		;;
	ENCODEAPI_LIB_SYMLINK|NVIFR_LIB_SYMLINK)
		parseparams arch dest
		install_lib_symlink nvidia $nvidia_libdir
		;;
	DOCUMENTATION)
		parseparams subdir
		case $subdir in
		*/html)
			add_to_list nvidia-html "%%doc %{pkgname}/$file"
			continue
			;;
		*/include/*)
			continue
			;;
		esac
		case $file in
		*XF86Config*|*nvidia-settings.png)
			continue;;
		esac
		add_to_list nvidia "%%doc %{pkgname}/$file"
		;;
	MANPAGE|NVIDIA_MODPROBE_MANPAGE)
		parseparams subdir
		case "$file" in
		*nvidia-installer*)
			# not installed
			continue
			;;
		*nvidia-settings*|*nvidia-xconfig*|*nvidia-modprobe*|*nvidia-persistenced*)
%if !%simple
			# installed separately below
			continue
%endif
			;;
		*nvidia-smi*|*nvidia-cuda-mps-control*)
			# ok
			;;
		*)
			error_unhandled "skipped unknown man page $(basename $file)"
			continue
		esac
		install_file_only nvidia %{_mandir}/$subdir
		;;
	UTILITY_BINARY)
		case "$file" in
		*nvidia-settings|*nvidia-xconfig|*nvidia-persistenced)
%if !%simple
			# not installed, we install our own copy
			continue
%endif
			;;
		*nvidia-smi|*nvidia-bug-report.sh|*nvidia-debugdump)
       	    #ok
        	;;
        *nvidia-cuda-mps-control|*nvidia-cuda-mps-server)
			# ok
			;;
		*)
			error_unhandled "unknown binary $(basename $file) will be installed to %{nvidia_bindir}/$(basename $file)"
			;;
		esac
		install_file nvidia %{nvidia_bindir}
		;;
	UTILITY_BIN_SYMLINK)
		case $file in nvidia-uninstall) continue;; esac
		parseparams dest
		install_symlink nvidia %{nvidia_bindir}
		;;
    NVIDIA_MODPROBE)
    # A suid-root tool (GPLv2) used as fallback for loading the module and
	# creating the device nodes in case the driver component is running a
	# a non-root user (e.g. a CUDA application). While the module is automatically
	# loaded by udev rules, the device nodes are not automatically created
	# like with regular drivers and therefore this tool is installed on
	# distro as well, at least for now.
	# We install our self-compiled version in non-simple mode
%if %simple
	install_file nvidia %{nvidia_bindir}
%endif
		;;
	INSTALLER_BINARY)
		# not installed
		;;
	KERNEL_MODULE_SRC)
		install_file nvidia-dkms %{_usrsrc}/%{drivername}-%{version}-%{release}
		;;
	CUDA_ICD)
		# in theory this should go to the cuda subpackage, but it goes into the main package
		# as this avoids one broken symlink and it is small enough to not cause space issues
		install_file nvidia %{_sysconfdir}/%{drivername}
		;;
	APPLICATION_PROFILE)
		parseparams subdir
		# application profile filenames are versioned, we can use a common
		# non-alternativesized directory
		install_file nvidia %{_datadir}/nvidia/$subdir
		;;
	DOT_DESKTOP)
		# we provide our own for now
		;;
	UVM_MODULE_SRC)
		install_file nvidia-dkms %{_usrsrc}/%{drivername}-%{version}-%{release}/uvm
		;;
	*)
		error_unhandled "file $(basename $file) of unknown type $type will be skipped"
	esac
done

[ -z "$warnings" ] || echo "Please inform Anssi Hannula <anssi@mandriva.org> or http://qa.mandriva.com/ of the above warnings." >> warns.log

%if %simple
find %{buildroot}%{_libdir} %{buildroot}%{_prefix}/lib -type d | while read dir; do
	dir=${dir#%{buildroot}}
	echo "$dir" | grep -q nvidia && echo "%%dir $dir" >> nvidia.files
done
[ -d %{buildroot}%{_includedir}/%{drivername} ] && echo "%{_includedir}/%{drivername}" >> nvidia-devel.files

# for old releases in %%simple mode
if ! [ -e %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf ]; then
	install -m644 kernel/dkms.conf %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf
fi
%endif

%if !%simple
# confirm SONAME; if something else than libvdpau_nvidia.so or libvdpau_nvidia.so.1, adapt .spec as needed:
[ "$(objdump -p %{buildroot}%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version} | grep SONAME | gawk '{ print $2 }')" = "libvdpau_nvidia.so.1" ]

rm -f %{buildroot}%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.1
rm -f %{buildroot}%{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.1
%endif

# vdpau alternative symlink
install -d -m755 %{buildroot}%{_libdir}/vdpau
touch %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.1
%ifarch %{biarches}
install -d -m755 %{buildroot}%{_prefix}/lib/vdpau
touch %{buildroot}%{_prefix}/lib/vdpau/libvdpau_nvidia.so.1
%endif

%if !%simple
# self-built binaries
install -m755 ../nvidia-settings-%{version}/src/_out/*/nvidia-settings %{buildroot}%{nvidia_bindir}
install -m755 ../nvidia-xconfig-%{version}/_out/*/nvidia-xconfig %{buildroot}%{nvidia_bindir}
install -m755 ../nvidia-persistenced-%{version}/_out/*/nvidia-persistenced %{buildroot}%{nvidia_bindir}
install -m4755 ../nvidia-modprobe-%{version}/_out/*/nvidia-modprobe %{buildroot}%{nvidia_bindir}
%endif
# binary alternatives
install -d -m755 %{buildroot}%{_bindir}
touch %{buildroot}%{_bindir}/nvidia-settings
touch %{buildroot}%{_bindir}/nvidia-smi
touch %{buildroot}%{_bindir}/nvidia-debugdump
touch %{buildroot}%{_bindir}/nvidia-xconfig
touch %{buildroot}%{_bindir}/nvidia-bug-report.sh
touch %{buildroot}%{_bindir}/nvidia-modprobe
touch %{buildroot}%{_bindir}/nvidia-persistenced
touch %{buildroot}%{_bindir}/nvidia-cuda-mps-control
touch %{buildroot}%{_bindir}/nvidia-cuda-mps-server
# rpmlint:
chmod 0755 %{buildroot}%{_bindir}/*

%if !%simple
# install man pages
install -m755 ../nvidia-settings-%{version}/doc/_out/*/nvidia-settings.1 %{buildroot}%{_mandir}/man1
install -m755 ../nvidia-xconfig-%{version}/_out/*/nvidia-xconfig.1 %{buildroot}%{_mandir}/man1
install -m644 ../nvidia-modprobe-%{version}/_out/*/nvidia-modprobe.1 %{buildroot}%{_mandir}/man1
install -m644 ../nvidia-persistenced-%{version}/_out/*/nvidia-persistenced.1 %{buildroot}%{_mandir}/man1
%endif
# bug #41638 - whatis entries of nvidia man pages appear wrong
gunzip %{buildroot}%{_mandir}/man1/*.gz
sed -r -i '/^nvidia\\-[a-z]+ \\- NVIDIA/s,^nvidia\\-,nvidia-,' %{buildroot}%{_mandir}/man1/*.1
cd %{buildroot}%{_mandir}/man1
rename nvidia alt-%{drivername} *
cd -
touch %{buildroot}%{_mandir}/man1/nvidia-xconfig.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-settings.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-modprobe.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-persistenced.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-smi.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-cuda-mps-control.1%{_extension}

# cuda nvidia.icd
install -d -m755 %{buildroot}%{_sysconfdir}/OpenCL/vendors
touch %{buildroot}%{_sysconfdir}/OpenCL/vendors/nvidia.icd

# ld.so.conf
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
echo "%{nvidia_libdir}" > %{buildroot}%{_sysconfdir}/%{drivername}/ld.so.conf
%ifarch %{biarches}
echo "%{nvidia_libdir32}" >> %{buildroot}%{_sysconfdir}/%{drivername}/ld.so.conf
%endif

# modprobe.conf
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.d
touch %{buildroot}%{_sysconfdir}/modprobe.d/display-driver.conf
echo "install nvidia /sbin/modprobe %{modulename} \$CMDLINE_OPTS" > %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.conf

# xinit script
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
cat > %{buildroot}%{_sysconfdir}/%{drivername}/nvidia-settings.xinit <<EOF
# to be sourced
#
# Do not modify this file; the changes will be overwritten.
# If you want to disable automatic configuration loading, create
# /etc/sysconfig/nvidia-settings with this line: LOAD_NVIDIA_SETTINGS="no"
#
LOAD_NVIDIA_SETTINGS="yes"
[ -f %{_sysconfdir}/sysconfig/nvidia-settings ] && . %{_sysconfdir}/sysconfig/nvidia-settings
[ "\$LOAD_NVIDIA_SETTINGS" = "yes" ] && %{_bindir}/nvidia-settings --load-config-only
EOF
chmod 0755 %{buildroot}%{_sysconfdir}/%{drivername}/nvidia-settings.xinit
install -d -m755 %{buildroot}%{_sysconfdir}/X11/xinit.d
touch %{buildroot}%{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit

# install ldetect-lst pcitable files for backports
# local version of merge2pcitable.pl:read_nvidia_readme:
section="nothingyet"
set +x
[ -e README.txt ] || cp -a usr/share/doc/README.txt .
cat README.txt | while read line; do
	if [ "$section" = "nothingyet" ] || [ "$section" = "midspace" ]; then
		if echo "$line" | grep -Pq "^\s*NVIDIA GPU product\s+Device PCI ID"; then
			section="data"
		elif [ "$section" = "midspace" ] && echo "$line" | grep -Pq "legacy"; then
			break
		fi
		continue
	fi

	if [ "$section" = "data" ] && echo "$line" | grep -Pq "^\s*$"; then
		section="midspace"
		continue
	fi

	echo "$line" | grep -Pq "^\s*-+[\s-]+$" && continue
	id=$(echo "$line" | sed -nre 's,^\s*.+?\s\s+(0x)?([0-9a-fA-F]{4}).*$,\2,p' | tr '[:upper:]' '[:lower:]')
	#id2=$(echo "$line" | sed -nre 's,^\s*.+?\s\s+0x(....)\s0x(....).*$,\2,p' | tr '[:upper:]' '[:lower:]')
	subsysid=
	# not useful as of 2013-05 -Anssi
	#[ -n "$id2" ] && subsysid="	0x10de	0x$id2"
	echo "0x10de	0x$id$subsysid	\"Card:%{ldetect_cards_name}\""
done | sort -u > pcitable.nvidia.lst
set -x
[ $(wc -l pcitable.nvidia.lst | cut -f1 -d" ") -gt 200 ]
%if "%{ldetect_cards_name}" != ""
install -d -m755 %{buildroot}%{_datadir}/ldetect-lst/pcitable.d
gzip -c pcitable.nvidia.lst > %{buildroot}%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

export EXCLUDE_FROM_STRIP="$(find %{buildroot} -type f \! -name nvidia-settings \! -name nvidia-xconfig \! -name nvidia-modprobe \! -name nvidia-persistenced)"

%post -n %{driverpkgname}
# XFdrake used to generate an nvidia.conf file
[ -L %{_sysconfdir}/modprobe.d/nvidia.conf ] || rm -f %{_sysconfdir}/modprobe.d/nvidia.conf

current_glconf="$(readlink -e %{_sysconfdir}/ld.so.conf.d/GL.conf)"

# owned by libvdpau1, created in case libvdpau1 is installed only just after
# this package
mkdir -p %{_libdir}/vdpau

%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf %{priority} \
	--slave %{_mandir}/man1/nvidia-settings.1%{_extension} man_nvidiasettings%{_extension} %{_mandir}/man1/alt-%{drivername}-settings.1%{_extension} \
	--slave %{_mandir}/man1/nvidia-xconfig.1%{_extension} man_nvidiaxconfig%{_extension} %{_mandir}/man1/alt-%{drivername}-xconfig.1%{_extension} \
	--slave %{_mandir}/man1/nvidia-smi.1%{_extension} nvidia-smi.1%{_extension} %{_mandir}/man1/alt-%{drivername}-smi.1%{_extension} \
	--slave %{_mandir}/man1/nvidia-cuda-mps-control.1%{_extension} nvidia-cuda-mps-control.1%{_extension} %{_mandir}/man1/alt-%{drivername}-cuda-mps-control.1%{_extension} \
	--slave %{_datadir}/applications/%{disttag}-nvidia-settings.desktop nvidia_desktop %{_datadir}/%{drivername}/%{disttag}-nvidia-settings.desktop \
	--slave %{_bindir}/nvidia-settings nvidia_settings %{nvidia_bindir}/nvidia-settings \
	--slave %{_bindir}/nvidia-smi nvidia_smi %{nvidia_bindir}/nvidia-smi \
	--slave %{_bindir}/nvidia-debugdump nvidia_debugdump %{nvidia_bindir}/nvidia-debugdump \
	--slave %{_bindir}/nvidia-xconfig nvidia_xconfig %{nvidia_bindir}/nvidia-xconfig \
	--slave %{_bindir}/nvidia-bug-report.sh nvidia_bug_report %{nvidia_bindir}/nvidia-bug-report.sh \
	--slave %{_bindir}/nvidia-cuda-mps-control nvidia-cuda-mps-control %{nvidia_bindir}/nvidia-cuda-mps-control \
	--slave %{_bindir}/nvidia-cuda-mps-server nvidia-cuda-mps-server %{nvidia_bindir}/nvidia-cuda-mps-server \
	--slave %{_bindir}/nvidia-modprobe nvidia-modprobe %{nvidia_bindir}/nvidia-modprobe \
	--slave %{_bindir}/nvidia-persistenced nvidia-persistenced %{nvidia_bindir}/nvidia-persistenced \
	--slave %{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit nvidia-settings.xinit %{_sysconfdir}/%{drivername}/nvidia-settings.xinit \
	--slave %{_libdir}/vdpau/libvdpau_nvidia.so.1 %{_lib}vdpau_nvidia.so.1 %{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version} \
	--slave %{_sysconfdir}/modprobe.d/display-driver.conf display-driver.conf %{_sysconfdir}/%{drivername}/modprobe.conf \
	--slave %{_sysconfdir}/OpenCL/vendors/nvidia.icd nvidia.icd %{_sysconfdir}/%{drivername}/nvidia.icd \
%ifarch %{biarches}
	--slave %{_prefix}/lib/vdpau/libvdpau_nvidia.so.1 libvdpau_nvidia.so.1 %{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.%{version} \
%endif
	--slave %{xorg_extra_modules} xorg_extra_modules %{nvidia_extensionsdir} \

if [ "${current_glconf}" = "%{_sysconfdir}/nvidia97xx/ld.so.conf" ]; then
	# Adapt for the renaming of the driver. X.org config still has the old ModulePaths
	# but they do not matter as we are using alternatives for libglx.so now.
	%{_sbindir}/update-alternatives --set gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf
fi
# explicit /sbin/ldconfig due to alternatives
/sbin/ldconfig -X

%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%postun -n %{driverpkgname}
if [ ! -f %{_sysconfdir}/%{drivername}/ld.so.conf ]; then
  %{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf
fi
# explicit /sbin/ldconfig due to alternatives
/sbin/ldconfig -X

%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%post -n %{drivername}-cuda-opencl
# explicit /sbin/ldconfig due to a non-standard library directory
/sbin/ldconfig -X

%post -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade add -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade build -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade install -m %{drivername} -v %{version}-%{release} --force

# rmmod any old driver if present and not in use (e.g. by X)
rmmod nvidia > /dev/null 2>&1 || true

%preun -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{drivername} -v %{version}-%{release} --all

# rmmod any old driver if present and not in use (e.g. by X)
rmmod nvidia > /dev/null 2>&1 || true

%files -n %{driverpkgname} -f %{pkgname}/nvidia.files
%defattr(-,root,root)
# other documentation files are listed in nvidia.files
%doc README.install.urpmi README.manual-setup

%if "%{ldetect_cards_name}" != ""
%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

# ld.so.conf, modprobe.conf, xinit
%ghost %{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit
%ghost %{_sysconfdir}/modprobe.d/display-driver.conf
%dir %{_sysconfdir}/%{drivername}
%{_sysconfdir}/%{drivername}/modprobe.conf
%{_sysconfdir}/%{drivername}/ld.so.conf
%{_sysconfdir}/%{drivername}/nvidia-settings.xinit
%if !%simple
%{_sysconfdir}/%{drivername}/nvidia.icd
%dir %{_datadir}/nvidia
%{_datadir}/nvidia/nvidia-application-profiles-%{version}-rc
%{_datadir}/nvidia/nvidia-application-profiles-%{version}-key-documentation
%{_datadir}/nvidia/monitoring.conf
%{_datadir}/nvidia/pci.ids
%endif

%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%ghost %{_sysconfdir}/OpenCL/vendors/nvidia.icd

%ghost %{_bindir}/nvidia-settings
%ghost %{_bindir}/nvidia-smi
%ghost %{_bindir}/nvidia-debugdump
%ghost %{_bindir}/nvidia-xconfig
%ghost %{_bindir}/nvidia-modprobe
%ghost %{_bindir}/nvidia-persistenced
%ghost %{_bindir}/nvidia-bug-report.sh
%ghost %{_bindir}/nvidia-cuda-mps-control
%ghost %{_bindir}/nvidia-cuda-mps-server
%if !%simple
%dir %{nvidia_bindir}
%{nvidia_bindir}/nvidia-settings
%{nvidia_bindir}/nvidia-smi
%{nvidia_bindir}/nvidia-debugdump
%{nvidia_bindir}/nvidia-xconfig
%{nvidia_bindir}/nvidia-modprobe
%{nvidia_bindir}/nvidia-persistenced
%{nvidia_bindir}/nvidia-bug-report.sh
%{nvidia_bindir}/nvidia-cuda-mps-control
%{nvidia_bindir}/nvidia-cuda-mps-server
%endif

%ghost %{_mandir}/man1/nvidia-xconfig.1%{_extension}
%ghost %{_mandir}/man1/nvidia-settings.1%{_extension}
%ghost %{_mandir}/man1/nvidia-modprobe.1%{_extension}
%ghost %{_mandir}/man1/nvidia-persistenced.1%{_extension}
%ghost %{_mandir}/man1/nvidia-smi.1%{_extension}
%ghost %{_mandir}/man1/nvidia-cuda-mps-control.1%{_extension}
%if !%simple
%{_mandir}/man1/alt-%{drivername}-xconfig.1*
%{_mandir}/man1/alt-%{drivername}-settings.1*
%{_mandir}/man1/alt-%{drivername}-modprobe.1*
%{_mandir}/man1/alt-%{drivername}-persistenced.1*
%{_mandir}/man1/alt-%{drivername}-smi.1*
%{_mandir}/man1/alt-%{drivername}-cuda-mps-control.1*
%else
%{_mandir}/man1/alt-%{drivername}-*
%endif

%ghost %{_datadir}/applications/%{disttag}-nvidia-settings.desktop
%dir %{_datadir}/%{drivername}
%{_datadir}/%{drivername}/%{disttag}-nvidia-settings.desktop

%if !%simple
%{_iconsdir}/hicolor/16x16/apps/%{drivername}-settings.png
%{_iconsdir}/hicolor/32x32/apps/%{drivername}-settings.png
%endif
%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png

%if !%simple
%dir %{nvidia_libdir}
%dir %{nvidia_libdir}/tls
%dir %{nvidia_libdir}/vdpau
%{nvidia_libdir}/libGL.so.%{version}
%{nvidia_libdir}/libEGL.so.%{version}
%{nvidia_libdir}/libGLESv*.%{version}
%{nvidia_libdir}/libnvidia-eglcore.so.%{version}
%{nvidia_libdir}/libnvidia-glsi.so.%{version}
%{nvidia_libdir}/libnvidia-glcore.so.%{version}
%{nvidia_libdir}/libnvidia-cfg.so.%{version}
%{nvidia_libdir}/libnvidia-fbc.so.%{version}
%{nvidia_libdir}/libnvidia-ifr.so.%{version}
%{nvidia_libdir}/libnvidia-ml.so.%{version}
%{nvidia_libdir}/libnvidia-tls.so.%{version}
%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%{nvidia_libdir}/libGL.so.1
%{nvidia_libdir}/libEGL.so.1
%{nvidia_libdir}/libGLESv*.so.1
%{nvidia_libdir}/libGLESv*.so.2
%{nvidia_libdir}/libnvidia-cfg.so.1
%{nvidia_libdir}/libnvidia-fbc.so.1
%{nvidia_libdir}/libnvidia-ifr.so.1
%{nvidia_libdir}/libnvidia-ml.so.1
%{nvidia_libdir}/libvdpau_nvidia.so
%{nvidia_libdir}/tls/libnvidia-tls.so.%{version}
# %simple
%endif

%ghost %{_libdir}/vdpau/libvdpau_nvidia.so.1
%ifarch %{biarches}
# avoid unowned directory
%dir %{_prefix}/lib/vdpau
%ghost %{_prefix}/lib/vdpau/libvdpau_nvidia.so.1
%endif

%if !%simple
# 2009.1+ (/usr/lib/drivername/xorg)
%dir %{nvidia_modulesdir}
%{nvidia_modulesdir}/libnvidia-wfb.so.1
%endif

%if !%simple
%{nvidia_modulesdir}/libnvidia-wfb.so.%{version}
%endif

%if !%simple
%{nvidia_extensionsdir}/libglx.so.%{version}
%{nvidia_extensionsdir}/libglx.so
%endif

%if !%simple
%{nvidia_driversdir}/nvidia_drv.so
%endif

%ifarch %{biarches}
%files -n %{driverpkgname}-32bit
%dir %{nvidia_libdir32}
%dir %{nvidia_libdir32}/tls
%dir %{nvidia_libdir32}/vdpau
%{nvidia_libdir32}/libGL.so.%{version}
%{nvidia_libdir32}/libEGL.so.%{version}
%{nvidia_libdir32}/libGLESv*.%{version}
%{nvidia_libdir32}/libnvidia-glcore.so.%{version}
%{nvidia_libdir32}/libnvidia-eglcore.so.%{version}
%{nvidia_libdir32}/libnvidia-glsi.so.%{version}
%{nvidia_libdir32}/libnvidia-tls.so.%{version}
%{nvidia_libdir32}/libvdpau_nvidia.so
%{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.%{version}
%{nvidia_libdir32}/libnvidia-ml.so.%{version}
%{nvidia_libdir32}/libnvidia-ml.so.1
%{nvidia_libdir32}/libnvidia-ifr.so.%{version}
%{nvidia_libdir32}/libnvidia-ifr.so.1
%{nvidia_libdir32}/libnvidia-fbc.so.%{version}
%{nvidia_libdir32}/libnvidia-fbc.so.1
%{nvidia_libdir32}/libGL.so.1
%{nvidia_libdir32}/libEGL.so.1
%{nvidia_libdir32}/libGLESv*.so.1
%{nvidia_libdir32}/libGLESv*.so.2
%{nvidia_libdir32}/tls/libnvidia-tls.so.%{version}
%endif

%files -n %{drivername}-devel -f %pkgname/nvidia-devel.files
%defattr(-,root,root)
%if !%simple
%{_includedir}/%{drivername}
%{nvidia_libdir}/libGL.so
%{nvidia_libdir}/libEGL.so
%{nvidia_libdir}/libGLESv*.so
%{nvidia_libdir}/libcuda.so
%{nvidia_libdir}/libnvcuvid.so
%{nvidia_libdir}/libnvidia-cfg.so
%{nvidia_libdir}/libnvidia-fbc.so
%{nvidia_libdir}/libnvidia-ifr.so
%{nvidia_libdir}/libnvidia-ml.so
%{nvidia_libdir}/libOpenCL.so
%{nvidia_libdir}/libnvidia-encode.so
%ifarch %{biarches}
%{nvidia_libdir32}/libGL.so
%{nvidia_libdir32}/libEGL.so
%{nvidia_libdir32}/libGLESv*.so
%{nvidia_libdir32}/libcuda.so
%{nvidia_libdir32}/libOpenCL.so
%{nvidia_libdir32}/libnvidia-ml.so
%{nvidia_libdir32}/libnvidia-fbc.so
%{nvidia_libdir32}/libnvidia-ifr.so
%{nvidia_libdir32}/libnvcuvid.so
%{nvidia_libdir32}/libnvidia-encode.so
%endif
%endif

%files -n dkms-%{drivername}
%defattr(-,root,root)
%doc %{pkgname}/LICENSE
%{_usrsrc}/%{drivername}-%{version}-%{release}

%files -n %{drivername}-doc-html -f %pkgname/nvidia-html.files
%defattr(-,root,root)

%files -n %{drivername}-cuda-opencl -f %pkgname/nvidia-cuda.files
%defattr(-,root,root)
%if !%simple
%{nvidia_libdir}/libOpenCL.so.1.0.0
%{nvidia_libdir}/libOpenCL.so.1.0
%{nvidia_libdir}/libOpenCL.so.1
%{nvidia_libdir}/libnvidia-compiler.so.%{version}
%{nvidia_libdir}/libcuda.so.%{version}
%{nvidia_libdir}/libcuda.so.1
%{nvidia_libdir}/libnvidia-opencl.so.%{version}
%{nvidia_libdir}/libnvidia-opencl.so.1
%{nvidia_libdir}/libnvidia-encode.so.%{version}
%{nvidia_libdir}/libnvidia-encode.so.1
%{nvidia_libdir}/libnvcuvid.so.%{version}
%{nvidia_libdir}/libnvcuvid.so.1
%ifarch %{biarches}
%{nvidia_libdir32}/libOpenCL.so.1.0.0
%{nvidia_libdir32}/libOpenCL.so.1.0
%{nvidia_libdir32}/libOpenCL.so.1
%{nvidia_libdir32}/libnvidia-compiler.so.%{version}
%{nvidia_libdir32}/libnvidia-opencl.so.%{version}
%{nvidia_libdir32}/libnvidia-opencl.so.1
%{nvidia_libdir32}/libnvidia-encode.so.%{version}
%{nvidia_libdir32}/libnvidia-encode.so.1
%{nvidia_libdir32}/libnvcuvid.so.%{version}
%{nvidia_libdir32}/libnvcuvid.so.1
%{nvidia_libdir32}/libcuda.so.%{version}
%{nvidia_libdir32}/libcuda.so.1
%endif
%endif
