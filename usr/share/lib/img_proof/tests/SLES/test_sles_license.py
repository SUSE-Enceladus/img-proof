import pytest


def test_sles_license(confirm_license_content):
    license_dirs = [
        '/etc/YaST2/licenses/base/',
        '/etc/YaST2/licenses/SLES/',
        '/usr/share/licenses/product/base/',
        '/usr/share/licenses/product/SLES/'
    ]
    license_content = [
        'SUSE End User License Agreement',
        'SUSE(R) Linux Enterprise End User License Agreement',
        'SUSE® Linux Enterprise End User License Agreement'
    ]
    result = confirm_license_content(license_dirs, license_content)

    if result is False:
        pytest.fail(
            'SUSE End User License Agreement not found '
            'or license has incorrect content.'
        )
