# Technical Architecture

## Data flow

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐
│ SharePoint List │───▶│  Power BI         │───▶│  Power BI         │───▶│ Power BI       │
│ LibraryActivity │    │  Dataflow (Gen2)  │    │  Semantic Model   │    │ Report (.pbix) │
│ (source of      │    │  — cleaning,      │    │  — star schema,   │    │ — 1-page ops   │
│ record)         │    │  conformance,     │    │  measures,        │    │ dashboard      │
│                 │    │  audit splits     │    │  relationships    │    │                │
└─────────────────┘    └──────────────────┘    └──────────────────┘    └────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Audit outputs   │
                       │ Rejects         │
                       │ Outliers        │
                       └─────────────────┘
```

Three deliberate boundaries. The SharePoint List is the **source of record** — operations staff edit it directly. The **dataflow** owns all transformation logic, runs server-side, and emits both the clean star schema and the audit splits. The **semantic model** owns relationships, measures, and security; it consumes dataflow outputs unchanged. The **report file** is a thin presentation layer over the semantic model.

The split matters because it makes transformation logic reusable. If a second report (paginated, leadership summary, mobile view) is built later, it inherits the same cleaning rules from the dataflow rather than reimplementing them.

## Refresh strategy

Scheduled refresh at **06:00 daily**. One window is sufficient for the operational use case — staffing decisions are made the morning of, not in real time, and the source list updates on a daily cadence. Refresh order is enforced by the dependency chain: dataflow refreshes first, semantic model refreshes from dataflow output, report renders from cached model data.

**Incremental refresh** is not configured at this scale (≈1,500 rows). The trigger to add it is roughly **100,000 fact rows** or refresh duration exceeding **two minutes**, whichever comes first. The partition key would be `EventDate` with a 12-month rolling window.

**Failure handling:** dataflow refresh failures are surfaced via the Power BI service's native email notifications to the dataset owner.

## Ownership

| Layer | Owner | Responsibility |
|---|---|---|
| SharePoint List | Library operations staff | Day-to-day data entry; source of record |
| Dataflow (Gen2) | Dashboard developer | Cleaning, conformance, audit logic |
| Semantic model | Dashboard developer | Relationships, measures, security |
| Report (.pbix) | Dashboard developer | Layout, visuals, publishing |

Separating the SharePoint List owner (operations) from the model owner (developer) is intentional: it means the people who know the data best maintain it, while the analytical logic stays version-controlled and consistent.

## Scalability considerations

- **Volume:** the star schema and dataflow pattern scale to millions of rows; the trigger points above tell you when to switch on incremental refresh.
- **New event types:** require a deliberate model extension (by design — see the `item_type` decision in the data model). This prevents silent scope creep.
- **New reports:** built on the existing semantic model or dataflow, never by re-cleaning the source — single source of transformation truth.
- **Version control:** `.pbix` and the dataset-generator script live in a Git repository; the dataflow definition is exportable as JSON for change tracking.
