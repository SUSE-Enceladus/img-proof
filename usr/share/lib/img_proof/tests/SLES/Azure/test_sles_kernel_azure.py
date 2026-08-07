

def test_sles_kernel_azure(
    host,
    get_version,
    get_variant,
    is_byos,
    is_suma,
    determine_architecture
):
    version = get_version()
    assert version

    arch = determine_architecture()
    assert arch

    variant = get_variant().lower()

    uname_check = host.run('uname -r')
    assert uname_check.rc == 0, (
        f"uname -r command failed: {uname_check.stderr}"
    )

    active_sle_versions = (15.7, 16.0, 16.1)
    use_default_kernel = (
        version not in active_sle_versions or
        is_byos() or
        arch == 'AARCH64' or
        'micro' in variant or
        'sap' in variant or
        'hpc' in variant or
        'sapcal' in variant or
        'hardened' in variant or
        'chost' in variant or
        is_suma()
    )

    if use_default_kernel:
        assert 'azure' not in uname_check.stdout, (
            f"The running kernel is not default kernel: {uname_check.stdout}"
        )
    else:
        assert 'azure' in uname_check.stdout, (
            f"The running kernel is not azure kernel: {uname_check.stdout}"
        )

        rpm_check = host.run('rpm -q kernel-azure')
        assert rpm_check.rc == 0, (
            f"kernel-azure package is not installed: {rpm_check.stderr}"
        )
