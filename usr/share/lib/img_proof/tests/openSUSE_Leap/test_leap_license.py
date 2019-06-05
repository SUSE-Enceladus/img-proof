def test_leap_license(host):
    license_dir = '/usr/share/licenses/openSUSE-release'
    license_content = 'LICENSE AGREEMENT'

    lic_dir = host.file(license_dir)
    assert lic_dir.exists
    assert lic_dir.is_directory

    license = host.file(license_dir + '/license.txt')
    assert license.exists
    assert license.is_file
    assert license.contains(license_content)
