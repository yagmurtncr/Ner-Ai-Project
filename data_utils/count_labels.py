import csv
from collections import Counter

target_labels = ["DATE", "ORG", "TCNO", "PHONE", "PERSON"]
label_counter = Counter()

with open("raw_data/balanced_test_dataset.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        label = row.get("label")
        if not label:
            continue  # label boşsa veya None ise atla
        if label.startswith("B-"):
            label_type = label.split("-", 1)[1]
            if label_type in target_labels:
                label_counter[label_type] += 1

print("Etiket sayıları:")
for label in target_labels:
    print(f"{label}: {label_counter[label]}")
