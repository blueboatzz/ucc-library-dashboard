# Dashboard Page Layout

## Audience: Operations

One audience, chosen and justified — not hedged.

**Why operations over leadership.** Leadership dashboards trade in strategic KPIs measured monthly or quarterly: cost per visit, collection ROI, strategic-plan progress. Eight months of synthetic transactional data can't credibly support that view — there's no budget context, no benchmarking, no multi-year trend. An operations view is what this dataset genuinely supports: daily/weekly activity patterns, branch comparisons, exam-period planning, staffing implications. Picking the view the data can actually defend is itself the analytical judgment worth showing.

---

## Canvas layout (single 16:9 page)

```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER BAND                                                           │
│  "UCC Library — Operations Activity"      [Date slicer] [Branch slicer]│
├───────────────┬───────────────┬───────────────┬──────────────────────┤
│ KPI: Total    │ KPI: Total    │ KPI: Avg       │ KPI: Unknown Patron   │
│ Loans         │ Footfall      │ Footfall/Day   │ Rate (data quality)   │
├───────────────┴───────────────┴───────────────┴──────────────────────┤
│  LEFT (≈60%)                          │  RIGHT (≈40%)                  │
│  Line chart:                          │  Stacked bar:                  │
│  Total Events by week,                │  Loans by Patron Category      │
│  with exam periods highlighted        │  (uses Loans per Category %)   │
│                                       │                                │
│                                       ├────────────────────────────────┤
│                                       │  Bar: Events by Branch         │
├───────────────────────────────────────┴────────────────────────────────┤
│  FOOTER STRIP                                                          │
│  Event-type breakdown (small multiples / donut) + data-quality note:  │
│  "X rejected rows, Y outliers excluded" (from audit queries)          │
└──────────────────────────────────────────────────────────────────────┘
```

## Region-by-region

| Region | Visual | Measure(s) | Why |
|---|---|---|---|
| KPI row | 4 card visuals | Total Loans, Total Footfall, Avg Footfall per Day, Unknown Patron Rate | Headline operational pulse + one data-quality signal |
| Left main | Line chart, X = week | Total Events (+ Exam Period Events as highlight) | Shows the term-time/exam rhythm staff plan around |
| Right top | 100% stacked bar | Loans per Patron Category % | Who is actually borrowing — staffing & collection signal |
| Right bottom | Horizontal bar | Total Events by Branch | Branch load comparison |
| Footer | Donut / small multiples | Total Events by EventType | Mix of activity at a glance |
| Footer note | Card / text | audit row counts | Transparency: nothing silently dropped |

## Slicers / filters

- **Date** slicer (between-style), wired to `Dim_Date[Date]`.
- **Branch** slicer (dropdown), wired to `Dim_Branch[Branch]`.
- **EventType** as an optional filter on the page (not a slicer) so the KPI cards stay stable while charts can be drilled.

## Design standards

- Single accent colour for "current" series, neutral grey for context — no rainbow.
- Exam periods shaded on the time axis so the busiest windows read instantly.
- KPI cards: value large, label small, no decorative icons.
- Consistent number formatting (`#,##0` for counts, `0.0%` for rates).
- Title states the audience explicitly: *"Operations Activity"* — never make a reviewer guess who a dashboard is for.
