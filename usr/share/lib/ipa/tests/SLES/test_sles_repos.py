def test_sles_repos(CheckZypperRepo, GetReleaseValue, GetSLESRepos, request):
    provider = request.config.getoption('provider')
    version = GetReleaseValue('VERSION')

    for repo in GetSLESRepos(version):
        assert CheckZypperRepo(
            ''.join([
                'SMT-http_smt-{provider}_susecloud_net:'.format(
                    provider=provider
                ),
                repo
            ])
        )
