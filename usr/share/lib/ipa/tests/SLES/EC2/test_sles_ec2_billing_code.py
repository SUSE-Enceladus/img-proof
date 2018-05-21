

def test_sles_ec2_billing_code(get_ec2_billing_products):
    assert get_ec2_billing_products()
