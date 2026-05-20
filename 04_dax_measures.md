# DAX Measures

Eleven measures. All live on `Fact_Events`. Naming: PascalCase, no prefixes, no `[Measure]` suffix noise. Format strings noted where they materially affect readability.

---

## Core volume

**1. Total Events** — base count of fact rows; foundation for almost everything else.
```dax
Total Events = COUNTROWS(Fact_Events)
```

**2. Total Value** — additive sum across discriminated event types. For `Footfall` this is a headcount; for `Loan`/`Return`/`StudyRoomBooking` it's a transaction count (each row = 1); for `EResourceSession`/`HelpDeskTicket` it's a session/ticket count. Combining them in one measure is intentional — slicers on `EventType` make the unit meaningful.
```dax
Total Value = SUM(Fact_Events[Value])
```

---

## Event-type-specific

**3. Total Loans** — filtered count, headline metric for circulation.
```dax
Total Loans =
CALCULATE(
    [Total Events],
    Dim_EventType[EventType] = "Loan"
)
```

**4. Total Footfall** — additive sum scoped to footfall events. Format: `#,##0`.
```dax
Total Footfall =
CALCULATE(
    [Total Value],
    Dim_EventType[EventType] = "Footfall"
)
```

**5. E-Resource Sessions** — scoped sum for digital engagement.
```dax
E-Resource Sessions =
CALCULATE(
    [Total Value],
    Dim_EventType[EventType] = "EResourceSession"
)
```

**6. Help Desk Tickets** — scoped sum for support load.
```dax
Help Desk Tickets =
CALCULATE(
    [Total Value],
    Dim_EventType[EventType] = "HelpDeskTicket"
)
```

---

## Time intelligence

**7. Events MoM %** — month-over-month delta on total events. `DIVIDE` (not `/`) handles the first-month divide-by-zero. Format: `0.0%;-0.0%`.
```dax
Events MoM % =
VAR Current = [Total Events]
VAR Prior =
    CALCULATE(
        [Total Events],
        DATEADD(Dim_Date[Date], -1, MONTH)
    )
RETURN
    DIVIDE(Current - Prior, Prior)
```

**8. Exam Period Events** — isolates exam-window activity. Pairs with `Total Events` as a ratio in the visual layer.
```dax
Exam Period Events =
CALCULATE(
    [Total Events],
    Dim_Date[IsExamPeriod] = TRUE()
)
```

---

## Ratios

**9. Avg Footfall per Day** — daily footfall normalised by active days in the current filter context. `DISTINCTCOUNT` on `Dim_Date[Date]` is the correct denominator (not `Fact_Events[EventDate]`) because it respects date-slicer selections even on days with zero footfall events.
```dax
Avg Footfall per Day =
DIVIDE(
    [Total Footfall],
    DISTINCTCOUNT(Dim_Date[Date])
)
```

**10. Loans per Patron Category %** — share of loans for the current patron filter context; used in stacked / 100% visuals.
```dax
Loans per Patron Category % =
DIVIDE(
    [Total Loans],
    CALCULATE([Total Loans], ALL(Dim_Patron[PatronCategory]))
)
```

---

## Data quality

**11. Unknown Patron Rate** — surfaces the `"Unknown"` mapping rate from Step 3 of the Power Query plan. Goes on the dashboard as a small KPI card; if it drifts upward over time, upstream data entry is degrading. Format: `0.0%`.
```dax
Unknown Patron Rate =
DIVIDE(
    CALCULATE([Total Events], Dim_Patron[PatronCategory] = "Unknown"),
    [Total Events]
)
```

---

## Notes on what's *not* here

- **No YoY measures.** The dataset spans ~8 months; year-over-year would be meaningless and look like padding.
- **No running totals.** Reasonable for some library metrics, but the single-page brief doesn't call for them. Add later if needed.
- **No `SWITCH`-based "selected metric" measure.** Tempting for a dynamic KPI card, but adds complexity without analytic value at this scope.
- **No iterator measures (`SUMX`, `AVERAGEX`).** Nothing in this model requires row-context evaluation — flat aggregations are correct and faster.

Each measure is independently testable against the cleaned fact table. The dependency chain `Total Events → Total Loans → Loans per Patron Category %` is the tree to validate first; everything else is leaf-level.
