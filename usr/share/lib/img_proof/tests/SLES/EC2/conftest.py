import json
import pytest


@pytest.fixture()
def get_ec2_billing_products(host):
    def f():
        result = host.run(
            'ec2metadata --api latest --document'
        )

        data = json.loads(result.stdout.strip())
        return data['billingProducts']
    return f
