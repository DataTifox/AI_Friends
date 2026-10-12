"""UTC storage timestamps and China-local display dates."""

from datetime import datetime, timedelta, timezone

CHINA_TIME = timezone(timedelta(hours=8))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def db_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def parse_db_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def display_time(value: str) -> str:
    return parse_db_time(value).astimezone(CHINA_TIME).strftime("%Y-%m-%d %H:%M")
