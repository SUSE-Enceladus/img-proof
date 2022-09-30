def test_sles_azure_kernel_cmdline(host, determine_architecture):
    kernel_cmdline = host.run('cat /proc/cmdline')
    kernel_args = kernel_cmdline.stdout.split()
    arch = determine_architecture()

    expected_args = {
        'X86_64': [
            'dis_ucode_ldr',
            'earlyprintk=ttyS0'
        ],
        'AARCH64': [
            'console=tty1',
            'console=ttyAMA0',
            'earlycon=pl011,0xeffec000',
            'initcall_blacklist=arm_pmu_acpi_init'
        ]
    }

    for arg in expected_args[arch]:
        assert arg in kernel_args

    for arg in expected_args['X86_64' if arch == 'AARCH64' else 'AARCH64']:
        assert arg not in kernel_args
