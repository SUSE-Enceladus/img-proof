

def test_sles_ec2_billing_code(get_ec2_billing_products):
    """
    This is really ONLY for SLES.

    All other on-demand products are sold through the Marketplace
    and they do not have a billing-product-code.
    """
    assert get_ec2_billing_products()
