import random
import re

def generate_phone_number():
    prefix = f"05{random.randint(30, 59)}"
    part1 = f"{random.randint(100, 999)}"
    part2 = f"{random.randint(10, 99)}"
    part3 = f"{random.randint(10, 99)}"
    return f"{prefix} {part1} {part2} {part3}"

def generate_tc_number():
    tc = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(8)]
    tenth = ((sum(tc[0:9:2]) * 7 - sum(tc[1:8:2])) % 10)
    tc.append(tenth)
    eleventh = sum(tc) % 10
    tc.append(eleventh)
    return ''.join(map(str, tc))

def create_bio_sentence(sentence_id, text, entity_value, entity_label):
    tokens = re.findall(r"\w+|[^\w\s]", text)
    entity_tokens = re.findall(r"\w+|[^\w\s]", entity_value)
    bio_lines = []
    found = False
    i = 0
    while i < len(tokens):
        if not found and tokens[i:i+len(entity_tokens)] == entity_tokens:
            bio_lines.append(f"{sentence_id},{tokens[i]},B-{entity_label}")
            for j in range(1, len(entity_tokens)):
                bio_lines.append(f"{sentence_id},{tokens[i+j]},I-{entity_label}")
            i += len(entity_tokens)
            found = True
        else:
            bio_lines.append(f"{sentence_id},{tokens[i]},O")
            i += 1
    return bio_lines

# Şablonlar
tc_templates = [
    "Ahmet'in T.C. kimlik numarası {}'dir.",
    "Kimlik bilgisi {} olarak görünüyor.",
    "Kimlik doğrulama için {} bilgisi kullanıldı.",
    "Sisteme {} T.C. kimlik numarası ile giriş yapıldı.",
    "Başvuru yapanın numarası {} olarak kaydedildi.",
    "T.C. numarası {} olan kişi kayıt oldu.",
    "Yeni gelen vatandaşın TC numarası {}.",
    "Beyan edilen kimlik numarası: {}",
    "Nüfus kayıt sistemindeki numara {} olarak verildi.",
    "Kişinin kimliği {} numarasıyla eşleşti."
]

phone_templates = [
    "İletişim için {} numarasını arayabilirsiniz.",
    "Yeni telefon numarası {} olarak kaydedildi.",
    "Lütfen {} numarasıyla iletişime geçin.",
    "Randevu için {} aranmalıdır.",
    "Bize ulaşmak için {} numarasını kullanabilirsiniz.",
    "Acil durumda {} numarasını arayın.",
    "Kayıtlı iletişim numarası: {}",
    "Cep telefonu {} olan kullanıcı giriş yaptı.",
    "Telefon rehberine {} eklendi.",
    "İrtibat numarası olarak {} verilmiştir."
]

# Veri üretimi
sentences = []
sentence_id = 9287

for _ in range(3355):
    tc = generate_tc_number()
    template = random.choice(tc_templates)
    text = template.format(tc)
    sentences += create_bio_sentence(sentence_id, text, tc, "TCNO")
    sentence_id += 1

for _ in range(3355):
    phone = generate_phone_number()
    template = random.choice(phone_templates)
    text = template.format(phone)
    sentences += create_bio_sentence(sentence_id, text, phone, "PHONE")
    sentence_id += 1

# Kaydet
with open("bio_tc_phone_4081_train.csv", "w", encoding="utf-8") as f:
    for line in sentences:
        f.write(line + "\n")
