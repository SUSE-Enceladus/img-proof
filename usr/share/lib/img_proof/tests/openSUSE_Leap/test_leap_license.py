import pytest


def test_leap_license(confirm_license_content):
    license_dirs = [
        '/etc/YaST2/licenses/base/',
        '/usr/share/licenses/openSUSE-release/'
    ]
    license_content = [
        'LICENSE AGREEMENT'
    ]
    result = confirm_license_content(license_dirs, license_content)

    if result is False:
        pytest.fail(
            'SUSE End User License Agreement not found '
            'or license has incorrect content.'
        )
