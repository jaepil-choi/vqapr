"""Measure one command's elapsed time, CPU, and process-tree peak memory."""

from __future__ import annotations

import argparse
import json
import subprocess
import threading
import time
from pathlib import Path

import psutil


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    stdout_path = args.output.with_suffix(".stdout.txt")
    started = time.perf_counter()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    peak_rss = 0
    peak_private = 0
    cpu_user = 0.0
    cpu_system = 0.0
    done = threading.Event()

    def sample() -> None:
        nonlocal peak_rss, peak_private, cpu_user, cpu_system
        try:
            root = psutil.Process(process.pid)
        except psutil.Error:
            return
        while not done.wait(0.1):
            try:
                tree = [root, *root.children(recursive=True)]
            except psutil.Error:
                continue
            rss = private = user = system = 0.0
            for member in tree:
                try:
                    memory = member.memory_info()
                    rss += memory.rss
                    try:
                        full = member.memory_full_info()
                    except psutil.Error:
                        full = memory
                    private += getattr(full, "uss", getattr(full, "private", memory.rss))
                    cpu = member.cpu_times()
                    user += cpu.user
                    system += cpu.system
                except psutil.Error:
                    continue
            peak_rss = max(peak_rss, int(rss))
            peak_private = max(peak_private, int(private))
            cpu_user = max(cpu_user, user)
            cpu_system = max(cpu_system, system)

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    stdout, _ = process.communicate()
    done.set()
    sampler.join()
    elapsed = time.perf_counter() - started
    stdout_path.write_bytes(stdout)
    result = {
        "label": args.label,
        "command": command,
        "returncode": process.returncode,
        "wall_s": round(elapsed, 3),
        "cpu_user_s": round(cpu_user, 3),
        "cpu_system_s": round(cpu_system, 3),
        "peak_rss_bytes": peak_rss,
        "peak_private_bytes": peak_private,
        "stdout": str(stdout_path),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(process.returncode)


if __name__ == "__main__":
    main()
