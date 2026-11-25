import asyncio, json, time
from pathlib import Path
import edge_tts

OUT_DIR = Path("outputs/ceiling_lang_test")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TESTS = [
    {
        "lang": "Somali (native voice)",
        "voice": "so-SO-MuuseNeural",
        "file": "shot01_somali.mp3",
        "text": "Subaxdii Ciidda Masiixiga ee 1975-kii magaalada Addis Ababa, qorraxda qabow ayaa ka soo baxday Gotera."
    },
    {
        "lang": "Tigrinya (cross-lingual via Amharic voice)",
        "voice": "am-ET-AmehaNeural",
        "file": "shot01_tigrinya_via_amharic.mp3",
        "text": "ኣብ 1975 ዓ.ም. ንግሆ ልደት ኣብ ኣዲስ ኣበባ፡ ዝሑል ጸሓይ ኣብ ጎተራ በረቐት።"
    },
    {
        "lang": "Afaan Oromo (cross-lingual via Somali voice)",
        "voice": "so-SO-MuuseNeural",
        "file": "shot01_oromo_via_somali.mp3",
        "text": "Ganama Ayyaana Qillee bara 1975 magaalaa Finfinneetti, aduun qorraan Goteraa irratti baate."
    },
]

async def run():
    # 1. Check which Ethiopian/Horn languages exist natively in edge-tts
    voices = await edge_tts.list_voices()
    found = [v["ShortName"] for v in voices if v["Locale"].startswith(("am-", "so-", "om-", "ti-"))]
    print("Native voices found in edge-tts:", found)

    # 2. Run the 3 tests and log to runs.jsonl
    for t in TESTS:
        start = time.time()
        out_path = OUT_DIR / t["file"]
        comm = edge_tts.Communicate(t["text"], voice=t["voice"], rate="-5%")
        await comm.save(str(out_path))
        latency = round(time.time() - start, 2)
        print(f"[OK] {t['lang']} -> {out_path} ({latency}s)")

        log_entry = {
            "stage": "ceiling_lang_test",
            "language": t["lang"],
            "model": f"edge-tts/{t['voice']}",
            "latency_sec": latency,
            "estimated_cost_usd": 0.0,
            "output": str(out_path),
            "cached": False
        }
        with open("runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

asyncio.run(run())