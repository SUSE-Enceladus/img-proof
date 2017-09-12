import pytest


def pytest_addoption(parser):
    parser.addoption('--provider', action='store', help='ipa provider')
    parser.addoption('--region', action='store', help='ipa region')


@pytest.fixture()
def CheckService(host):
    def f(service_name, running=True, enabled=True):
        service = host.service(service_name)
        return all([
            service.is_running == running,
            service.is_enabled == enabled
        ])
    return f


@pytest.fixture()
def CheckZypperRepo(host):
    def f(repo):
        repo = host.file('/etc/zypp/repos.d/' + repo + '.repo')
        return repo.exists
    return f


@pytest.fixture()
def GetReleaseValue(host):
    def f(key):
        release = host.file('/etc/os-release')

        if not release.exists:
            release = host.file('/etc/SUSE-release')

        pretty_name = None
        key += '='

        for line in release.content_string.split('\n'):
            if line.startswith(key):
                pretty_name = line[len(key):].replace('"', '')\
                        .replace("'", '').strip()
                break

        return pretty_name
    return f


@pytest.fixture()
def InstallZypperPackage(host):
    def f(name):
        result = host.run('sudo zypper -n in %s' % name)
        return result.rc
    return f
