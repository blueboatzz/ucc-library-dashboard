"""
UCC Library Activity — Synthetic Dataset Generator
===================================================

Produces a deliberately IMPERFECT operational dataset for a Power BI
portfolio prototype. The imperfections are intentional: they exist so the
Power Query layer has something real to clean (mixed date formats,
inconsistent category spellings, missing values, duplicates, outliers).

Output: library_activity_raw.csv  (ready to upload to a SharePoint List)

Schema (one row = one operational event):
    event_id          unique id (key)
    event_date        DELIBERATELY mixed formats
    branch            library branch
    event_type        Loan | Return | StudyRoomBooking | Footfall
                      | EResourceSession | HelpDeskTicket
    item_type         Book | Journal | Laptop | StudyRoom | EResource | NA
    patron_category   undergrad / postgrad / staff / external (MESSY spellings)
    value             count/headcount for the event (footfall can be large)

Run:  python 01_generate_library_dataset.py
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible


START = date(2025, 9, 1)     # academic year start
DAYS = 243                   # ~8 months -> ends ~late April
TARGET_ROWS = 1500

BRANCHES = ["Boole Library", "Brookfield Health Sciences", "Boole Basement", "Q+1 Reading Room"]

PATRON_VARIANTS = {
    "undergrad":  ["Undergrad", "undergraduate", "UG", "Undergraduate", "undergrad"],
    "postgrad":   ["Postgrad", "postgraduate", "PG", "Postgraduate"],
    "staff":      ["Staff", "staff", "STAFF"],
    "external":   ["External", "external", "Ext", "Visitor"],
}

EVENT_TYPES = ["Loan", "Return", "StudyRoomBooking", "Footfall",
               "EResourceSession", "HelpDeskTicket"]

ITEM_BY_EVENT = {
    "Loan": ["Book", "Journal", "Laptop"],
    "Return": ["Book", "Journal", "Laptop"],
    "StudyRoomBooking": ["StudyRoom"],
    "Footfall": ["NA"],
    "EResourceSession": ["EResource"],
    "HelpDeskTicket": ["NA"],
}



def seasonal_weight(d: date) -> float:
    """Activity multiplier by date. Exam periods spike; breaks dip."""
    # Christmas break (mid-Dec to early Jan): quiet
    if (d.month == 12 and d.day >= 18) or (d.month == 1 and d.day <= 6):
        return 0.35
    # Autumn exams / Winter exam prep (early-mid Dec): spike
    if d.month == 12 and d.day < 18:
        return 1.8
    # Spring exam prep (April): spike
    if d.month == 4 and d.day >= 10:
        return 1.9
    # Reading weeks / lull (late Oct, late Feb): slight dip
    if (d.month == 10 and 20 <= d.day <= 27) or (d.month == 2 and d.day >= 22):
        return 0.7
    # Weekends: lighter
    if d.weekday() >= 5:
        return 0.55
    # Normal term time
    return 1.0


def is_exam_period(d: date) -> bool:
    return (d.month == 12 and d.day < 18) or (d.month == 4 and d.day >= 10)


def messy_date(d: date) -> str:
    fmt = random.choices(
        ["iso", "dmy_slash", "dmy_dash", "long"],
        weights=[0.55, 0.25, 0.12, 0.08],
    )[0]
    if fmt == "iso":
        return d.isoformat()                       # 2025-09-01
    if fmt == "dmy_slash":
        return d.strftime("%d/%m/%Y")              # 01/09/2025
    if fmt == "dmy_dash":
        return d.strftime("%d-%m-%Y")              # 01-09-2025
    return d.strftime("%d %b %Y")                  # 01 Sep 2025

def event_value(event_type: str) -> int:
    if event_type == "Footfall":
        return max(1, int(random.gauss(420, 160)))   # headcount
    return 1                                           # transaction count


def make_rows():
    rows = []
    eid = 1000
    for offset in range(DAYS):
        d = START + timedelta(days=offset)
        w = seasonal_weight(d)
        # base events per day scaled by seasonality
        n_events = max(1, int(random.gauss(6, 2) * w))
        for _ in range(n_events):
            et = random.choices(
                EVENT_TYPES,
                weights=[0.28, 0.18, 0.14, 0.12, 0.18, 0.10],
            )[0]
            cat_key = random.choices(
                list(PATRON_VARIANTS.keys()),
                weights=[0.62, 0.24, 0.09, 0.05],
            )[0]
            patron = random.choice(PATRON_VARIANTS[cat_key])
            # Footfall is not patron-specific -> sometimes blank
            if et == "Footfall" and random.random() < 0.5:
                patron = ""
            row = {
                "event_id": f"E{eid}",
                "event_date": messy_date(d),
                "branch": random.choice(BRANCHES),
                "event_type": et,
                "item_type": random.choice(ITEM_BY_EVENT[et]),
                "patron_category": patron,
                "value": event_value(et),
            }
            rows.append(row)
            eid += 1
            if len(rows) >= TARGET_ROWS:
                return rows
    return rows


def inject_imperfections(rows):
    """Add the deliberate data quality issues."""
    n = len(rows)

    # 1. ~3% missing values in NON-KEY fields (branch / patron_category)
    for _ in range(int(n * 0.03)):
        r = random.choice(rows)
        field = random.choice(["branch", "patron_category"])
        r[field] = ""

    # 2. A few unparseable dates (typos) -> exercise the reject path
    for _ in range(4):
        r = random.choice(rows)
        r["event_date"] = random.choice(["2025-13-02", "31/02/2025", "n/a", ""])

    # 3. Footfall outliers (impossible values) -> exercise outlier filter
    foot = [r for r in rows if r["event_type"] == "Footfall"]
    for r in random.sample(foot, min(3, len(foot))):
        r["value"] = random.choice([-5, 9999, 5200])

    # 4. Duplicates (same event_id appears twice)
    for _ in range(6):
        r = random.choice(rows)
        rows.append(dict(r))

    return rows


def main():
    rows = make_rows()
    rows = inject_imperfections(rows)
    random.shuffle(rows)

    out = "library_activity_raw.csv"
    fields = ["event_id", "event_date", "branch", "event_type",
              "item_type", "patron_category", "value"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")
    print("Deliberate issues injected: mixed date formats, ~3% missing "
          "branch/patron, 4 unparseable dates, 3 footfall outliers, 6 duplicates.")


if __name__ == "__main__":
    main()
