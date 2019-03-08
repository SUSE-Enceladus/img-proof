import pytest


def test_sles_repos(check_zypper_repo,
                    determine_provider,
                    get_release_value,
                    get_sles_repos,
                    is_sles_sap,
                    determine_architecture):
    version = []
    provider = determine_provider()
    version.append(get_release_value('VERSION'))
    version.append(determine_architecture())
    sap = is_sles_sap()

    if sap:
        version.append('SAP')

    version = '-'.join(version)

    missing_repos = []
    repos = get_sles_repos(version)

    if not repos:
        pytest.fail(
            'No repos found for version {0}'.format(version)
        )

    for repo in repos:
        result = check_zypper_repo(
            ''.join([
                'SMT-http_smt-{provider}_susecloud_net:'.format(
                    provider=provider
                ),
                repo
            ])
        )
        if not result:
            missing_repos.append(
                ''.join([
                    'SMT-http_smt-{provider}_susecloud_net:'.format(
                        provider=provider
                    ),
                    repo
                ])
            )

    if missing_repos:
        pytest.fail(
            'Missing Repos: \n{0}'.format('\n'.join(missing_repos))
        )
