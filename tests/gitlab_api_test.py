from unittest import mock

from all_repos import gitlab_api
from testing.mock_http import FakeResponse
from testing.mock_http import urlopen_side_effect


def test_get_all(mock_urlopen):
    mock_urlopen.side_effect = urlopen_side_effect({
        'https://example.com/api': FakeResponse(
            b'["page1_1", "page1_2"]',
            next_link='https://example.com/api?page=2',
        ),
        'https://example.com/api?page=2': FakeResponse(
            b'["page2_1", "page2_2"]',
            next_link='https://example.com/api?page=3',
        ),
        'https://example.com/api?page=3': FakeResponse(
            b'["page3_1"]',
        ),
    })

    ret = gitlab_api.get_all('https://example.com/api')
    assert ret == ['page1_1', 'page1_2', 'page2_1', 'page2_2', 'page3_1']


@mock.patch.dict(gitlab_api.os.environ, {'ALL_REPOS_SSL_NO_VERIFY': 'true'})
def test_req_bypasses_ssl(mock_urlopen):
    mock_urlopen.side_effect = urlopen_side_effect({
        'fake://url': FakeResponse(b'{}'),
    })
    gitlab_api.req('fake://url')
    mock_urlopen.assert_called_with(mock.ANY, context=gitlab_api.NO_SSL)
