# Power Query (M) Transformation Plan

**Source:** SharePoint List `LibraryActivity` (uploaded from `library_activity_raw.csv`)
**End state:** a clean star schema — one fact table (`Fact_Events`) plus dimension tables (`Dim_Date`, `Dim_Patron`, `Dim_EventType`, `Dim_Branch`) — and two audit queries that capture rejected rows.

The cleaning runs in a **Power BI Dataflow (Gen2)** so the logic is reusable by any report built later, not trapped in a single `.pbix`.

---

#Step-by-step cleaning logic

#Step 1 — Connect and promote headers
Connect to the SharePoint List. Remove SharePoint system columns (`ContentType`, `Modified`, `Author`, etc.), keep only the seven business fields. Promote the first row to headers if needed.

#Step 2 — Parse the mixed-format dates (the hard one)
`event_date` arrives in four formats (`2025-09-01`, `01/09/2025`, `01-09-2025`, `01 Sep 2025`) plus a handful of unparseable junk values. We try each format in turn and fall back to `null`:

```m
// Custom column: try each known format, null if all fail
AddParsedDate = Table.AddColumn(Source, "EventDate", each
    let raw = Text.Trim(Text.From([event_date]))
    in
        try Date.FromText(raw, [Format="yyyy-MM-dd", Culture="en-IE"])
        otherwise try Date.FromText(raw, [Format="dd/MM/yyyy", Culture="en-IE"])
        otherwise try Date.FromText(raw, [Format="dd-MM-yyyy", Culture="en-IE"])
        otherwise try Date.FromText(raw, [Format="dd MMM yyyy", Culture="en-IE"])
        otherwise null,
    type nullable date)
```

Rows where `EventDate = null` are split off into `Fact_Events_Rejects` (Step 8), **not** silently dropped.

#Step 3 — Conform patron categories
Map the inconsistent spellings (`UG`, `undergraduate`, `Undergrad`...) to four canonical values. Anything unrecognised or blank becomes `"Unknown"` (surfaced later as a data-quality KPI, not hidden):

```m
ConformPatron = Table.AddColumn(PrevStep, "PatronCategory", each
    let p = Text.Lower(Text.Trim(Text.From([patron_category])))
    in
        if List.Contains({"undergrad","undergraduate","ug"}, p) then "Undergrad"
        else if List.Contains({"postgrad","postgraduate","pg"}, p) then "Postgrad"
        else if p = "staff" then "Staff"
        else if List.Contains({"external","ext","visitor"}, p) then "External"
        else "Unknown",
    type text)
```

#Step 4 — Trim and clean text fields
`Text.Trim` and `Text.Clean` on `branch`, `event_type`, `item_type`. Replace empty `branch` with `"Unspecified"`.

#Step 5 — Type-cast everything
`EventDate` → date, `value` → Int64, all category fields → text. Explicit typing prevents downstream model surprises.

#Step 6 — Remove duplicates
Duplicates were injected on `event_id`. Remove rows that are exact duplicates across **all** columns (`Table.Distinct`). We dedupe on the whole row rather than `event_id` alone, so a genuine re-keyed correction isn't lost.

#Step 7 — Filter footfall outliers
Footfall `value` must be in a plausible range. Rows with footfall `< 0` or `> 2000` are split into `Fact_Events_Outliers` (audited, not deleted). All other event types keep `value = 1` by construction.

#Step 8 — Split outputs (clean + audit)
- `Fact_Events` — all rows that passed Steps 2 and 7.
- `Fact_Events_Rejects` — rows where `EventDate` could not be parsed.
- `Fact_Events_Outliers` — footfall rows filtered in Step 7.

#Step 9 — Build the dimensions
- `Dim_Date` — generated calendar from min to max `EventDate`, with `IsExamPeriod`, `IsWeekend`, `MonthName`, `YearMonth` flags.
- `Dim_Patron` — distinct `PatronCategory`.
- `Dim_EventType` — distinct `EventType`.
- `Dim_Branch` — distinct `Branch`.

---

#End-state tables

| Query | Role | In relationships? |
|---|---|---|
| `Fact_Events` | Fact (grain = one event) | Yes |
| `Dim_Date` | Dimension | Yes |
| `Dim_Patron` | Dimension | Yes |
| `Dim_EventType` | Dimension | Yes |
| `Dim_Branch` | Dimension | Yes |
| `Fact_Events_Rejects` | Audit (unparseable dates) | No — row count only |
| `Fact_Events_Outliers` | Audit (footfall out of range) | No — row count only |

The two audit queries are loaded but kept **out of the relationship graph** — they surface on the dashboard as data-quality row counts, so problems are visible rather than buried.
