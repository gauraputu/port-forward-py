import os
import signal
import subprocess
import time
from typing import Optional


class TunnelManager:
    def __init__(self):
        self._processes: dict[str, subprocess.Popen] = {}

    def start(self, entry) -> tuple[bool, Optional[str]]:
        if entry.id in self._processes and self.is_running(entry.id):
            return True, None

        prev = self._processes.pop(entry.id, None)
        if prev is not None:
            self._kill(prev)

        cmd = [
            "ssh",
            "-o", "ExitOnForwardFailure=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-N",
            "-L", f"{entry.local_port}:localhost:{entry.remote_port}",
            entry.remote_host,
        ]

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                preexec_fn=os.setpgrp,
            )
        except FileNotFoundError:
            return False, "ssh command not found"

        self._processes[entry.id] = proc

        time.sleep(0.3)
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode(errors="replace").strip()
            self._processes.pop(entry.id, None)
            return False, stderr or f"SSH exited code {proc.returncode}"

        return True, None

    def stop(self, entry_id: str) -> None:
        proc = self._processes.pop(entry_id, None)
        if proc is not None:
            self._kill(proc)

    def stop_all(self) -> None:
        for entry_id in list(self._processes.keys()):
            self.stop(entry_id)

    def is_running(self, entry_id: str) -> bool:
        proc = self._processes.get(entry_id)
        if proc is None:
            return False
        return proc.poll() is None

    def get_error(self, entry_id: str) -> Optional[str]:
        proc = self._processes.get(entry_id)
        if proc is None or proc.poll() is None:
            return None
        stderr = proc.stderr.read().decode(errors="replace").strip()
        return stderr if stderr else f"SSH exited with code {proc.returncode}"

    def _kill(self, proc: subprocess.Popen) -> None:
        if proc.poll() is not None:
            return
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()