from datetime import date

from ship_date import parse_reply

TODAY = date(2026, 11, 23)


def test_delay_with_new_date():
    r = parse_reply("Unfortunately the unit is delayed. Revised ship date is May 20, 2027.", TODAY)
    assert r.new_date == date(2027, 5, 20) and r.delay_mentioned and not r.needs_human


def test_old_and_new_date_with_delay_takes_later():
    r = parse_reply("PO-4411 was 2027-03-15, but due to a core steel shortage it moved to 2027-06-12.", TODAY)
    assert r.new_date == date(2027, 6, 12)


def test_two_dates_without_delay_asks_human():
    r = parse_reply("Partial ship 2027-02-01 and balance 2027-03-01.", TODAY)
    assert r.new_date is None and r.needs_human


def test_no_date():
    r = parse_reply("Thanks, we'll get back to you.", TODAY)
    assert r.new_date is None and r.needs_human


def test_shipped():
    r = parse_reply("Your order shipped today, tracking number 1Z999.", TODAY)
    assert r.shipped and not r.needs_human


def test_past_dates_ignored():
    r = parse_reply("Original date 2025-01-10 still holds? New date 2027-01-10.", TODAY)
    assert r.new_date == date(2027, 1, 10)


def test_long_input_is_truncated():
    r = parse_reply("x" * 50_000 + " ship 2027-01-01", TODAY)
    assert r.new_date is None
