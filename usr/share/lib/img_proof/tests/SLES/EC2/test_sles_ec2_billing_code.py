import pytest


def test_sles_ec2_billing_code(
    get_ec2_billing_products,
    is_byos,
    get_release_value,
    is_suma_server
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

    has_no_code = (
        byos or
        (variant in ('sles-sap', 'sles-sap-hardened') and not byos) or
        is_suma_server() and not byos
    )

    if has_no_code:
        assert products is None
    else:
        assert products
