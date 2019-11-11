import pytest


def test_sles_sap_license(confirm_license_content, get_release_value):
    version = get_release_value('VERSION')

    if version in ('12-SP4', '12-SP5'):
        # Skip SAP specific license, license is combined
        pytest.skip('Has combined SAP license.')

    license_dirs = [
        '/etc/YaST2/licenses/ha/',
        '/etc/YaST2/licenses/SLES_SAP/',
        '/usr/share/licenses/product/SLES_SAP/'
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
