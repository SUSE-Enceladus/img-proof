import pytest


def test_sles_ec2_billing_code(
    get_ec2_billing_products,
    is_byos,
    get_release_value
):
    try:
        products = get_ec2_billing_products()
    except Exception:
        # CHOST images have no ec2metdata.
        pytest.skip(
            'ec2metadata not in image, cannot determine billing products.'
        )

    variant = get_release_value('VARIANT_ID')
    byos = is_byos()

    if byos or (variant in ('sles-sap', 'sles-sap-hardened') and not byos):
        assert products is None
    else:
        assert products
