from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """  Lütfen tamamen yapay ve doğal Türkçe NER verisi üret. Veride aşağıdaki varlık türleri olacak: PHONE, TCNO, PERSON, ORG, DATE.

**Öncelik:** Telefon numaraları doğal, çeşitli Türk cep telefonu biçimlerinde, zengin biçimlerde ve doğru BIO formatıyla üretilecek. Telefon numaraları kesinlikle doğru şekilde işaretlenecek.

Kurallar:

- Telefon numaraları farklı formatlarda olacak, örnekler:  
  “0542 848 51 51”,  
  “+90 (506) 111-9800”,  
  “0535-248-8363”,  
  “05075545950”,  
  “(0216)-122-21-92”,  
  “+90 212 234 56 78”,  
  “0 (530) 123 45 67”  
  vb. çeşitli parantez, kısa çizgi, boşluk ve + işaretleri içerecek.

- Telefon numarasındaki sayı olan tokenların ilk tokenu B-PHONE, sonraki sayı tokenları I-PHONE etiketi alacak.

- Telefon numarasındaki sayı olmayan tüm semboller (parantez, +, -, boşluk vb.) **O** etiketi alacak.

- TC Kimlik Numarası (TCNO) 11 haneli ve tek token olacak, B-TCNO ile işaretlenecek. (İlk hane 0 olamaz, 10. ve 11. hanedeki kurallar geçerli)

- Eğer TCNO, PERSON, ORG, DATE varlıkları da varsa, doğru BIO formatında işaretlenecek.

- Tokenlar kelime ve noktalama işaretleri ayrı ayrı olacak.

- Diğer kelimeler O etiketi alacak.

- Cümleler doğal, günlük Türkçe olacak.

Çıktı CSV formatında olacak, sütunlar: sentence_id,token,label

sentence_id artan tamsayı şeklinde olacak.

Lütfen 250 cümle üret:

- En az 250 cümlede B-PHONE olacak ve çeşitli formatlarda telefon numaraları üretilecek.

- En az 100 cümlede B-TCNO olacak.

- En az 50 cümlede hem B-PHONE hem B-TCNO birlikte olacak.

- PERSON, ORG, DATE varlıkları toplamda 10-20 cümlede yer alacak.

Örnek çıktı formatı:

sentence_id,token,label  
1,Ayşe,B-PERSON  
1,Yılmaz,I-PERSON  
1,doğdu,O  
1,12,B-DATE  
1,Ekim,I-DATE  
1,1990,I-DATE  
1,TC,O  
1,kimlik,O  
1,numarası,O  
1,12345678901,B-TCNO  
1,telefon,O  
1,+,O  
1,90,O  
1,(,O  
1,506,O  
1,),O  
1,111,B-PHONE  
1,-,O  
1,9800,I-PHONE  


"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=4096
)

data_text = response.choices[0].message.content

# CSV dosyasına yaz
with open("openai_dev_data.csv", "w", encoding="utf-8") as f:
    f.write(data_text)

print("Veri openai_dev_data.csv dosyasına yazıldı.")