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

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define parent plexus
%define subname ant-factory

Name:           %{parent}-%{subname}
Version:        1.0
Release:        0.5.a2.1.4
Summary:        Plexus Ant component factory
# Email from copyright holder confirms license.
License:        ASL 2.0
Group:          Development/Java
URL:            http://plexus.codehaus.org/
Source0:        %{name}-src.tar.bz2
# svn export http://svn.codehaus.org/plexus/tags/plexus-ant-factory-1.0-alpha-2.1/ plexus-ant-factory/
# tar cjf plexus-ant-factory-src.tar.bz2 plexus-ant-factory/
Source1:        %{name}-jpp-depmap.xml
Source2:        %{name}-build.xml
Source3:	plexus-ant-factory_license_and_copyright.txt

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:  jpackage-utils >= 0:1.7.2
%if %{with_maven}
BuildRequires:    maven2 >= 2.0.4-9
BuildRequires:    maven2-plugin-compiler
BuildRequires:    maven2-plugin-install
BuildRequires:    maven2-plugin-jar
BuildRequires:    maven2-plugin-javadoc
BuildRequires:    maven2-plugin-resources
BuildRequires:    maven-surefire-maven-plugin
BuildRequires:    maven-surefire-provider-junit
BuildRequires:    maven-doxia-sitetools
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

%description
Ant component class creator for Plexus.

%if %{with_maven}
%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
# for /bin/rm and /bin/ls
Requires(pre):    coreutils
Requires(post):   coreutils

%description javadoc
Javadoc for %{name}.
%endif

%prep
%setup -q -n %{name}
cp %{SOURCE3} .

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
    ant -Dmaven.mode.offline=true

%endif

%install
rm -rf %{buildroot}
# jars
install -d -m 755 %{buildroot}%{_javadir}/plexus
install -pm 644 target/*.jar \
      %{buildroot}%{_javadir}/%{parent}/%{subname}-%{version}.jar
%add_to_maven_depmap org.codehaus.plexus %{name} 1.0-alpha-1 JPP/%{parent} %{subname}

(cd %{buildroot}%{_javadir}/%{parent} && for jar in *-%{version}*; \
  do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# pom
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 pom.xml \
          %{buildroot}%{_datadir}/maven2/poms/JPP.%{parent}-%{subname}.pom

# javadoc
%if %{with_maven}
    install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}

    cp -pr target/site/apidocs/* \
        %{buildroot}%{_javadocdir}/%{name}-%{version}/

    ln -s %{name}-%{version} \
                %{buildroot}%{_javadocdir}/%{name} # ghost symlink
%endif

%clean
rm -rf %{buildroot}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc plexus-ant-factory_license_and_copyright.txt
%dir %{_javadir}/plexus
%{_javadir}/plexus
%{_datadir}/maven2
%{_mavendepmapfragdir}

%if %{with_maven}
%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*
%endif


