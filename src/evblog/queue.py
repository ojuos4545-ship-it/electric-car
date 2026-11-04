"""차종 큐 읽기·상태 갱신. 상태 전환 규칙은 TRANSITIONS가 유일한 기준이다."""
from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from pathlib import Path

DEFAULT_QUEUE_PATH = Path(__file__).resolve().parents[2] / "data" / "queue.csv"
COLUMNS = ["order", "brand", "model", "slug", "status", "updated_at", "note"]

STATUSES = (
    "hold", "queued", "researching", "drafting", "verifying",
    "needs_human", "ready", "published", "stale",
)

# 허용되는 전환만 나열한다. 여기 없는 전환은 오류.
TRANSITIONS: dict[str, frozenset[str]] = {
    "hold": frozenset({"queued"}),
    "queued": frozenset({"researching", "hold"}),
    "researching": frozenset({"drafting", "needs_human"}),
    "drafting": frozenset({"verifying", "needs_human"}),
    "verifying": frozenset({"needs_human", "ready"}),
    # 사람이 확인 후 검증을 다시 돌리거나(verifying), 처음부터 재시작(queued)
    "needs_human": frozenset({"verifying", "queued"}),
    "ready": frozenset({"published", "needs_human"}),
    "published": frozenset({"stale"}),
    "stale": frozenset({"queued"}),  # 새 시점 글을 새로 쓸 때
}


class QueueError(Exception):
    """큐 관련 오류의 기본 클래스."""


class InvalidTransition(QueueError):
    """허용되지 않은 상태 전환."""


class UnknownSlug(QueueError):
    """큐에 없는 slug."""


@dataclass
class QueueItem:
    order: int
    brand: str
    model: str
    slug: str
    status: str
    updated_at: str = ""
    note: str = ""


def can_transition(current: str, new: str) -> bool:
    return new in TRANSITIONS.get(current, frozenset())


def load_queue(path: Path | str = DEFAULT_QUEUE_PATH) -> list[QueueItem]:
    items: list[QueueItem] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = set(COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise QueueError(f"queue.csv에 없는 열: {sorted(missing)}")
        for row in reader:
            if row["status"] not in STATUSES:
                raise QueueError(f"알 수 없는 상태값 '{row['status']}' (slug={row['slug']})")
            items.append(QueueItem(
                order=int(row["order"]), brand=row["brand"], model=row["model"],
                slug=row["slug"], status=row["status"],
                updated_at=row["updated_at"], note=row["note"],
            ))
    slugs = [i.slug for i in items]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        raise QueueError(f"중복 slug: {sorted(dup)}")
    return items


def save_queue(items: list[QueueItem], path: Path | str = DEFAULT_QUEUE_PATH) -> None:
    """임시 파일에 쓴 뒤 교체해서, 중간에 끊겨도 원본이 깨지지 않게 한다."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=[x.name for x in fields(QueueItem)])
            writer.writeheader()
            for item in sorted(items, key=lambda i: i.order):
                writer.writerow(asdict(item))
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def get_item(items: list[QueueItem], slug: str) -> QueueItem:
    for item in items:
        if item.slug == slug:
            return item
    raise UnknownSlug(f"큐에 없는 slug: {slug}")


def next_queued(items: list[QueueItem]) -> QueueItem | None:
    """order가 가장 작은 queued 차종. 없으면 None."""
    candidates = [i for i in items if i.status == "queued"]
    return min(candidates, key=lambda i: i.order) if candidates else None


def set_status(
    slug: str, new_status: str, note: str | None = None,
    path: Path | str = DEFAULT_QUEUE_PATH, now: datetime | None = None,
) -> QueueItem:
    """상태를 전환하고 저장한다. 허용되지 않은 전환이면 InvalidTransition."""
    if new_status not in STATUSES:
        raise InvalidTransition(f"알 수 없는 상태값: {new_status}")
    items = load_queue(path)
    item = get_item(items, slug)
    if not can_transition(item.status, new_status):
        raise InvalidTransition(f"{slug}: {item.status} → {new_status} 전환은 허용되지 않습니다")
    item.status = new_status
    item.updated_at = (now or datetime.now()).isoformat(timespec="seconds")
    if note is not None:
        item.note = note
    save_queue(items, path)
    return item


def claim_next(path: Path | str = DEFAULT_QUEUE_PATH, now: datetime | None = None) -> QueueItem | None:
    """다음 queued 차종을 골라 researching으로 바꾸고 반환. 없으면 None."""
    item = next_queued(load_queue(path))
    if item is None:
        return None
    return set_status(item.slug, "researching", path=path, now=now)
