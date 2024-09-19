import json
import pytest
import xml.etree.ElementTree as ET

from susepubliccloudinfoclient import infoserverrequests


@pytest.fixture()
def check_cloud_register(host):
    def f():
        # There was an API change in registerutils and we have to check
        # which version is in place on the system
        deleted_interface_import = \
            'from cloudregister.registerutils import check_registration'
        result = host.run(
            "sudo python3 -c '{0}'".format(deleted_interface_import)
        )
        # Old interface of is_registered()
        is_registered_arg = 'registerutils.get_current_smt()'
        if result.rc == 1:
            # New interface of is_registered()
            is_registered_arg = 'registerutils.get_current_smt().get_FQDN()'
        result = host.run(
            "sudo python3 -c 'from cloudregister import registerutils; "
            "print(registerutils.is_registered("
            "{0}))'".format(is_registered_arg)
        )
        output = result.stdout.strip()
        return output in ('1', 'True')
    return f


@pytest.fixture()
def check_service(host):
    def f(service_name, running=True, enabled=True):
        is_running = None
        is_enabled = None

        if host.exists('systemctl'):
            service = host.service(service_name)

            if running is not None:
                is_running = service.is_running

            if enabled is not None:
                is_enabled = service.is_enabled
        else:
            # SystemV Init
            if running is not None:
                is_running = host.run_expect(
                    [0, 1, 3],
                    'sudo /sbin/service {0} status'.format(service_name)
                ).rc == 0

            if enabled is not None:
                is_enabled = bool(host.check_output(
                    'find -L /etc/init.d/rc?.d/ -name S??{0}'.format(
                        service_name
                    ),
                ))

        return all([
            is_running == running,
            is_enabled == enabled
        ])
    return f


@pytest.fixture()
def determine_architecture(host):
    def f():
        result = host.run('uname --m')
        return result.stdout.strip().upper()
    return f


@pytest.fixture()
def determine_provider(host):
    def f():
        result = host.run('sudo /usr/sbin/dmidecode -t system')
        output = result.stdout.lower()
        if 'amazon' in output:
            provider = 'ec2'
        elif 'microsoft' in output:
            provider = 'azure'
        elif 'google' in output:
            provider = 'gce'
        else:
            raise Exception('Provider not found.')
        return provider
    return f


@pytest.fixture()
def determine_region(host):
    def f(provider):
        if provider == 'ec2':
            result = host.run(
                'curl http://169.254.169.254/latest/meta-data/placement/'
                'availability-zone'
            )
            region = result.stdout.strip()[:-1]
        elif provider == 'gce':
            result = host.run(
                'curl "http://metadata.google.internal/computeMetadata/v1/'
                'instance/zone" -H "Metadata-Flavor: Google"'
            )
            # returns zone like: us-west1-a
            region = result.stdout.strip().rsplit('/', maxsplit=1)[-1]
            # returns region: us-west1
            region = region.rsplit('-', maxsplit=1)[0]
        elif provider == 'azure':
            result = host.run(
                'curl -H Metadata:true '
                '"http://169.254.169.254/metadata/instance'
                '?api-version=2017-12-01"'
            )
            region = json.loads(result.stdout)['compute']['location']
        return region
    return f


@pytest.fixture()
def get_baseproduct(host):
    """
    Return the name of the file the 'baseproduct' link points to.
    """
    def f():
        result = host.run('readlink -f "/etc/products.d/baseproduct"')
        return result.stdout.strip()
    return f


@pytest.fixture()
def is_sles_sap(host, get_baseproduct):
    def f():
        sap_product = '/etc/products.d/SLES_SAP.prod'
        sap = host.file(sap_product)
        base_product = get_baseproduct()

        return all([
            sap.exists,
            sap.is_file,
            base_product == sap_product
        ])
    return f


