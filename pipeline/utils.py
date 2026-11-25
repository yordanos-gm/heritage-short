import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
RUNS_LOG = ROOT_DIR / "runs.jsonl"


def ensure_dirs():
    for sub in ["narration", "keyframes", "shots", "music", "radio_cut", "final"]:
        (OUTPUTS_DIR / sub).mkdir(parents=True, exist_ok=True)


def load_storyboard() -> dict:
    with open(ROOT_DIR / "storyboard.json", "r", encoding="utf-8") as f:
        return json.load(f)


def compute_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def is_cached(artifact_path: Path, meta_path: Path, expected_hash: str) -> bool:
    if not artifact_path.exists() or not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return meta.get("hash") == expected_hash
    except Exception:
        return False


def write_cache_meta(meta_path: Path, expected_hash: str, extra: dict | None = None):
    data = {"hash": expected_hash, "updated_at": datetime.now(timezone.utc).isoformat()}
    if extra:
        data.update(extra)
    meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def log_run(
    stage: str,
    shot_id: int | str,
    model: str,
    params: dict,
    seed: int | None,
    latency_sec: float,
    cost_usd: float = 0.0,
    status: str = "ok",
    cached: bool = False,
):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "shot_id": shot_id,
        "model": model,
        "params": params,
        "seed": seed,
        "latency_sec": round(latency_sec, 3),
        "cost_usd": cost_usd,
        "status": status,
        "cached": cached,
    }
    with open(RUNS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")