from faker import Faker
import random
from datetime import date

faker = Faker('tr_TR')

phone_formats = [
    '05#########',          # 05321234567
    '0 5## ### ## ##',      # 0 532 123 45 67
    '0(5##) ### ## ##',     # 0(532) 123 45 67
    '0(5##)-###-##-##',     # 0(532)-123-45-67
    '0212 #######',         # 0212 1234567
    '0 212 ### ## ##',      # 0 212 123 45 67
    '0(212) ### ## ##',     # 0(212) 123 45 67
    '0(212)-###-##-##',     # 0(212)-123-45-67
    '0216 #######',         # 0216 1234567
    '0 216 ### ## ##',      # 0 216 123 45 67
    '0(216) ### ## ##',     # 0(216) 123 45 67
    '0(216)-###-##-##',     # 0(216)-123-45-67
    '+90 5#########',       # +90 5321234567
    '+90 5## ### ## ##',    # +90 532 123 45 67
    '+90 (5##) ### ## ##',  # +90 (532) 123 45 67
    '+90 (5##)-###-##-##',  # +90 (532)-123-45-67
    '+90 212 #######',      # +90 2121234567
    '+90 216 #######',      # +90 2161234567
    '+905#########',        # +905321234567
    '+9(506)-###-##-##',    # +9(506)-123-45-67 (örnek)
    '0### ### ####',        # 0312 123 4567
    '0###-###-####',        # 0312-123-4567
    '+90 ### ### ####',     # +90 312 123 4567
    '+90 ###-###-####',     # +90 312-123-4567
]

def generate_phone_number():
    fmt = random.choice(phone_formats)
    number = ''
    for ch in fmt:
        if ch == '#':
            number += str(random.randint(0,9))
        else:
            number += ch
    return number

def generate_valid_tc_no():
    # TC Kimlik No kuralları:
    # 1. 11 haneli sayı
    # 2. İlk hane 0 olamaz
    # 3. 10. hane: ((1+3+5+7+9).sum * 7 - (2+4+6+8).sum) mod 10
    # 4. 11. hane: ilk 10 hanenin mod 10’u
    
    digits = [random.randint(1,9)]  # ilk hane 0 değil
    digits += [random.randint(0,9) for _ in range(8)]  # 2.-9. hane
    odd_sum = sum(digits[0:9:2])  # 1.,3.,5.,7.,9.
    even_sum = sum(digits[1:8:2]) # 2.,4.,6.,8.
    
    digit_10 = ((odd_sum * 7) - even_sum) % 10
    digits.append(digit_10)
    
    digit_11 = sum(digits[:10]) % 10
    digits.append(digit_11)
    
    return ''.join(str(d) for d in digits)

def generate_sample_data():
    name = faker.name()
    tcno = generate_valid_tc_no()
    phone = generate_phone_number()
    organization = faker.company()
    random_date = faker.date_between(start_date='-5y', end_date='today')  # son 5 yıl içinden tarih
    return name, tcno, phone, organization, random_date

def generate_sentence():
    name, tcno, phone, organization, random_date = generate_sample_data()
    date_str = random_date.strftime('%d.%m.%Y')  # Sayısal tarih formatı: 04.07.2025
    return (f"{name}, {organization} şirketinde çalışıyor. "
            f"TC kimlik numarası {tcno} ve telefon numarası {phone}. "
            f"Son giriş tarihi {date_str}.")

if __name__ == "__main__":
    for _ in range(3):
        print(generate_sentence())
