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

plt.figure(figsize=(14, 8))

plt.subplot(3, 1, 1)
plt.bar(df["label"], df["encoding_time_s"])
plt.title("Encoding Time (seconds)")
plt.ylabel("Seconds")
plt.xticks(rotation=45, ha="right")

plt.subplot(3, 1, 2)
plt.bar(df["label"], df["co2_kg"])
plt.title("CO₂ Emissions (kg)")
plt.ylabel("kg")
plt.xticks(rotation=45, ha="right")

plt.subplot(3, 1, 3)
plt.bar(df["label"], df["vmaf_mean"])
plt.title("VMAF Score")
plt.ylabel("VMAF")
plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.show()
