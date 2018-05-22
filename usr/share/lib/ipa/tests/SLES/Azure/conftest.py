import json
import pytest


@pytest.fixture()
def get_azure_billing_tag(host):
    def f():
        result = host.run(
            'sudo azuremetadata --tag'
        )

        data = json.loads(result.stdout.strip())
        return data['billingTag']
    return f