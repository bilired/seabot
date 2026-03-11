#!/usr/bin/env python3
"""
批量上传本地图片到后端图像上传接口，用于验证后端接收与入库情况。

默认目录: ~/Desktop/boat-image
默认接口: https://yunpingtai.cc/api
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Iterable
from typing import Optional

import requests

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量上传 boat-image 图片到后端")
    parser.add_argument(
        "--base-url",
        default="https://yunpingtai.cc/api",
        help="后端 API 根地址，示例: http://127.0.0.1:8000/api"
    )
    parser.add_argument(
        "--image-dir",
        default=str(Path.home() / "Desktop" / "boat-image"),
        help="图片目录，默认 ~/Desktop/boat-image"
    )
    parser.add_argument("--username", required=False, help="登录用户名（可选）")
    parser.add_argument("--password", required=False, help="登录密码（可选）")
    parser.add_argument(
        "--ship-model",
        default="DL-3022",
        help="上传时附带的 shipModel，用于历史记录归档"
    )
    parser.add_argument(
        "--ship-port",
        type=int,
        default=9001,
        help="上传时附带的 shipPort，用于服务端按端口映射设备型号，默认 9001"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="递归扫描子目录"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="仅上传前 N 张，0 表示不限制"
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="HTTPS 时校验证书（默认关闭，便于自签证书测试）"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="单次请求超时秒数，默认 20"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将上传的文件，不真正请求"
    )
    parser.add_argument(
        "--check-history",
        action="store_true",
        help="上传后拉取一次图像历史列表，快速确认入库"
    )
    return parser.parse_args()


def find_images(root: Path, recursive: bool) -> list[Path]:
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"图片目录不存在: {root}")

    iterator: Iterable[Path]
    if recursive:
        iterator = root.rglob("*")
    else:
        iterator = root.glob("*")

    files = [p for p in iterator if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    files.sort()
    return files


def login(base_url: str, username: str, password: str, timeout: int, verify_ssl: bool) -> str:
    url = f"{base_url.rstrip('/')}/login/"
    payload = {"userName": username, "password": password}

    try:
        resp = requests.post(url, json=payload, timeout=timeout, verify=verify_ssl)
    except requests.RequestException as exc:
        raise RuntimeError(f"登录请求失败: {exc}") from exc

    if resp.status_code != 200:
        raise RuntimeError(f"登录失败 HTTP {resp.status_code}: {resp.text}")

    body = resp.json()
    token = ((body.get("data") or {}).get("token"))
    if not token:
        raise RuntimeError(f"登录返回中未找到 token: {json.dumps(body, ensure_ascii=False)}")

    return token


def upload_one(
    base_url: str,
    token: Optional[str],
    image_path: Path,
    ship_model: str,
    ship_port: int,
    timeout: int,
    verify_ssl: bool,
) -> tuple[bool, str]:
    url = f"{base_url.rstrip('/')}/drone/upload-image/"
    content_type = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"

    with image_path.open("rb") as f:
        files = {"file": (image_path.name, f, content_type)}
        data = {"shipModel": ship_model, "shipPort": str(ship_port)}
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            resp = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=timeout,
                verify=verify_ssl,
            )
        except requests.RequestException as exc:
            return False, f"请求失败: {exc}"

    if resp.status_code != 200:
        return False, f"HTTP {resp.status_code}: {resp.text}"

    try:
        body = resp.json()
    except ValueError:
        return False, f"响应不是 JSON: {resp.text}"

    if body.get("code") != 200:
        return False, f"业务失败 code={body.get('code')}, msg={body.get('msg')}"

    image_uid = (body.get("data") or {}).get("imageUid", "")
    image_url = (body.get("data") or {}).get("url", "")
    return True, f"imageUid={image_uid} url={image_url}"


def check_history(base_url: str, token: str, timeout: int, verify_ssl: bool) -> None:
    url = f"{base_url.rstrip('/')}/drone/image-history/list/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"current": 1, "size": 5}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout, verify=verify_ssl)
    except requests.RequestException as exc:
        print(f"[WARN] 拉取历史列表失败: {exc}")
        return

    if resp.status_code != 200:
        print(f"[WARN] 拉取历史列表 HTTP {resp.status_code}: {resp.text}")
        return

    try:
        body = resp.json()
    except ValueError:
        print(f"[WARN] 历史列表响应不是 JSON: {resp.text}")
        return

    records = ((body.get("data") or {}).get("records") or [])
    total = (body.get("data") or {}).get("total")
    print(f"\n[INFO] 历史记录总数: {total}, 最近返回 {len(records)} 条")
    for i, item in enumerate(records, start=1):
        print(
            f"  {i}. {item.get('imageUid')} | {item.get('shipModel')} | "
            f"{item.get('timestamp')} | {item.get('imageFormat')}"
        )


def main() -> int:
    args = parse_args()
    image_dir = Path(os.path.expanduser(args.image_dir)).resolve()

    try:
        image_files = find_images(image_dir, args.recursive)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.limit > 0:
        image_files = image_files[: args.limit]

    if not image_files:
        print(f"[ERROR] 未在目录中找到可上传图片: {image_dir}")
        return 1

    print(f"[INFO] 目标接口: {args.base_url.rstrip('/')}/drone/upload-image/")
    print(f"[INFO] 图片目录: {image_dir}")
    print(f"[INFO] 发现图片: {len(image_files)} 张")

    if args.dry_run:
        for p in image_files:
            print(f"[DRY] {p}")
        return 0

    token: Optional[str] = None
    if args.username or args.password:
        if not args.username or not args.password:
            print("[ERROR] --username 和 --password 需同时提供，或都不提供（匿名上传）")
            return 1

        try:
            token = login(
                base_url=args.base_url,
                username=args.username,
                password=args.password,
                timeout=args.timeout,
                verify_ssl=args.verify_ssl,
            )
        except RuntimeError as exc:
            print(f"[ERROR] {exc}")
            return 1
    else:
        print("[INFO] 未提供账号密码，将按匿名模式上传")

    ok_count = 0
    fail_count = 0

    for idx, image_path in enumerate(image_files, start=1):
        ok, msg = upload_one(
            base_url=args.base_url,
            token=token,
            image_path=image_path,
            ship_model=args.ship_model,
            ship_port=args.ship_port,
            timeout=args.timeout,
            verify_ssl=args.verify_ssl,
        )
        if ok:
            ok_count += 1
            print(f"[OK {idx}/{len(image_files)}] {image_path.name} -> {msg}")
        else:
            fail_count += 1
            print(f"[FAIL {idx}/{len(image_files)}] {image_path.name} -> {msg}")

    print("\n========== 上传结果 ==========")
    print(f"成功: {ok_count}")
    print(f"失败: {fail_count}")
    print(f"总计: {len(image_files)}")

    if args.check_history:
        if not token:
            print("[WARN] 匿名模式无法拉取历史列表（该接口需要认证），跳过")
            return 0 if fail_count == 0 else 2
        check_history(
            base_url=args.base_url,
            token=token,
            timeout=args.timeout,
            verify_ssl=args.verify_ssl,
        )

    return 0 if fail_count == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
