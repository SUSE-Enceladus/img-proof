import json
import pytest
import shlex

from susepubliccloudinfoclient import infoserverrequests


@pytest.fixture()
def check_cloud_register(host):
    def f():
        client_log = host.file('/var/log/cloudregister')
        return all([
            client_log.contains('ERROR') is False,
            client_log.contains('failed') is False
        ])
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
def check_zypper_repo(host):
    def f(repo):
        repo = host.file('/etc/zypp/repos.d/' + repo + '.repo')
        return repo.exists
    return f


@pytest.fixture()
def determine_provider(host):
    def f():
        result = host.run('sudo dmidecode -t system')
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
            result = host.run('ec2metadata --availability-zone')
            region = result.stdout.strip()[:-1]
        elif provider == 'gce':
            result = host.run('gcemetadata --query instance --zone')
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
def get_smt_servers(get_release_value, host):
    def f(provider, region):
        cpe_name = get_release_value('CPE_NAME')
        if 'sap' in cpe_name:
            smt_type = 'smt-sap'
        else:
            smt_type = 'smt-sles'

        if provider == 'azure':
            provider = 'microsoft'
        elif provider == 'ec2':
            provider = 'amazon'
        elif provider == 'gce':
            provider = 'google'
        else:
            raise Exception('Provider %s unknown' % provider)

        output = json.loads(
            infoserverrequests.get_server_data(
                provider,
                'smt',
                'json',
                region,
                'type~{smt_type}'.format(smt_type=smt_type)
            )
        )

        return output['servers']
    return f


@pytest.fixture()
def install_zypper_package(host):
    def f(name):
        result = host.run('sudo zypper -n in %s' % name)
        return result.rc
    return f
