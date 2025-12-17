import subprocess
from codecarbon import EmissionsTracker
import time
import os
import json
import csv


files = os.listdir("input")
settings = {
    "slower": 0,
    "slow": 1,
    "medium": 3,
    "fast": 5,
    "faster": 8 
}

for i in files:
    preset = "medium"
    crf = 10
    input_file = f"input/{i}"
    csv_path = "output/results-coverage.csv"
    file_name = os.path.basename(input_file)
    base, ext = os.path.splitext(file_name)
    vmaf_json = f"output/vmaf-{base}-crf{crf}-preset{preset}.json"
    output_file = f"output/{base}-crf{crf}-preset{preset}.webm"
    
    duration = subprocess.run([
        "ffprobe",
        "-i", input_file,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0"
    ],  capture_output=True, text=True).stdout.strip()


    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libvpx",
        "-crf", str(crf),
        "-b:v", "0",
        "-deadline", "good",
        "-cpu-used", str(settings[preset]),
        "-row-mt", "1",
        "-threads", "8",
        "-r", "60",
        "-pix_fmt", "yuv420p",
        "-c:a", "libopus",
        "-b:a", "128k",
        output_file
    ]

    vmaf_cmd = [
        "ffmpeg",
        "-i", f"{input_file}",
        "-i", f"{output_file}",
        "-lavfi", f"libvmaf=log_fmt=json:log_path={vmaf_json}",
        "-f", "null",
        "-"
    ]

    tracker = EmissionsTracker(save_to_file=False)
    tracker.start()

    start = time.time()
    subprocess.run(cmd)
    end = time.time()

    encoding_time = end - start

    emissions = tracker.stop()

    subprocess.run(vmaf_cmd)

    if os.path.exists(vmaf_json):
        with open(vmaf_json, "r") as f:
            data = json.load(f)
            vmaf_mean = data["pooled_metrics"]["vmaf"]["mean"]
    else:
        vmaf_mean = None

    print("Encoding time:", encoding_time)
    print("Emissions:", emissions)
    print("VMAF:", vmaf_mean)

    header = [
        "input_file",
        "duration",
        "encoder",
        "crf",
        "preset",
        "encoding_time_s",
        "co2_kg",
        "vmaf_mean"
    ]

    row = [
        file_name,
        duration,
        "libvvenc",
        crf,
        preset,
        encoding_time,
        emissions,
        vmaf_mean
    ]

    write_header = not os.path.exists(csv_path)

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)

    print("Saved results to", csv_path)