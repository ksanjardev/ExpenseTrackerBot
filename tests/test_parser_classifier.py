import pytest

from categories import classify, rule_key
from expense_parser import parse_line, parse_message


@pytest.mark.parametrize("text,item,amount", [
    ("10 ta paypoq oldim 13k", "10 ta paypoq oldim", 13000),          # the example from the spec
    ("taksi 25 000", "taksi", 25000),
    ("3 kg olma 45 ming", "3 kg olma", 45000),
    ("10 пар носков 13k", "10 пар носков", 13000),
    ("telefon 1.5 mln", "telefon", 1_500_000),
    ("non 4000", "non", 4000),
    ("kofe 18 000 so'm", "kofe", 18000),
    ("olma 2 kg 15000", "olma 2 kg", 15000),
    ("coffee 2.5k", "coffee", 2500),
])
def test_parse(text, item, amount):
    assert parse_line(text) == (item, amount)


def test_parse_multi_and_failures():
    ok, bad = parse_message("taksi 25000; non 4000\nsalom")
    assert ok == [("taksi", 25000), ("non", 4000)] and bad == ["salom"]


@pytest.mark.parametrize("text,cat", [
    ("10 ta paypoq oldim", "daily.clothing"), ("taksi", "transport.fare"), ("3 kg olma", "daily.groceries"),
    ("benzin", "transport.fuel"), ("ijara", "home.rent"), ("dori", "health.medicine"),
    ("Netflix", "subs.dues"), ("свет", "home.electricity"), ("такси домой", "transport.fare"),
    ("кофе", "daily.dining"), ("telefon balans", "home.phone"), ("telefon sotib oldim", "fun.gadgets"),
    ("mashina remont", "transport.repairs"), ("uy remont", "home.maintenance"), ("sadaqa", "charity.religious"),
    ("o'g'limga sovg'a", "charity.gifts"), ("kredit to'lov", "oblig.loans"), ("soliq", "oblig.federal"),
])
def test_classify(text, cat):
    assert classify(text) == cat


def test_unknown_and_learned_rule():
    assert classify("qwerty zxcv") is None
    rules = {rule_key("qwerty zxcv"): "fun.hobbies"}
    assert classify("2 ta qwerty zxcv oldim", rules) == "fun.hobbies"      # numbers/verbs ignored
    assert classify("taksi", {"taksi": "daily.other"}) == "daily.other"     # user rule beats built-in
