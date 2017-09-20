

def test_sles_sap_repos(check_zypper_repo,
                        get_release_value,
                        get_sles_repos,
                        request):
    provider = request.config.getoption('provider')
    version = get_release_value('VERSION')

    for repo in get_sles_repos('%s-SAP' % version):
        assert check_zypper_repo(
            ''.join([
                'SMT-http_smt-{provider}_susecloud_net:'.format(
                    provider=provider
                ),
                repo
            ])
        )
