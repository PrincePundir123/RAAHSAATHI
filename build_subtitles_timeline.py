import asyncio
import os
import json
import edge_tts

# We will run Communicate and listen to word boundary events or stream to get exact timings
# Then format to standard .srt and timing file.

from generate_voiceovers_concise import scenes_concise

def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milli = int(round((seconds - int(seconds)) * 1000))
    if milli >= 1000:
        secs += 1
        milli = 0
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

async def main():
    voice = "en-IN-PrabhatNeural"
    with open("video-production/voiceover/voiceover_metadata.json", "r") as f:
        meta = json.load(f)
    durations = meta["durations"]
    
    current_time = 0.0
    timeline = []
    srt_entries = []
    timing_lines = []
    srt_index = 1

    for s in scenes_concise:
        sid = s["id"]
        dur = durations[sid]
        start = current_time
        end = current_time + dur
        
        timeline.append({
            "scene_id": sid,
            "title": s["title"],
            "start_time": start,
            "end_time": end,
            "duration": dur,
            "text": s["text"]
        })
        
        timing_lines.append(f"[{format_timestamp(start)} --> {format_timestamp(end)}] {sid.upper()} ({s['title']})")
        timing_lines.append(f"Text: {s['text']}\n")
        
        # Break text into 3-4 natural subtitle sentences
        sentences = [sent.strip() for sent in s["text"].replace("!", ".").replace("?", ".").split(".") if sent.strip()]
        if not sentences:
            sentences = [s["text"]]
        
        sent_dur = dur / len(sentences)
        for i, sent in enumerate(sentences):
            sub_start = start + i * sent_dur
            sub_end = start + (i + 1) * sent_dur
            srt_entries.append(f"{srt_index}\n{format_timestamp(sub_start)} --> {format_timestamp(sub_end)}\n{sent}\n")
            srt_index += 1
            
        current_time = end

    # Write scene_timeline.json
    with open("scene_timeline.json", "w") as f:
        json.dump(timeline, f, indent=2)
    with open("video-production/scene_timeline.json", "w") as f:
        json.dump(timeline, f, indent=2)
        
    # Write final_demo_subtitles.srt
    with open("final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("video-production/final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
        
    # Write voiceover_timing.txt
    with open("video-production/voiceover/voiceover_timing.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(timing_lines))

    print("Subtitles, timeline, and timing files written successfully!")

if __name__ == "__main__":
    asyncio.run(main())

