# ship-date

Pull a new ship date and delay signals out of a vendor's email reply.

Built by [Eidran](https://eidran.com), which tracks long-lead equipment (transformers, switchgear, generators) on data center projects. This is the rule-based reply reader from our expeditor, released on its own.

```python
from datetime import date
from ship_date import parse_reply

r = parse_reply(
    "Due to a core steel shortage, PO-4411 has been pushed. New ship date is 2027-06-12.",
    today=date(2026, 11, 23),
)
r.new_date          # date(2027, 6, 12)
r.delay_mentioned   # True
r.needs_human       # False
r.explanation       # 'Ship date stated: 2027-06-12'
```

## What it does

- Finds dates written as `2027-06-12`, `6/12/2027` or `Jun 12, 2027`.
- Ignores dates in the past and dates more than five years out.
- Detects delay language ("delayed", "pushed out", "backordered", "revised") and shipment language ("shipped", "in transit", "tracking number").
- When a reply has an old and a new date and mentions a delay, it takes the later date.
- When it can't tell, it sets `needs_human=True` instead of guessing.

## Install

```
pip install git+https://github.com/eidranai/ship-date
```

Requires Python 3.9+ and `python-dateutil`.

## Tests

```
pip install pytest && pytest
```

## License

MIT. Want this running on your whole long-lead log? Try the demo at [eidran.com/#try](https://eidran.com/#try).
