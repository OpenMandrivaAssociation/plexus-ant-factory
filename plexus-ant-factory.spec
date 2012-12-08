# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:
  %{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:
  %{_gcj_support}}%{!?_gcj_support:0}}}

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define without_maven 1
%define with_maven 0

%define parent plexus
%define subname ant-factory

Name:           %{parent}-%{subname}
Version:        1.0
Release:        0.1.a1.2jpp.2.7
Epoch:          0
Summary:        Plexus Ant component factory
License:        MIT-Style
Group:          Development/Java
URL:            http://plexus.codehaus.org/
Source0:        %{name}-src.tar.gz
# svn export svn://svn.plexus.codehaus.org/plexus/tags/
#            plexus-ant-factory-1.0-alpha-1 plexus-ant-factory/
# tar czf plexus-ant-factory-src.tar.gz plexus-ant-factory/
Source1:        %{name}-jpp-depmap.xml
Source2:        %{name}-build.xml

%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRequires:  java-rpmbuild >= 0:1.7.2
%if %{with_maven}
BuildRequires:    maven2 >= 2.0.4-9
BuildRequires:    maven2-plugin-compiler
BuildRequires:    maven2-plugin-install
BuildRequires:    maven2-plugin-jar
BuildRequires:    maven2-plugin-javadoc
BuildRequires:    maven2-plugin-release
BuildRequires:    maven2-plugin-resources
BuildRequires:    maven2-plugin-surefire
BuildRequires:    maven2-common-poms >= 1.0-2
%endif
BuildRequires:    ant
BuildRequires:    classworlds
BuildRequires:    plexus-container-default
BuildRequires:    plexus-utils

Requires:    ant
Requires:    classworlds
Requires:    plexus-container-default
Requires:    plexus-utils

Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%if %{gcj_support}
BuildRequires:       java-gcj-compat-devel
%endif

%description
Ant component class creator for Plexus.

%if %{with_maven}
%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.
%endif

%prep
%setup -q -n %{name}

%if %{without_maven}
    cp -p %{SOURCE2} build.xml
%endif


%build
%if %{with_maven}
    export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
    mkdir -p $MAVEN_REPO_LOCAL

    mvn-jpp \
        -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc

%else

    mkdir lib
    build-jar-repository \
                             -s -p \
                            lib ant ant-launcher \
                            classworlds \
                            plexus/container-default \
                            plexus/utils
    %{ant} -Dmaven.mode.offline=true

%endif

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 target/*.jar \
      $RPM_BUILD_ROOT%{_javadir}/%{parent}/%{subname}-%{version}.jar
%add_to_maven_depmap org.codehaus.plexus %{name} 1.0-alpha-1 JPP/%{parent} %{subname}

(cd $RPM_BUILD_ROOT%{_javadir}/%{parent} && for jar in *-%{version}*; \
  do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# pom
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 pom.xml \
          $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{parent}-%{subname}.pom

# javadoc
%if %{with_maven}
    install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

    cp -pr target/site/apidocs/* \
        $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/

    ln -s %{name}-%{version} \
                $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif
%update_maven_depmap

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif
%update_maven_depmap

%files
%{_javadir}/plexus
%{_datadir}/maven2
%config(noreplace) %{_mavendepmapfragdir}/*

%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%{_libdir}/gcj/%{name}/ant-factory-1.0.jar.*
%endif

%if %{with_maven}
%files javadoc
%doc %{_javadocdir}/*
%endif


%changelog
* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.0-0.1.a1.2jpp.2.6mdv2011.0
+ Revision: 607180
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.0-0.1.a1.2jpp.2.5mdv2010.1
+ Revision: 523666
- rebuilt for 2010.1

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:1.0-0.1.a1.2jpp.2.4mdv2010.0
+ Revision: 426729
- rebuild

* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 0:1.0-0.1.a1.2jpp.2.3mdv2009.0
+ Revision: 140733
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.0-0.1.a1.2jpp.2.3mdv2008.1
+ Revision: 120996
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.0-0.1.a1.2jpp.2.2mdv2008.0
+ Revision: 87282
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Wed Jul 04 2007 David Walluck <walluck@mandriva.org> 0:1.0-0.1.a1.2jpp.2.1mdv2008.0
+ Revision: 47869
- Import plexus-ant-factory




* Tue Mar 20 2007 Deepak Bhole <dbhole@redhat.com> 1.0-0.1.a1.2jpp.2
- Build with maven

* Fri Feb 23 2007 Tania Bento <tbento@redhat.com> 0:1.0-0.1.a1.2jpp.1
- Fixed %%Release.
- Fixed %%BuildRoot.
- Removed %%Vendor.
- Removed %%Distribution.
- Removed %%post and %%postun sections for javadoc.
- Defined _with_gcj_supoprt and _gcj_support.
- Changed to use cp -p to preserve timestamps.

* Tue Oct 17 2006 Deepak Bhole <dbhole@redhat.com> 1.0-0.a1.2jpp
- Update for maven2 9jpp.

* Thu Sep 07 2006 Deepak Bhole <dbhole@redhat.com> 1.0-0.a1.1jpp
- Initial build
