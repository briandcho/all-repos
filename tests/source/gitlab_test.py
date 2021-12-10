import json

import pytest

from all_repos.source.gitlab import list_repos
from all_repos.source.gitlab import Settings
from testing.mock_http import FakeResponse
from testing.mock_http import urlopen_side_effect

TEST_API_URL = 'https://gitlab.on.prem/api/v4'


@pytest.mark.usefixtures('repos_response')
@pytest.mark.parametrize(
    ('settings', 'expected_repo_names'),
    (
        pytest.param(
            {'membership': None},
            {
                'briandcho/twenty48',
                'sudoscience/sandbox',
            },
            id='wide open',
        ),
        pytest.param(
            {'owned': True},
            {
                'briandcho/twenty48',
                'sudoscience/sandbox',
            },
            id='owned repo',
        ),
        pytest.param(
            {'visibility': 'private'},
            {'sudoscience/sandbox'},
            id='private repo',
        ),
        pytest.param(
            {'archived': True},
            {'sudoscience/flask-autodevops'},
            id='archived repo',
        ),
        pytest.param(
            {'forks': True},
            {
                'briandcho/gitlab',
                'briandcho/twenty48',
                'sudoscience/sandbox',
            },
            id='forked repo',
        ),
    ),
)
def test_list_repos(settings, expected_repo_names):
    repos = list_repos(
        Settings('key', base_url=TEST_API_URL, **settings),
    )
    assert set(repos) == expected_repo_names


def test_settings_repr():
    assert repr(Settings('key')) == (
        'Settings(\n'
        '    api_key=...,\n'
        '    forks=False,\n'
        '    archived=False,\n'
        "    base_url='https://gitlab.com/api/v4',\n"
        '    membership=True,\n'
        '    owned=None,\n'
        '    visibility=None,\n'
        ')'
    )


@pytest.fixture
def repos_response(mock_urlopen):
    public = _resource_json('twenty48')
    forked = _resource_json('gitlab')
    private = _resource_json('sandbox')
    archived = _resource_json('flask-autodevops')
    all_repos = [public, forked, private]
    base_url = f'{TEST_API_URL}/projects'
    base_params = '?pagination=keyset&per_page=100&order_by=id'
    all_url = base_url + base_params + '&archived=false'
    default_url = all_url + '&membership=true'
    private_url = default_url + '&visibility=private'
    owned_url = default_url + '&owned=true'
    archived_url = base_url + base_params + '&archived=true&membership=true'
    mock_urlopen.side_effect = urlopen_side_effect({
        all_url: FakeResponse(json.dumps(all_repos).encode()),
        default_url: FakeResponse(json.dumps(all_repos).encode()),
        owned_url: FakeResponse(json.dumps(all_repos).encode()),
        private_url: FakeResponse(json.dumps([private]).encode()),
        archived_url: FakeResponse(json.dumps([archived]).encode()),
    })
    return all_repos


def _resource_json(repo_name):
    with open(f'testing/resources/gitlab/{repo_name}.json') as f:
        return json.load(f)
