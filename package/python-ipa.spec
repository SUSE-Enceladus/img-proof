#
# spec file for package python3-ipa
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

%bcond_without test
Name:           python3-ipa
Version:        0.1.1
Release:        0
Summary:        Command line and API for testing custom images
License:        GPL-3.0+
Group:          Development/Languages/Python
Url:            https://github.com/SUSE/ipa
Source:         ipa-%{version}.tar.gz
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%if %{with test}
BuildRequires:  python3-apache-libcloud
BuildRequires:  python3-azurectl >= 3.0.1
BuildRequires:  python3-boto3
BuildRequires:  python3-click
BuildRequires:  python3-coverage
BuildRequires:  python3-cryptography
BuildRequires:  python3-paramiko
BuildRequires:  python3-pycrypto
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-cov
BuildRequires:  python3-PyYAML
BuildRequires:  python3-testinfra
BuildRequires:  python3-vcrpy
%endif
Requires:       python3-apache-libcloud
Requires:       python3-azurectl >= 3.0.1
Requires:       python3-boto3
Requires:       python3-click
Requires:       python3-cryptography
Requires:       python3-paramiko
Requires:       python3-pycrypto
Requires:       python3-pytest
Requires:       python3-PyYAML
Requires:       python3-testinfra
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
ipa provides a command line utility to test images in
the Public Cloud (AWS, Azure, GCE, etc.).

%prep
%setup -q -n ipa-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}
install -d -m 755 %{buildroot}/%{_mandir}/man1
install -m 644 man/man1/*.1 %{buildroot}/%{_mandir}/man1

%check
%if %{with test}
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
python3 -m pytest --cov=ipa --ignore=tests/data
%endif

%files
%defattr(-,root,root)
%doc CHANGES.asciidoc CONTRIBUTING.asciidoc LICENSE README.asciidoc
%doc %{_mandir}/man1/*
%{_bindir}/ipa
%{python3_sitelib}/*

%changelog
