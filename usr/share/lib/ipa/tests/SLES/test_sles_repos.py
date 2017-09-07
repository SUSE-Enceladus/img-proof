repos = [
    ('nVidia-Driver-SLE{version}'),
    ('SLE-Module-Adv-Systems-Management{release}-Debuginfo-Pool'),
    ('SLE-Module-Adv-Systems-Management{release}-Debuginfo-Updates'),
    ('SLE-Module-Adv-Systems-Management{release}-Pool'),
    ('SLE-Module-Adv-Systems-Management{release}-Updates'),
    ('SLE-Module-Containers{release}-Debuginfo-Pool'),
    ('SLE-Module-Containers{release}-Debuginfo-Updates'),
    ('SLE-Module-Containers{release}-Pool'),
    ('SLE-Module-Containers{release}-Updates'),
    ('SLE-Module-HPC{release}-Debuginfo-Pool'),
    ('SLE-Module-HPC{release}-Debuginfo-Updates'),
    ('SLE-Module-HPC{release}-Pool'),
    ('SLE-Module-HPC{release}-Updates'),
    ('SLE-Module-Legacy{release}-Debuginfo-Pool'),
    ('SLE-Module-Legacy{release}-Debuginfo-Updates'),
    ('SLE-Module-Legacy{release}-Pool'),
    ('SLE-Module-Legacy{release}-Updates'),
    ('SLE-Module-Public-Cloud{release}-Debuginfo-Pool'),
    ('SLE-Module-Public-Cloud{release}-Debuginfo-Updates'),
    ('SLE-Module-Public-Cloud{release}-Pool'),
    ('SLE-Module-Public-Cloud{release}-Updates'),
    ('SLE-Module-Toolchain{release}-Debuginfo-Pool'),
    ('SLE-Module-Toolchain{release}-Debuginfo-Updates'),
    ('SLE-Module-Toolchain{release}-Pool'),
    ('SLE-Module-Toolchain{release}-Updates'),
    ('SLE-Module-Web-Scripting{release}-Debuginfo-Pool'),
    ('SLE-Module-Web-Scripting{release}-Debuginfo-Updates'),
    ('SLE-Module-Web-Scripting{release}-Pool'),
    ('SLE-Module-Web-Scripting{release}-Updates'),
    ('SLES{version}-Debuginfo-Pool'),
    ('SLES{version}-Debuginfo-Updates'),
    ('SLES{version}-Pool'),
    ('SLES{version}-Updates'),
    ('SLE-SDK{version}-Debuginfo-Pool'),
    ('SLE-SDK{version}-Debuginfo-Updates'),
    ('SLE-SDK{version}-Pool'),
    ('SLE-SDK{version}-Updates')
]


def test_sles_repos(CheckZypperRepo, GetReleaseValue, request):
    provider = request.config.getoption('provider')

    version = GetReleaseValue('VERSION')
    release = version.split('-')[0]

    for repo in repos:
        if repo.startswith('SLE'):
            repo = ''.join(['SMT-http_smt-%s_susecloud_net:' % provider, repo])

        assert CheckZypperRepo(repo.format(version=version, release=release))
