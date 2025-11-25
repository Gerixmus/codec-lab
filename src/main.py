import subprocess
from codecarbon import EmissionsTracker
import time
import os
import json
import csv

qp = 63
preset = "fast" 
# qp = 24
# preset = "medium"
input_file = "input/6.mp4"
csv_path = "output/results.csv"
file_name = filename = os.path.basename(input_file)

base, ext = os.path.splitext(file_name)
vmaf_json = f"output/vmaf-{base}-out-qp{qp}-preset{preset}.json"
output_file = f"output/{base}-out-qp{qp}-preset{preset}{ext}"

subprocess.run([
    "ffmpeg", "-y",
    "-i", input_file,
    "-t", "5",
    "-c", "copy",
    f"output/{base}-trim{ext}"
])
input_file = f"output/{base}-trim{ext}"

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
    "encoder",
    "qp",
    "preset",
    "encoding_time_s",
    "co2_kg",
    "vmaf_mean"
]

row = [
    file_name,
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