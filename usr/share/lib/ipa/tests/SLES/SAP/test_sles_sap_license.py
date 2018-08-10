def test_sles_sap_license(host):
    license_dir = '/etc/YaST2/licenses/ha'
    license_content = 'SUSE End User License Agreement'

    lic_dir = host.file(license_dir)

    try:
        assert lic_dir.exists
        assert lic_dir.is_directory
    except AssertionError:
        # SLE15 dir changed
        license_dir = '/etc/YaST2/licenses/SLES_SAP'
        lic_dir = host.file(license_dir)
        assert lic_dir.exists
        assert lic_dir.is_directory

    license = host.file(license_dir + '/license.txt')
    assert license.exists
    assert license.is_file

    try:
        assert license.contains(license_content)
    except AssertionError:
        # SLE15 license text changed
        license_content = 'SUSE(R) Linux Enterprise End User License Agreement'
        assert license.contains(license_content)
