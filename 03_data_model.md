# Data Model

## Shape: star schema

One fact table at the centre, four dimensions radiating out. No snowflaking, no bridges, no many-to-many. At this scope, a clean star is the correct and most defensible choice.

```
                 ┌─────────────┐
                 │  Dim_Date   │
                 └──────┬──────┘
                        │ 1
                        │
                        │ *
┌──────────────┐ * ┌────┴─────────┐ * ┌────────────────┐
│  Dim_Branch  ├───┤  Fact_Events ├───┤  Dim_EventType │
└──────────────┘ 1 └────┬─────────┘ 1 └────────────────┘
                        │ *
                        │
                        │ 1
                 ┌──────┴──────┐
                 │  Dim_Patron │
                 └─────────────┘
```

## Relationships

| From (many) | To (one) | Key | Cardinality | Cross-filter |
|---|---|---|---|---|
| `Fact_Events[EventDate]` | `Dim_Date[Date]` | date | Many-to-one | Single |
| `Fact_Events[Branch]` | `Dim_Branch[Branch]` | text | Many-to-one | Single |
| `Fact_Events[EventType]` | `Dim_EventType[EventType]` | text | Many-to-one | Single |
| `Fact_Events[PatronCategory]` | `Dim_Patron[PatronCategory]` | text | Many-to-one | Single |

All relationships are **active**, **single-direction** (dimension filters fact). No bidirectional filtering — it isn't needed and bidirectional cross-filter is the most common source of subtle measure bugs in beginner models. Leaving it off is a deliberate signal of discipline.

## Modelling choices — and the reasoning

**Why a star, not a flat table.** A single wide table would "work" for 1,500 rows, but the brief is about demonstrating production practice. A star schema is what scales, what makes `Dim_Date` time-intelligence possible, and what a reviewer expects to see.

**Why `Dim_Date` is generated, not derived.** A proper date dimension covering every calendar day (not just days with events) is what makes measures like *Avg Footfall per Day* correct — the denominator must count calendar days, including zero-activity days, or averages inflate.

**No `Dim_ItemType`.** `item_type` is left as a fact-table attribute rather than promoted to a dimension. It's low-cardinality and only used for occasional filtering; a dimension would be overhead. Documenting this as a *choice* (new item types require deliberate model extension) is the point worth making in the portfolio narrative.

**No measure table yet.** For 8–12 measures, a dedicated hidden `_Measures` table is overkill. They live on `Fact_Events`. The trigger to add `_Measures` is roughly 20+ measures.

**What's deliberately *not* in the model:**
- No bridge tables (no many-to-many relationships exist)
- No calculated columns (anything derivable goes in measures or Power Query)
- No `USERELATIONSHIP` / inactive relationships (none needed)

Each absence is a choice, not an oversight — and that framing is what separates a portfolio piece from a tutorial.
