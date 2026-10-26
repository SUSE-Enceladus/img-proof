import pytest


def test_sles_fips(host, is_chost, get_version):
    is_chost = is_chost()
    version = get_version()

    if not (is_chost and version >= 15.7):
        pytest.skip("The image does not have FIPS enabled by default")

    with host.sudo():
        host.check_output("fips-mode-setup --is-enabled")
