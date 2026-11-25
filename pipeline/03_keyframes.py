import base64
import os
import time
import requests
from pathlib import Path
from pipeline.utils import (
    OUTPUTS_DIR,
    compute_hash,
    ensure_dirs,
    is_cached,
    load_storyboard,
    log_run,
    write_cache_meta,
)

CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"


def call_flux(account_id: str, token: str, prompt: str, steps: int = 4) -> bytes:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{CF_MODEL}"
    headers = {"Authorization": f"Bearer {token}"}
    # Cloudflare flux-1-schnell only accepts prompt and steps (1-8)
    payload = {
        "prompt": prompt,
        "steps": steps,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        data = resp.json()
        b64_img = data.get("result", {}).get("image")
        if not b64_img:
            raise RuntimeError(f"Unexpected Cloudflare response: {data}")
        return base64.b64decode(b64_img)
    return resp.content


def generate_reference_sheet(account_id: str, token: str, sb: dict) -> Path:
    ref_prompt = f"{sb['character_sheet_prompt']}, {sb['style_block']}"
    cache_key = compute_hash({"model": CF_MODEL, "prompt": ref_prompt, "steps": 4})
    out_dir = OUTPUTS_DIR / "keyframes"
    img_path = out_dir / "reference_sheet.png"
    meta_path = out_dir / "reference_sheet.json"

    if is_cached(img_path, meta_path, cache_key):
        print("[CACHE] Character reference sheet unchanged.")
        log_run("keyframes", "ref", CF_MODEL, {"steps": 4}, None, 0.0, 0.0, "cached", True)
        return img_path

    print("[GEN] Generating 1975 character & style reference sheet...")
    t0 = time.perf_counter()
    img_bytes = call_flux(account_id, token, ref_prompt, steps=4)
    img_path.write_bytes(img_bytes)
    latency = time.perf_counter() - t0
    write_cache_meta(meta_path, cache_key, {"prompt": ref_prompt, "steps": 4})
    log_run("keyframes", "ref", CF_MODEL, {"steps": 4}, None, latency, 0.0, "ok", False)
    print(f"[OK] Saved reference_sheet.png ({latency:.2f}s).")
    return img_path


def generate_shot_keyframe(account_id: str, token: str, shot: dict, style_block: str, ref_hash: str) -> Path:
    shot_id = shot["shot_id"]
    seed = shot["seed"]
    full_prompt = (
        f"{shot['image_prompt']}, featuring the young Ethiopian boy and 1975 family style, "
        f"subject centered in frame, {style_block}"
    )
    cache_key = compute_hash({
        "model": CF_MODEL,
        "prompt": full_prompt,
        "seed": seed,
        "ref_hash": ref_hash,
        "steps": 4,
    })

    out_dir = OUTPUTS_DIR / "keyframes"
    img_path = out_dir / f"shot_{shot_id:02d}.png"
    meta_path = out_dir / f"shot_{shot_id:02d}.json"

    if is_cached(img_path, meta_path, cache_key):
        print(f"[CACHE] Shot {shot_id:02d} keyframe unchanged.")
        log_run("keyframes", shot_id, CF_MODEL, {"steps": 4}, seed, 0.0, 0.0, "cached", True)
        return img_path

    print(f"[GEN] Generating keyframe for Shot {shot_id:02d}...")
    t0 = time.perf_counter()
    last_err = None
    for attempt in range(1, 4):
        try:
            img_bytes = call_flux(account_id, token, full_prompt, steps=4)
            img_path.write_bytes(img_bytes)
            latency = time.perf_counter() - t0
            write_cache_meta(meta_path, cache_key, {"prompt": full_prompt, "seed": seed, "steps": 4})
            log_run("keyframes", shot_id, CF_MODEL, {"steps": 4, "attempt": attempt}, seed, latency, 0.0, "ok", False)
            print(f"[OK] Shot {shot_id:02d} keyframe saved ({latency:.2f}s).")
            return img_path
        except Exception as e:
            last_err = e
            print(f"[WARN] Attempt {attempt} failed for Shot {shot_id:02d}: {e}")
            time.sleep(2 * attempt)

    latency = time.perf_counter() - t0
    log_run("keyframes", shot_id, CF_MODEL, {"steps": 4, "error": str(last_err)}, seed, latency, 0.0, "error", False)
    raise RuntimeError(f"Keyframe failed for Shot {shot_id}: {last_err}")


def main():
    ensure_dirs()
    acc_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not acc_id or not token or "PASTE_" in acc_id or "PASTE_" in token:
        raise ValueError("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in .env first!")

    sb = load_storyboard()
    ref_path = generate_reference_sheet(acc_id, token, sb)
    ref_hash = compute_hash({"ref_file": str(ref_path), "prompt": sb["character_sheet_prompt"]})

    for shot in sb["shots"]:
        generate_shot_keyframe(acc_id, token, shot, sb["style_block"], ref_hash)


if __name__ == "__main__":
    main()