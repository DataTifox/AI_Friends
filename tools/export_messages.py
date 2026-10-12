"""Export one China-local calendar day to JSONL without modifying the database."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3


CHINA_TIME = timezone(timedelta(hours=8))
PROJECT_DIR = Path(__file__).resolve().parents[1]


def export_day(database_path: Path, output_path: Path, date_text: str) -> int:
    if output_path.resolve() == database_path.resolve():
        raise ValueError("导出路径不能是原数据库文件。")
    local_start = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=CHINA_TIME)
    utc_start = local_start.astimezone(timezone.utc)
    utc_end = utc_start + timedelta(days=1)
    connection = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    count = 0
    try:
        rows = connection.execute(
            """SELECT id, conversation_id, role, content, created_at FROM messages
            WHERE created_at >= ? AND created_at < ? ORDER BY created_at, id""",
            (utc_start.strftime("%Y-%m-%d %H:%M:%S"), utc_end.strftime("%Y-%m-%d %H:%M:%S")),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as output:
            for row in rows:
                item = dict(row)
                utc_time = datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                item["created_at"] = utc_time.isoformat()
                item["local_time"] = utc_time.astimezone(CHINA_TIME).isoformat()
                output.write(json.dumps(item, ensure_ascii=False) + "\n")
                count += 1
    finally:
        connection.close()
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="按北京时间的日期导出聊天记录；不修改原数据库。")
    parser.add_argument("date", help="日期，例如 2026-10-12")
    parser.add_argument("--output", type=Path, help="输出 JSONL 文件路径")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已有导出文件")
    args = parser.parse_args()
    output = args.output or PROJECT_DIR / "exports" / f"{args.date}_messages.jsonl"
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
        if output.exists() and not args.overwrite:
            parser.error("导出文件已存在；如需覆盖请加 --overwrite。")
        count = export_day(PROJECT_DIR / "data" / "companion.db", output, args.date)
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.error(f"导出失败：{error}")
    print(f"已导出 {count} 条消息：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
