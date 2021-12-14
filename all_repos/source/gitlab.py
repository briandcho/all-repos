import os
from typing import Dict
from typing import NamedTuple
from typing import Optional

from all_repos import gitlab_api
from all_repos.util import hide_api_key_repr

DEFAULT_HOST: str = os.environ.get('ALL_REPOS_GITLAB_HOST', 'gitlab.com')


class Settings(NamedTuple):
    api_key: str
    forks: bool = False
    archived: bool = False
    base_url: str = f'https://{DEFAULT_HOST}/api/v4'
    base_params: str = 'pagination=keyset&order_by=id&per_page=100'
    membership: Optional[bool] = True
    owned: Optional[bool] = None
    visibility: Optional[str] = None

    def __repr__(self) -> str:
        return hide_api_key_repr(self)


def list_repos(settings: Settings) -> Dict[str, str]:
    params = settings_to_url_params(settings)
    repos = gitlab_api.get_all(
        f'{settings.base_url}/projects?{settings.base_params}{params}',
        headers={'Private-Token': settings.api_key},
    )
    return gitlab_api.filter_repos_from_settings(repos, settings)


def settings_to_url_params(settings: Settings) -> str:
    s = f'&archived={str(settings.archived).lower()}'
    if settings.membership is not None:
        s += f'&membership={str(settings.membership).lower()}'
    if settings.owned is not None:
        s += f'&owned={str(settings.owned).lower()}'
    if settings.visibility is not None:
        s += f'&visibility={settings.visibility}'
    return s
