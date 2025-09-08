import csv
import random
from collections import defaultdict

input_file = "raw_data/balanced_dev_dataset.csv"
output_file = "raw_data/balanced_dev2_dataset.csv"
target_labels = ["DATE", "ORG", "TCNO", "PHONE", "PERSON"]
target_b_count = 265  # Her etiket için hedeflenen B-token sayısı

# Cümleleri yükle
sentences = defaultdict(list)
with open(input_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 3:
            continue
        sid, token, label = row
        sentences[sid].append((token, label))

# Her etiketten B-token sayısı hedefini karşılayan cümleleri seç
label_to_sentences = defaultdict(list)

for sid, tokens in sentences.items():
    b_labels = defaultdict(int)
    for _, label in tokens:
        if label.startswith("B-"):
            entity = label.split("-", 1)[1]
            if entity in target_labels:
                b_labels[entity] += 1

    if len(b_labels) == 1:  # Cümle sadece bir etiket içeriyorsa
        label = next(iter(b_labels))
        count = b_labels[label]
        label_to_sentences[label].append((sid, tokens, count))


selected = []
used_sids = set()

for label in target_labels:
    sents = label_to_sentences[label]
    random.shuffle(sents)
    
    current_b_count = 0
    label_selected = []

    for sid, tokens, b_count in sents:
        if sid in used_sids:
            continue
        if current_b_count + b_count > target_b_count:
            continue
        label_selected.append((sid, tokens))
        used_sids.add(sid)
        current_b_count += b_count
        if current_b_count == target_b_count:
            break

    if current_b_count < target_b_count:
        raise ValueError(f"{label} etiketi için yeterli B-token bulunamadı. Bulunan: {current_b_count}")

    selected.extend(label_selected)

# Yeni sentence_id ile çıktıya yaz
with open(output_file, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["sentence_id", "token", "label"])
    for new_sid, (old_sid, tokens) in enumerate(selected, 1):
        for token, label in tokens:
            writer.writerow([new_sid, token, label])

print("✔ Her etiket için tam 263 B-token içeren cümleler seçildi ve yazıldı.")
