

def test_sles_ec2_uuid(host):
    result = host.run('sudo cat /sys/devices/virtual/dmi/id/product_uuid')
    assert result.stdout[:3].lower() == 'ec2'
