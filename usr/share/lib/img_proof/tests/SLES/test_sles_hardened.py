import pytest


SWAP_FILE = "/swap"


# Workaround for OOM killer triggered by the issue
# https://github.com/OpenSCAP/openscap/issues/1796
def setup_swap(host, swap_file=SWAP_FILE):
    min_memory = 16e6
    mem_total = int(host.run(
        "cat /proc/meminfo | awk '$0 ~ /MemTotal:/ { print $2 }'"
    ).stdout.strip())
    if mem_total < min_memory:
        # Follow steps in https://btrfs.readthedocs.io/en/latest/Swapfile.html
        for command in [
            "sudo truncate -s 0 {}".format(swap_file),
            "sudo chattr +C {} || true".format(swap_file),
            "sudo fallocate -l 4G {}".format(swap_file),
            "sudo chmod 600 {}".format(swap_file),
            "sudo mkswap {}".format(swap_file),
            "sudo swapon {}".format(swap_file),
        ]:
            result = host.run(command)
            if result.rc != 0:
                return False
    return True


def remove_swap(host, swap_file=SWAP_FILE):
    host.run("sudo swapoff {}".format(swap_file))
    host.run("sudo rm {}".format(swap_file))


def test_sles_hardened(host, get_release_value, is_sles_sap, is_sle_micro):
    variant = get_release_value('VARIANT_ID') or ''

    if "hardened" not in variant:
        pytest.skip('Skipping non-hardened image')
    if is_sle_micro():
        pytest.skip('Skipping SLE Micro')

    if not setup_swap(host):
        pytest.skip("Failed to setup swap, not enough memory.")

    xml_path = "pub/projects/security/oval/suse.linux.enterprise.15.xml"
    # Downloaded file should have slashes replaced by hyphens
    xml_file = xml_path.replace("/", "-")
    oscap_dir = "/tmp/oscap"
    oscap_file = "/usr/share/xml/scap/ssg/content/ssg-sle15-ds.xml"
    oscap_profile = "pcs-hardening-sap" if is_sles_sap() else "pcs-hardening"

    host.run("mkdir {}".format(oscap_dir))
    host.run(
        "curl -o- https://ftp.suse.com/{path}.gz | gunzip -c > {dir}/{file}".format(
            path=xml_path,
            file=xml_file,
            dir=oscap_dir,
        )
    )

    result = host.run(
        "sudo oscap xccdf eval --local-files {dir} --profile {profile} {file}".format(
            dir=oscap_dir,
            file=oscap_file,
            profile=oscap_profile,
        )
    )

    assert result.rc == 0

    remove_swap(host)
