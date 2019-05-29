import pytest


def test_sles_license(host, confirm_sles_license_content):
    license_dirs = [
        '/etc/YaST2/licenses/base/',
        '/etc/YaST2/licenses/SLES/',
        '/usr/share/licenses/product/base/',
        '/usr/share/licenses/product/SLES/'
    ]
    result = confirm_sles_license_content(license_dirs)

    if result is False:
        pytest.fail(
            'SUSE End User License Agreement not found '
            'or license has incorrect content.'
        )