@pytest.fixture()
def is_suma_server(host, get_baseproduct, get_suma_version):
    def f():
        suma_server_product = '/etc/products.d/SUSE-Manager-Server.prod'
        suma_server = host.file(suma_server_product)
        base_product = get_baseproduct()
        suma_version = get_suma_version(suma_server_product)

        if suma_version and suma_version.startswith('4'):
            # For suma 4.3 baseproduct HAS to be SUMA server
            expected_product = suma_server_product
        else:
            # For suma >=5 baseproduct has to be Micro
            # SUMA is included as an additional product
            expected_product = '/etc/products.d/SLE-Micro.prod'

        return all([
            suma_server.exists,
            suma_server.is_file,
            base_product == expected_product
        ])
    return f


@pytest.fixture()
def is_suma_proxy(host, get_baseproduct, get_suma_version):
    def f():
        suma_proxy_product = '/etc/products.d/SUSE-Manager-Proxy.prod'
        suma_proxy = host.file(suma_proxy_product)
        base_product = get_baseproduct()
        suma_version = get_suma_version(suma_proxy_product)

        if suma_version and suma_version.startswith('4'):
            # For suma 4.3 baseproduct HAS to be SUMA proxy
            expected_product = suma_proxy_product
        else:
            # For suma >=5 baseproduct has to be Micro
            # SUMA is included as an additional product
            expected_product = '/etc/products.d/SLE-Micro.prod'

        return all([
            suma_proxy.exists,
            suma_proxy.is_file,
            base_product == expected_product
        ])
    return f


@pytest.fixture()
def is_suma(is_suma_server, is_suma_proxy):
    def f():
        return is_suma_server() or is_suma_proxy()
    return f


@pytest.fixture()
def get_suma_version(host):
    def f(product_file):
        version = ''
        try:
            suma_product = host.file(product_file)
            xmlroot = ET.fromstring(suma_product.content_string)
            version = xmlroot.find('./version').text
        except Exception:
            pass
        return version
    return f


@pytest.fixture()
def is_sles_sapcal(host):
    def f():
        motd = host.file('/etc/motd')
        return motd.contains('SAPCAL')
    return f


@pytest.fixture()
def is_sle_micro(host, get_release_value):
    def f():
        name = get_release_value('PRETTY_NAME')
        return 'micro' in name.lower()
    return f


@pytest.fixture()
def get_release_value(host):
    def f(key):
        release = host.file('/etc/os-release')

        if not release.exists:
            release = host.file('/etc/SUSE-release')

        value = None
        key += '='

        for line in release.content_string.split('\n'):
            if line.startswith(key):
                value = line[len(key):].replace('"', '').replace("'", '')
                value = value.strip()
                break

        return value
    return f


@pytest.fixture()
def get_smt_server_name(host):
    def f(provider):
        return 'smt-{}.susecloud.net'.format(provider)
    return f


@pytest.fixture()
def get_smt_servers():
    def f(provider, region=None):
        if provider == 'azure':
            provider = 'microsoft'
        elif provider == 'ec2':
            provider = 'amazon'
        elif provider == 'gce':
            provider = 'google'
        else:
            raise Exception('Provider %s unknown' % provider)

        args = [provider, 'smt', 'json']

        if region:
            args.append(region)

        output = json.loads(
            infoserverrequests.get_server_data(*args)
        )

        return output['servers']
    return f


@pytest.fixture()
def install_zypper_package(host):
    def f(name):
        result = host.run('sudo zypper -n in %s' % name)
        return result.rc
    return f


@pytest.fixture()
def confirm_license_content(host):
    def f(license_dirs, license_content):
        for license_dir in license_dirs:
            lic_dir = host.file(license_dir)

            if lic_dir.exists and lic_dir.is_directory:
                lic = host.file(license_dir + 'license.txt')
                return all([
                    lic.exists,
                    lic.is_file,
                    any(lic.contains(content) for content in license_content)
                ])

        return False
    return f


@pytest.fixture()
def is_byos(host):
    def f():
        result = host.run('rpm -q cloud-regionsrv-client')
        service = host.service('guestregister.service')
        is_client_installed = result.rc == 0

        if is_client_installed and service.is_enabled:
            return False
        else:
            return True
    return f


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers",
        "skipinbeta: mark test to be skipped during beta testing phase"
    )
