import re

import generate_fake_tc_num as g


def _is_valid_tc(tc: str) -> bool:
    """Official Turkish national-ID checksum rule."""
    if not (tc.isdigit() and len(tc) == 11 and tc[0] != "0"):
        return False
    d = [int(c) for c in tc]
    tenth = ((sum(d[0:9:2]) * 7) - sum(d[1:8:2])) % 10
    eleventh = sum(d[0:10]) % 10
    return d[9] == tenth and d[10] == eleventh


def test_generated_tc_numbers_pass_checksum():
    for _ in range(200):
        assert _is_valid_tc(g.generate_tc_number())


def test_phone_number_format():
    for _ in range(50):
        phone = g.generate_phone_number()
        assert re.fullmatch(r"05\d{2} \d{3} \d{2} \d{2}", phone)


def test_bio_tagging_marks_entity_tokens():
    lines = g.create_bio_sentence(1, "Numaram 12345 olarak kayitli", "12345", "TCNO")
    tagged = [ln.split(",")[-1] for ln in lines]
    assert "B-TCNO" in tagged
    # non-entity tokens are tagged O
    assert tagged.count("O") == len(tagged) - 1
    # every line carries the sentence id
    assert all(ln.startswith("1,") for ln in lines)
