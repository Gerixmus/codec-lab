import pandas as pd
import matplotlib.pyplot as plt
import re

df = pd.read_csv("output/results.csv")

def extract_number(filename):
    match = re.search(r"(\d+)-trim", filename)
    if match:
        return match.group(1)
    return filename
df["video_id"] = df["input_file"].apply(extract_number)
df["label"] = df.apply(lambda row: f"{row['video_id']}{row['preset']}{row['qp']}", axis=1)
df = df.sort_values(by="label")

df["encoding_time_per_s"] = df["encoding_time_s"] / df["duration"]
df["co2_per_s"] = df["co2_kg"] / df["duration"]

df["encoding_time_per_vmaf"] = df["encoding_time_s"] / df["vmaf_mean"]
df["co2_per_vmaf"] = df["co2_kg"] / df["vmaf_mean"]

plt.figure(figsize=(14, 8))

plt.subplot(3, 1, 1)
plt.bar(df["label"], df["encoding_time_per_s"])
plt.title("Encoding Time per Second of Video")
plt.ylabel("sec/sec")

plt.subplot(3, 1, 2)
plt.bar(df["label"], df["co2_per_s"])
plt.title("CO2 Emissions per Second of Video")
plt.ylabel("kg/sec")

plt.subplot(3, 1, 3)
plt.bar(df["label"], df["encoding_time_per_vmaf"])
plt.title("Encoding Time per VMAF Point")
plt.ylabel("seconds per VMAF")

plt.tight_layout()
plt.show()