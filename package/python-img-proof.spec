#
# spec file for package python-img-proof
#
# Copyright (c) 2020 SUSE LLC
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
%define python python
%{?sle15_python_module_pythons}
%bcond_without test

%if 0%{?suse_version} > 1500
%bcond_without libalternatives
%else
%bcond_with libalternatives
%endif

Name:           python-img-proof
Version:        7.32.0
Release:        0
Summary:        Command line and API for testing custom images
License:        GPL-3.0-or-later
Group:          Development/Languages/Python
URL:            https://github.com/SUSE-Enceladus/img-proof
Source:         https://files.pythonhosted.org/packages/source/i/img-proof/img-proof-%{version}.tar.gz
BuildRequires:  python-rpm-macros
BuildRequires:  fdupes
BuildRequires:  %{python_module PyYAML}
BuildRequires:  %{python_module aliyun-python-sdk-core}
BuildRequires:  %{python_module aliyun-python-sdk-ecs}
BuildRequires:  %{python_module msrestazure >= 0.6.0}
BuildRequires:  %{python_module azure-identity}
BuildRequires:  %{python_module azure-mgmt-compute}
BuildRequires:  %{python_module azure-mgmt-network}
BuildRequires:  %{python_module azure-mgmt-resource}
BuildRequires:  %{python_module boto3}
BuildRequires:  %{python_module click}
BuildRequires:  %{python_module click-man}
BuildRequires:  %{python_module devel}
BuildRequires:  %{python_module google-api-python-client}
BuildRequires:  %{python_module google-auth}
BuildRequires:  %{python_module oci-sdk}
BuildRequires:  %{python_module paramiko}
BuildRequires:  %{python_module pytest}
BuildRequires:  %{python_module pip}
BuildRequires:  %{python_module setuptools}
BuildRequires:  %{python_module wheel}
BuildRequires:  %{python_module pytest-testinfra}
BuildRequires:  %{python_module pytest-json-report}
Requires:       python-PyYAML
Requires:       python-aliyun-python-sdk-core
Requires:       python-aliyun-python-sdk-ecs
Requires:       python-msrestazure >= 0.6.0
Requires:       python-azure-identity
Requires:       python-azure-mgmt-compute
Requires:       python-azure-mgmt-network
Requires:       python-azure-mgmt-resource
Requires:       python-boto3
Requires:       python-click
Requires:       python-google-api-python-client
Requires:       python-google-auth
Requires:       python-oci-sdk
Requires:       python-paramiko
Requires:       python-pytest
Requires:       python-pytest-testinfra
Requires:       python-pytest-json-report

%if %{with libalternatives}
BuildRequires:  alts
Requires:       alts
%else
Requires(post): update-alternatives
Requires(postun): update-alternatives
%endif

BuildArch:      noarch
Obsoletes:      python3-ipa < 7.24.0
Provides:       python3-img-proof = %{version}
Obsoletes:      python3-img-proof < %{version}
%python_subpackages

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
%setup -q -n img-proof-%{version}

%build
%pyproject_wheel
mkdir -p man/man1
python3.11 setup.py --command-packages=click_man.commands man_pages --target man/man1

%install
%pyproject_install
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/*.1 %{buildroot}/%{_mandir}/man1

install -d -m 755 %{buildroot}%{_prefix}
cp -r usr/* %{buildroot}%{_prefix}/

%python_clone -a %{buildroot}%{_bindir}/img-proof
%{python_expand %fdupes %{buildroot}%{$python_sitelib}}

%check
%if %{with test}
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
%pytest --ignore=data --ignore=usr
%endif

%pre
%python_libalternatives_reset_alternative img-proof

%post
%{python_install_alternative img-proof}

%postun
%{python_uninstall_alternative img-proof}

%files %{python_files}
%defattr(-,root,root)
%license LICENSE
%doc CHANGES.md CONTRIBUTING.md README.md
%{_mandir}/man1/*
%python_alternative %{_bindir}/img-proof
%{python_sitelib}/*

%files %{python_files}-tests
%defattr(-,root,root)
%dir %{_datadir}/lib
%dir %{_datadir}/lib/img_proof
%{_datadir}/lib/img_proof/*

%changelog

