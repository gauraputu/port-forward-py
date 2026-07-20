import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".port-forward"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class ForwardEntry:
    name: str
    local_port: int
    remote_host: str
    remote_port: int
    target_host: str = "localhost"
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "local_port": self.local_port,
            "remote_host": self.remote_host,
            "remote_port": self.remote_port,
            "target_host": self.target_host,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ForwardEntry":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data["name"],
            local_port=data["local_port"],
            remote_host=data["remote_host"],
            remote_port=data["remote_port"],
            target_host=data.get("target_host", "localhost"),
        )


def load_entries() -> list[ForwardEntry]:
    if not CONFIG_FILE.exists():
        return []
    with open(CONFIG_FILE) as f:
        raw = json.load(f)
    return [ForwardEntry.from_dict(item) for item in raw]


def save_entries(entries: list[ForwardEntry]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = [e.to_dict() for e in entries]
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)