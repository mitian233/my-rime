#!/usr/bin/env python3
"""Restore pinned external lexicons without third-party Python dependencies."""
import argparse
import hashlib
import json
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            checksum.update(chunk)
    return checksum.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Only verify; never download")
    args = parser.parse_args()
    try:
        lock = json.loads((ROOT / "scripts/dictionaries.lock.json").read_text())
    except (OSError, ValueError) as error:
        print(f"无法读取词库锁定清单：{error}", file=sys.stderr)
        return 1
    errors = []
    for entry in lock["files"]:
        target = ROOT / entry["path"]
        if target.is_file():
            if digest(target) == entry["sha256"]:
                print("OK:", entry["path"], flush=True)
            else:
                errors.append(f"本地内容已修改，未覆盖：{entry['path']}；请先备份，再移走该文件后重试。")
            continue
        if args.check:
            errors.append(f"缺少词库：{entry['path']}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            print("下载：", entry["path"], flush=True)
            url = urllib.parse.urlparse(entry["url"])
            if url.scheme != "https" or url.netloc != "raw.githubusercontent.com":
                raise ValueError("只允许从 raw.githubusercontent.com 使用 HTTPS 下载")
            with (
                urllib.request.urlopen(entry["url"], timeout=120) as response,  # nosec B310: HTTPS host validated above
                tempfile.NamedTemporaryFile(dir=target.parent, suffix=".part", delete=False) as output,
            ):
                temporary = Path(output.name)
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            if digest(temporary) != entry["sha256"]:
                raise ValueError("SHA-256 校验失败")
            temporary.replace(target)
            print("OK:", entry["path"], flush=True)
        except Exception as error:
            errors.append(f"{entry['path']}: {error}")
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("词库准备完成。现在可以重新部署 Rime。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
