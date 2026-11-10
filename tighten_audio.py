import asyncio
import os
import edge_tts
from generate_master_voiceovers import scenes_master

async def tighten():
    voice = "en-IN-PrabhatNeural"
    # Setting rate to +18% achieves the exact 4m 30s target (4.5 min) with crisp, fluent delivery
    for s in scenes_master:
        path = f"video-production/voiceover/{s['id']}_master.mp3"
        print(f"Generating {path} at +18%...")
        comm = edge_tts.Communicate(s['text'], voice, rate="+18%")
        await comm.save(path)
    print("ALL_TIGHTENED_DONE")

if __name__ == "__main__":
    asyncio.run(tighten())
