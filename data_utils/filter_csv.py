import pandas as pd

# CSV dosyasının yolu
file_path = 'data/train.csv'

# Tutulacak etiketler (sadece bu etiketler ve 'O' dosyada kalacak)
target_tags = [
    "B-PERSON", "I-PERSON",
    "B-ORG", "I-ORG",
    "B-DATE", "I-DATE",
    "B-TCNO", "I-TCNO",
    "B-PHONE", "I-PHONE",
    "O"
]

# Çıktı dosyası için başlıklar
header_names = ['sentence_id', 'token', 'label']

# CSV dosyasını oku
try:
    df = pd.read_csv(file_path, header=None, names=['sentence_id', 'token', 'label'])
except pd.errors.EmptyDataError:
    print(f"Girdi dosyası {file_path} boş. Sadece başlık ile üzerine yazılacak.")
    df = pd.DataFrame(columns=['sentence_id', 'token', 'label'])
except FileNotFoundError:
    print(f"{file_path} bulunamadı. Çıktı oluşturulmayacak.")
    exit()

# 'label' sütununun tipini string olarak ayarla
df['label'] = df['label'].astype(str)

# Sadece target_tags ve 'O' etiketlerine sahip satırları tut
df_filtered = df[df['label'].isin(target_tags)].copy()

# Çıktı dosyasının yolu (orijinal dosyanın üzerine yazar)
output_file_path = 'data/train.csv'

# Sonucu CSV dosyasına yaz (başlıklarla ve index olmadan)
df_filtered.to_csv(output_file_path, index=False, header=header_names)

print(f"İşlem tamamlandı. Sadece belirtilen etiketlere ve 'O' etiketine sahip satırlar {output_file_path} dosyasına kaydedildi.") 