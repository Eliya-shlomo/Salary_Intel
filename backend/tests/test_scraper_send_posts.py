import json

import httpx
import pytest

from scraper import send_posts
from scraper.send_posts import delete_files, results_path, send_file

API_URL = "http://test"


def write_posts(path, texts):
    path.write_text("".join(json.dumps({"text": t, "source": "facebook_group"}, ensure_ascii=False) + "\n" for t in texts))
    return path


def make_client(statuses, requests):
    responses = iter(statuses)

    def handler(request):
        requests.append(request)
        status = next(responses)
        if isinstance(status, Exception):
            raise status
        return httpx.Response(status)

    return httpx.Client(transport=httpx.MockTransport(handler))


class FakeSleep:
    def __init__(self):
        self.calls = []

    def __call__(self, seconds):
        self.calls.append(seconds)


def test_status_codes_map_to_outcomes(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a", "b", "c", "d", "e"])
    requests = []
    client = make_client([201, 202, 409, 422, 500], requests)

    results = send_file(path, API_URL, client=client, sleep=FakeSleep())

    assert results == {
        "approved": 1,
        "pending_review": 1,
        "duplicate": 1,
        "not_a_salary_post": 1,
        "error_500": 1,
    }
    assert json.loads(requests[0].content) == {"raw_text": "a", "source": "facebook_group"}
    assert requests[0].url == "http://test/api/v1/posts"


def test_pauses_between_posts_but_not_before_the_first(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a", "b", "c"])
    sleep = FakeSleep()

    send_file(path, API_URL, client=make_client([201, 201, 201], []), pause=13, sleep=sleep)

    assert sleep.calls == [13, 13]


def test_retries_once_after_429(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a"])
    requests = []
    sleep = FakeSleep()

    results = send_file(path, API_URL, client=make_client([429, 201], requests), pause=0, sleep=sleep)

    assert results == {"approved": 1}
    assert len(requests) == 2
    assert sleep.calls == [send_posts.RATE_LIMIT_WAIT_SECONDS]


def test_gives_up_after_second_429(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a"])
    requests = []

    results = send_file(path, API_URL, client=make_client([429, 429], requests), pause=0, sleep=FakeSleep())

    assert results == {"error_429": 1}
    assert len(requests) == 2


@pytest.mark.parametrize("name", ["posts_1.jsonl", "posts_1.unsure.jsonl", "posts_1.clean.json"])
def test_refuses_files_that_were_not_scrubbed(tmp_path, name):
    path = write_posts(tmp_path / name, ["a"])
    requests = []

    with pytest.raises(ValueError, match="scrub_posts"):
        send_file(path, API_URL, client=make_client([201], requests), sleep=FakeSleep())
    assert requests == []


def test_resume_after_crash_does_not_send_twice(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a", "b", "c"])
    first_requests = []
    crashing = make_client([201, httpx.ConnectError("server down")], first_requests)

    with pytest.raises(httpx.ConnectError):
        send_file(path, API_URL, client=crashing, pause=0, sleep=FakeSleep())

    second_requests = []
    results = send_file(path, API_URL, client=make_client([202, 409], second_requests), pause=0, sleep=FakeSleep())

    assert [json.loads(r.content)["raw_text"] for r in second_requests] == ["b", "c"]
    assert results == {"already_sent": 1, "pending_review": 1, "duplicate": 1}


def test_failed_posts_are_retried_on_the_next_run(tmp_path):
    path = write_posts(tmp_path / "posts_1.clean.jsonl", ["a", "b"])
    send_file(path, API_URL, client=make_client([201, 500], []), pause=0, sleep=FakeSleep())

    second_requests = []
    send_file(path, API_URL, client=make_client([201], second_requests), pause=0, sleep=FakeSleep())

    assert [json.loads(r.content)["raw_text"] for r in second_requests] == ["b"]


def test_delete_files_removes_clean_raw_and_results(tmp_path):
    clean = write_posts(tmp_path / "posts_1.clean.jsonl", ["a"])
    raw = write_posts(tmp_path / "posts_1.jsonl", ["a"])
    unsure = write_posts(tmp_path / "posts_1.unsure.jsonl", ["b"])
    send_file(clean, API_URL, client=make_client([201], []), sleep=FakeSleep())

    deleted = delete_files(clean)

    assert set(deleted) == {clean, raw, results_path(clean)}
    assert not clean.exists() and not raw.exists() and not results_path(clean).exists()
    assert unsure.exists()


def test_main_deletes_only_when_every_post_finished(tmp_path, monkeypatch):
    clean = write_posts(tmp_path / "posts_1.clean.jsonl", ["a", "b"])
    clients = [make_client([201, 500], []), make_client([201], [])]
    monkeypatch.setattr(
        send_posts,
        "send_file",
        lambda path, api_url: send_file(path, api_url, client=clients.pop(0), pause=0, sleep=FakeSleep()),
    )
    monkeypatch.setattr("sys.argv", ["send_posts", str(clean), "--delete-after-send"])

    assert send_posts.main() == 1
    assert clean.exists()

    assert send_posts.main() == 0
    assert not clean.exists()
    assert not results_path(clean).exists()
