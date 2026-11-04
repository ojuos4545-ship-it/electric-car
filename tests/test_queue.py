import shutil
from datetime import datetime

import pytest

from evblog import queue as q

REAL_QUEUE = q.DEFAULT_QUEUE_PATH


@pytest.fixture
def qpath(tmp_path):
    dst = tmp_path / "queue.csv"
    shutil.copy(REAL_QUEUE, dst)
    return dst


def test_초기_큐_구성():
    items = q.load_queue(REAL_QUEUE)
    queued = [i for i in items if i.status == "queued"]
    hold = [i for i in items if i.status == "hold"]
    assert len(queued) == 10 and len(hold) == 10
    assert queued[0].slug == "kia-ev3"
    assert [i.order for i in items] == sorted(i.order for i in items)


def test_모든_상태에_전환규칙이_정의됨():
    assert set(q.TRANSITIONS) == set(q.STATUSES)
    for targets in q.TRANSITIONS.values():
        assert targets <= set(q.STATUSES)


def test_정상_흐름(qpath):
    for s in ["researching", "drafting", "verifying", "ready", "published", "stale"]:
        q.set_status("kia-ev3", s, path=qpath)
    assert q.get_item(q.load_queue(qpath), "kia-ev3").status == "stale"


def test_needs_human_경로(qpath):
    for s in ["researching", "drafting", "verifying", "needs_human", "verifying", "ready"]:
        q.set_status("kia-ev3", s, path=qpath)


@pytest.mark.parametrize("start,bad", [
    ("queued", "ready"), ("queued", "published"), ("drafting", "ready"),
    ("verifying", "published"), ("needs_human", "ready"), ("published", "queued"),
])
def test_금지된_전환(start, bad):
    assert not q.can_transition(start, bad)


def test_금지된_전환은_예외이고_파일은_그대로(qpath):
    before = qpath.read_bytes()
    with pytest.raises(q.InvalidTransition):
        q.set_status("kia-ev3", "ready", path=qpath)
    assert qpath.read_bytes() == before


def test_알수없는_slug_상태(qpath):
    with pytest.raises(q.UnknownSlug):
        q.set_status("nope", "researching", path=qpath)
    with pytest.raises(q.InvalidTransition):
        q.set_status("kia-ev3", "weird", path=qpath)


def test_next_queued_order순_hold제외(qpath):
    assert q.next_queued(q.load_queue(qpath)).slug == "kia-ev3"
    q.set_status("kia-ev3", "researching", path=qpath)
    assert q.next_queued(q.load_queue(qpath)).slug == "kia-ev5"


def test_claim_next와_빈큐(qpath):
    now = datetime(2026, 11, 4, 9, 0, 0)
    item = q.claim_next(path=qpath, now=now)
    assert item.slug == "kia-ev3" and item.status == "researching"
    assert item.updated_at == "2026-11-04T09:00:00"
    items = q.load_queue(qpath)
    for i in items:
        if i.status == "queued":
            i.status = "hold"
    q.save_queue(items, qpath)
    assert q.claim_next(path=qpath) is None


def test_한글_저장_왕복(qpath):
    q.set_status("kia-ev3", "researching", note="메모 테스트", path=qpath)
    item = q.get_item(q.load_queue(qpath), "kia-ev3")
    assert item.brand == "기아" and item.note == "메모 테스트"


def test_중복_slug_거부(qpath):
    items = q.load_queue(qpath)
    items[1].slug = items[0].slug
    q.save_queue(items, qpath)
    with pytest.raises(q.QueueError):
        q.load_queue(qpath)
