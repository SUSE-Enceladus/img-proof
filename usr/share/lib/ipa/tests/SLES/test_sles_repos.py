

def test_sles_repos(check_zypper_repo,
                    determine_provider,
                    get_release_value,
                    get_sles_repos):
    provider = determine_provider()
    version = get_release_value('VERSION')

    for repo in get_sles_repos(version):
        assert check_zypper_repo(
            ''.join([
                'SMT-http_smt-{provider}_susecloud_net:'.format(
                    provider=provider
                ),
                repo
            ])
        )
