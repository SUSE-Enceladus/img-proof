#
# spec file for package python-img-proof
#
# Copyright (c) 2025 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

%define upstream_name img-proof
%if 0%{?suse_version} >= 1600
%define pythons %{primary_python}
%else
%{?sle15_python_module_pythons}
%endif
%global _sitelibdir %{%{pythons}_sitelib}

Name:           python-img-proof
Version:        8.1.0
Release:        0
Summary:        Command line and API for testing custom images
License:        GPL-3.0-or-later
Group:          Development/Languages/Python
URL:            https://github.com/SUSE-Enceladus/%{upstream_name}
Source:         https://files.pythonhosted.org/packages/source/i/%{upstream_name}/%{upstream_name}-%{version}.tar.gz
BuildRequires:  python-rpm-macros
BuildRequires:  fdupes
BuildRequires:  %{pythons}-PyYAML
BuildRequires:  %{pythons}-aliyun-python-sdk-core
BuildRequires:  %{pythons}-aliyun-python-sdk-ecs
BuildRequires:  %{pythons}-msrestazure >= 0.6.0
BuildRequires:  %{pythons}-azure-identity
BuildRequires:  %{pythons}-azure-mgmt-compute
BuildRequires:  %{pythons}-azure-mgmt-network
BuildRequires:  %{pythons}-azure-mgmt-resource
BuildRequires:  %{pythons}-boto3
BuildRequires:  %{pythons}-click
BuildRequires:  %{pythons}-devel
BuildRequires:  %{pythons}-google-cloud-compute >= 1.21.0
BuildRequires:  %{pythons}-google-auth
BuildRequires:  %{pythons}-oci-sdk
BuildRequires:  %{pythons}-paramiko
BuildRequires:  %{pythons}-pytest
BuildRequires:  %{pythons}-pip
BuildRequires:  %{pythons}-setuptools
BuildRequires:  %{pythons}-wheel
BuildRequires:  %{pythons}-pytest-testinfra
BuildRequires:  %{pythons}-pytest-json-report
Requires:       %{pythons}-PyYAML
Requires:       %{pythons}-aliyun-python-sdk-core
Requires:       %{pythons}-aliyun-python-sdk-ecs
Requires:       %{pythons}-msrestazure >= 0.6.0
Requires:       %{pythons}-azure-identity
Requires:       %{pythons}-azure-mgmt-compute
Requires:       %{pythons}-azure-mgmt-network
Requires:       %{pythons}-azure-mgmt-resource
Requires:       %{pythons}-boto3
Requires:       %{pythons}-click
Requires:       %{pythons}-google-cloud-compute >= 1.21.0
Requires:       %{pythons}-google-auth
Requires:       %{pythons}-oci-sdk
Requires:       %{pythons}-paramiko
Requires:       %{pythons}-pytest
Requires:       %{pythons}-pytest-testinfra
Requires:       %{pythons}-pytest-json-report

BuildArch:      noarch
Obsoletes:      python3-ipa < 7.24.0
Provides:       python3-img-proof = %{version}
Obsoletes:      python3-img-proof < %{version}

%description
img-proof provides a command line utility to test images in
the Public Cloud (AWS, Azure, GCE, etc.).

%package tests
Summary:        Infrastructure tests for img-proof
Group:          Development/Languages/Python
Requires:       python-susepubliccloudinfo
PreReq:         python-img-proof = %{version}
Obsoletes:      python3-ipa-tests < 7.24.0

%description tests
Directory of infrastructure tests for testing images.

%prep
%setup -q -n %{upstream_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/*.1 %{buildroot}/%{_mandir}/man1

install -d -m 755 %{buildroot}%{_prefix}
cp -r usr/* %{buildroot}%{_prefix}/

%fdupes %{buildroot}%{_sitelibdir}

%check
%if %{with test}
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
%pytest --ignore=data --ignore=usr
%endif

%files
%defattr(-,root,root)
%license LICENSE
%doc CHANGES.md CONTRIBUTING.md README.md
%{_mandir}/man1/img-proof-list.1%{?ext_man}
%{_mandir}/man1/img-proof-results-archive.1%{?ext_man}
%{_mandir}/man1/img-proof-results-clear.1%{?ext_man}
%{_mandir}/man1/img-proof-results-delete.1%{?ext_man}
%{_mandir}/man1/img-proof-results-list.1%{?ext_man}
%{_mandir}/man1/img-proof-results-show.1%{?ext_man}
%{_mandir}/man1/img-proof-results.1%{?ext_man}
%{_mandir}/man1/img-proof-test.1%{?ext_man}
%{_mandir}/man1/img-proof.1%{?ext_man}
%{_bindir}/img-proof
%{_sitelibdir}/img_proof/
%{_sitelibdir}/img_proof-*.dist-info/

%files tests
%defattr(-,root,root)
%dir %{_datadir}/lib
%dir %{_datadir}/lib/img_proof
%{_datadir}/lib/img_proof/*

%changelog
