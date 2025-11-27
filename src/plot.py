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

# 1. Encoding Time
plt.subplot(3, 1, 1)
bars = plt.bar(df["label"], df["encoding_time_s"], color='skyblue')
plt.title("Encoding Time (seconds)")
plt.ylabel("Seconds")
plt.xticks(rotation=45, ha="right")
for bar, val in zip(bars, df["encoding_time_s"]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
             f"{val:.2f}", ha='center', va='bottom', fontsize=9)

# 2. CO2
plt.subplot(3, 1, 2)
bars = plt.bar(df["label"], df["co2_kg"], color='lightgreen')
plt.title("CO₂ Emissions (kg)")
plt.ylabel("kg")
plt.xticks(rotation=45, ha="right")
for bar, val in zip(bars, df["co2_kg"]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
             f"{val:.5f}", ha='center', va='bottom', fontsize=9)

# 3. VMAF
plt.subplot(3, 1, 3)
bars = plt.bar(df["label"], df["vmaf_mean"], color='salmon')
plt.title("VMAF Score")
plt.ylabel("VMAF")
plt.xticks(rotation=45, ha="right")
for bar, val in zip(bars, df["vmaf_mean"]):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
             f"{val:.1f}", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()