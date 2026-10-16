def test_multi_user_isolation_and_claims(fresh_db):
    db = fresh_db
    db.upsert_user(1, 1, "A"); db.upsert_user(2, 2, "B")
    e1 = db.add_expense(1, "taksi", 25000, "transport.fare")
    db.add_expense(2, "non", 4000, None)
    assert [r["item"] for r in db.get_expenses(1)] == ["taksi"]
    assert [r["item"] for r in db.get_expenses(2)] == ["non"]
    assert db.set_category(2, e1, "daily.other") is None                  # cannot edit another user's row
    assert db.set_category(1, e1, "daily.other")["cat"] == "daily.other"
    assert db.claim_reminder(1, "2026-10-16") is True
    assert db.claim_reminder(1, "2026-10-16") is False                     # at most once a day
    assert db.claim_reminder(1, "2026-10-17") is True
    db.save_rule(1, "paypoq", "daily.clothing"); db.save_rule(1, "paypoq", "daily.other")
    assert db.get_rules(1) == {"paypoq": "daily.other"} and db.get_rules(2) == {}
    assert db.delete_last(1)["id"] == e1 and db.delete_last(1) is None
    assert db.get_user(1)["remind_time"] == "18:00"
    big = 9_000_000_000_000                                                # Telegram ids exceed 32 bit
    db.upsert_user(big, big, "Big"); assert db.get_user(big)["user_id"] == big
