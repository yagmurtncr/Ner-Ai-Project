import csv

def conll_to_csv(conll_file, csv_file):
    with open(conll_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = []
    sentence_id = 1

    for line in lines:
        line = line.strip()
        if not line:
            sentence_id += 1
            continue
        parts = line.split()
        if len(parts) >= 2:
            token = parts[0]
            label = parts[-1]
            data.append([sentence_id, token, label])

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sentence_id', 'token', 'label'])
        writer.writerows(data)

    print(f"CSV dosyası başarıyla oluşturuldu: {csv_file}")

# Kullanım örneği
conll_to_csv('train.conll', 'train.csv')

