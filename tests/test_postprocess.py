from postprocess import are_similar_entities, postprocess_entities


def test_similar_entity_groups():
    assert are_similar_entities("TCNO", "PHONE") is True     # same group
    assert are_similar_entities("tcno", "phone") is True     # case-insensitive
    assert are_similar_entities("DATE", "PERSON") is False
    assert are_similar_entities(None, "PHONE") is False


def _ent(word, group, start, end, score=0.9):
    return {"word": word, "entity_group": group, "start": start, "end": end, "score": score}


def test_eleven_digit_number_labelled_tcno():
    out = postprocess_entities([_ent("12345678901", "TCNO", 0, 11)])
    assert len(out) == 1 and out[0]["entity_group"] == "TCNO"


def test_number_starting_05_labelled_phone():
    out = postprocess_entities([_ent("05321234567", "PHONE", 0, 11)])
    assert out[0]["entity_group"] == "PHONE"


def test_consecutive_numeric_tokens_are_merged():
    entities = [_ent("0532", "PHONE", 0, 4), _ent("1234567", "PHONE", 4, 11)]
    out = postprocess_entities(entities)
    assert len(out) == 1
    assert out[0]["word"] == "05321234567"
    assert out[0]["entity_group"] == "PHONE"


def test_non_numeric_person_passes_through():
    out = postprocess_entities([_ent("Ahmet", "PERSON", 0, 5)])
    assert len(out) == 1 and out[0]["entity_group"] == "PERSON"
