import re

SIMILAR_ENTITY_GROUPS = [
    {"TCNO", "PHONE"},
    {"DATE"},
    {"PERSON"},
    {"ORG"},
]

def are_similar_entities(e1, e2):
    if e1 is None or e2 is None:
        return False
    e1 = e1.upper()
    e2 = e2.upper()
    for group in SIMILAR_ENTITY_GROUPS:
        if e1 in group and e2 in group:
            return True
    return False

# Gelişmiş postprocess: Ardışık sayısal tokenları birleştirip, TCNO/PHONE bloklarını tam ve doğru şekilde etiketler.
def postprocess_entities(entities):
    import re
    merged = []
    i = 0
    n = len(entities)
    while i < n:
        ent = entities[i]
        word_raw = ent["word"]
        word = word_raw.replace(" ", "").replace("-", "")
        digits = re.sub(r"\D", "", word)
        is_numeric = bool(re.fullmatch(r"[\d\+\-]+", word))

        # Eğer sayısal blok başlıyorsa, ardışık tüm sayısal tokenları birleştir
        if is_numeric:
            start = ent["start"]
            end = ent["end"]
            score_sum = ent["score"]
            count = 1
            full_word = word
            j = i + 1
            while j < n:
                next_ent = entities[j]
                next_word = next_ent["word"].replace(" ", "").replace("-", "")
                next_digits = re.sub(r"\D", "", next_word)
                next_is_numeric = bool(re.fullmatch(r"[\d\+\-]+", next_word))
                # Arada O veya sayısal entity varsa birleştir
                if next_is_numeric and next_ent["start"] == end:
                    full_word += next_word
                    end = next_ent["end"]
                    score_sum += next_ent["score"]
                    count += 1
                    j += 1
                else:
                    break
            avg_score = score_sum / count
            digits_full = re.sub(r"\D", "", full_word)
            # Etiketle
            if digits_full.startswith("05") or digits_full.startswith("905"):
                entity_group = "PHONE"
            elif len(digits_full) == 11 and digits_full.isdigit():
                entity_group = "TCNO"
            elif (len(digits_full) in [10, 11]) and (full_word.strip().startswith(("0", "+90")) or digits_full.startswith("5")):
                entity_group = "PHONE"
            elif len(digits_full) == 10 and digits_full.startswith("5"):
                entity_group = "PHONE"
            else:
                entity_group = ent["entity_group"]
            if entity_group in ["TCNO", "PHONE"]:
                merged.append({
                    "word": full_word,
                    "entity_group": entity_group,
                    "start": start,
                    "end": end,
                    "score": avg_score
                })
            i = j
        else:
            # Diğer entity'ler için eski kural
            if ent["entity_group"] not in ["O", "TCNO", "PHONE"]:
                merged.append(ent)
            i += 1
    return merged
