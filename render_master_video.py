import os
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using FFmpeg binary: {ffmpeg_exe}")

os.makedirs("video-production/renders", exist_ok=True)
os.makedirs("video-production/footage", exist_ok=True)

W, H = 1920, 1080

from generate_master_voiceovers import scenes_master

def render_master_video():
    with open("video-production/voiceover/master_metadata.json", "r") as f:
        meta = json.load(f)
    durations = meta["durations"]

    scene_video_parts = []
    current_time = 0.0
    timeline = []
    srt_entries = []
    timing_lines = []
    srt_index = 1

    def format_ts(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milli = int(round((seconds - int(seconds)) * 1000))
        if milli >= 1000:
            secs += 1
            milli = 0
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

    for idx, sc in enumerate(scenes_master):
        sid = sc["id"]
        dur = durations[sid]
        start_ts = current_time
        end_ts = current_time + dur
        
        timeline.append({
            "scene_id": sid,
            "title": sc["title"],
            "tag": sc["tag"],
            "start_time": start_ts,
            "end_time": end_ts,
            "duration": dur,
            "text": sc["text"]
        })
        
        timing_lines.append(f"[{format_ts(start_ts)} --> {format_ts(end_ts)}] {sid.upper()} ({sc['title']})")
        timing_lines.append(f"Text: {sc['text']}\n")
        
        # Subtitles breakdown
        sentences = [sent.strip() for sent in sc["text"].replace("!", ".").replace("?", ".").split(".") if sent.strip()]
        if not sentences:
            sentences = [sc["text"]]
        sent_dur = dur / len(sentences)
        for i, sent in enumerate(sentences):
            sub_start = start_ts + i * sent_dur
            sub_end = start_ts + (i + 1) * sent_dur
            srt_entries.append(f"{srt_index}\n{format_ts(sub_start)} --> {format_ts(sub_end)}\n{sent}\n")
            srt_index += 1

        print(f"Compositing master {sid} (Duration: {dur:.2f}s)...")
        canvas = Image.new("RGBA", (W, H), (15, 23, 42, 255))
        
        # If graphic or UI screenshot
        vfile = sc["visual_file"]
        if os.path.exists(vfile):
            base_img = Image.open(vfile).convert("RGBA")
            if sc["visual_type"] == "graphic":
                # Clean graphic slide fits canvas directly
                canvas.paste(base_img, (0, 0))
            else:
                # UI screenshot framed neatly
                ui_scaled = base_img.resize((1840, 900))
                canvas.paste(ui_scaled, (40, 140))
                # Add header and footer for UI slides
                draw = ImageDraw.Draw(canvas)
                draw.rectangle([0, 0, W, 130], fill=(15, 23, 42, 245))
                draw.rectangle([0, 126, W, 130], fill=(16, 185, 129, 255))
                draw.rounded_rectangle([40, 25, 340, 65], radius=8, fill=(30, 41, 59, 255), outline=(52, 211, 153, 255), width=2)
                draw.text((55, 36), sc["tag"], fill=(52, 211, 153, 255))
                draw.text((360, 25), sc["title"], fill=(255, 255, 255, 255))
                draw.text((360, 75), "SafeWalk (RaahSaathi) | Presented by Prince Pundir", fill=(148, 163, 184, 255))
                draw.rectangle([0, H - 75, W, H], fill=(15, 23, 42, 240))
                draw.text((60, H - 52), sc["pill"], fill=(241, 245, 249, 255))
                draw.text((W - 380, H - 52), f"Scene {idx+1}/8 | SafeWalk", fill=(148, 163, 184, 255))

        frame_path = f"video-production/footage/{sid}_master_frame.png"
        canvas.convert("RGB").save(frame_path, "PNG")

        out_part = f"video-production/renders/{sid}_master.mp4"
        audio_path = f"video-production/voiceover/{sid}_master.mp3"

        # Encode part with 30fps and AAC audio
        cmd = [
            ffmpeg_exe,
            "-y",
            "-loop", "1",
            "-i", frame_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-r", "30",
            out_part
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print(f"Error encoding {sid}:", res.stderr.decode()[:300])
        else:
            print(f"Rendered {out_part}")
            scene_video_parts.append(out_part)

        current_time = end_ts

    # Save Subtitles & Timeline
    with open("scene_timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    with open("video-production/scene_timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    with open("final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("video-production/final_demo_subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    with open("video-production/voiceover/voiceover_timing.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(timing_lines))

    # Concat all into final_demo_video.mp4
    print("Concatenating master parts into final_demo_video.mp4 ...")
    concat_list = "video-production/renders/master_concat_list.txt"
    with open(concat_list, "w") as f:
        for p in scene_video_parts:
            abs_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    final_video = "final_demo_video.mp4"
    cmd_concat = [
        ffmpeg_exe,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        final_video
    ]
    res = subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"SUCCESS: Master video {final_video} generated!")
    else:
        print("Concat error:", res.stderr.decode()[:300])

if __name__ == "__main__":
    render_master_video()
