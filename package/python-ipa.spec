#
# spec file for package python-ipa
#
# Copyright (c) 2017 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%{?!python_module:%define python_module() python-%{**} python3-%{**}}
%define skip_python2 1
%bcond_without test
Name:           python-ipa
Version:        0.0.1
Release:        0
Summary:        Command line and API for testing custom images
License:        GPL-3.0+
Group:          Development/Languages/Python
Url:            https://github.com/SUSE/ipa
Source:         ipa-%{version}.tar.gz
BuildRequires:  fdupes
BuildRequires:  python-rpm-macros
BuildRequires:  %{python_module devel}
BuildRequires:  %{python_module setuptools}
%if %{with test}
BuildRequires:  %{python_module azurectl >= 3.0.1}
BuildRequires:  %{python_module boto3}
BuildRequires:  %{python_module click}
BuildRequires:  %{python_module coverage}
BuildRequires:  %{python_module flake8}
BuildRequires:  %{python_module paramiko}
BuildRequires:  %{python_module pytest}
BuildRequires:  %{python_module pytest-cov}
BuildRequires:  %{python_module PyYAML}
BuildRequires:  %{python_module testinfra}
BuildRequires:  %{python_module vcrpy}
%endif
Requires:       python-azurectl >= 3.0.1
Requires:       python-boto3
Requires:       python-click
Requires:       python-paramiko
Requires:       python-pytest
Requires:       python-PyYAML
Requires:       python-testinfra
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%python_subpackages

%description
ipa provides a command line utility to test images in
the Public Cloud (AWS, Azure, GCE, etc.).

%prep
%setup -q -n ipa-%{version}

%build
%python_build

%install
%python_install
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/*.1 %{buildroot}/%{_mandir}/man1
%python_expand %fdupes %{buildroot}%{$python_sitelib}/ipa

%check
%if %{with test}
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
%python_exec -m pytest --cov=ipa
%endif

%files %{python_files}
%defattr(-,root,root)
%doc CHANGES.asciidoc CONTRIBUTING.asciidoc LICENSE README.asciidoc
%python3_only %doc %{_mandir}/man1/*
%python3_only %{_bindir}/ipa
%{python_sitelib}/*

%changelog
