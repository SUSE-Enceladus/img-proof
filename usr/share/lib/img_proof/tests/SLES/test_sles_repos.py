import pytest


def test_sles_repos(
    get_instance_repos,
    get_version,
    get_sles_repos,
    get_micro_repos,
    get_baseproduct,
    determine_architecture,
    is_sles_sapcal,
    is_sle_micro
):
    version = [str(get_version()), determine_architecture()]
    is_micro = is_sle_micro()

    if not is_micro:
        product = get_baseproduct()
        if 'sap' in product.lower():
            version.append('SAP')
        if 'hpc' in product.lower():
            version.append('HPC')

    version = '-'.join(version)
    missing_repos = []

    if is_micro:
        repos = get_micro_repos(version)
    else:
        repos = get_sles_repos(version)

    if is_sles_sapcal():
        repos = [repo for repo in repos if 'Python2' not in repo]

    if not repos:
        pytest.fail(
            'No repos found for version {0}'.format(version)
        )

    instance_repos = get_instance_repos()

    for repo in repos:
        if repo not in instance_repos:
            missing_repos.append(repo)

    if missing_repos:
        pytest.fail(
            'Missing Repos: \n{0}'.format('\n'.join(missing_repos))
        )
