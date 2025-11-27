import subprocess
from codecarbon import EmissionsTracker
import time
import os
import json
import csv


# files = os.listdir("input")
settings = {
  "faster": 63,
  "fast": 48,
  "medium": 32,
  "slow": 16,
  "slower": 0
}

# for i in files:
for preset, qp in settings.items():
    # qp = 63
    # preset = "faster" 

    # qp = 24
    # preset = "medium"
    input_file = "input/4.mp4"
    # input_file = f"input/{i}"
    csv_path = "output/results-coverage.csv"
    file_name = os.path.basename(input_file)
    #TODO generate output folder 
    base, ext = os.path.splitext(file_name)
    vmaf_json = f"output/vmaf-{base}-out-qp{qp}-preset{preset}.json"
    output_file = f"output/{base}-out-qp{qp}-preset{preset}.mkv"
    
    # trims to 5 seconds and sets input to the trimmed file
    # subprocess.run([
    #     "ffmpeg", "-y",
    #     "-i", input_file,
    #     "-t", "5",
    #     "-c", "copy",
    #     f"output/{base}-trim{ext}"
    # ])
    # input_file = f"output/{base}-trim{ext}"
    
    duration = subprocess.run([
        "ffprobe",
        "-i", input_file,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=p=0"
    ],  capture_output=True, text=True).stdout.strip()


    cmd = [
        "ffmpeg",
        "-i", f"{input_file}",
        "-c:v", "libvvenc",
        "-preset", f"{preset}",
        "-period", "10",
        "-qp", f"{qp}",
        "-c:a", "copy",
        f"{output_file}"
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
        "qp",
        "preset",
        "encoding_time_s",
        "co2_kg",
        "vmaf_mean"
    ]

    row = [
        file_name,
        duration,
        "libvvenc",
        qp,
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