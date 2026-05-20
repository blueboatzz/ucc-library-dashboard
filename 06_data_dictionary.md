# Data Dictionary — `Fact_Events` and dimensions

Two description columns per field: a **general-audience** plain-English line, and an **SME-level** line with the technical/lineage detail. This dual-audience format is exactly what the role brief calls for.

## Fact_Events

| Field | Type | Source | Transformation logic | General-audience description | SME description |
|---|---|---|---|---|---|
| `event_id` | Text | SharePoint List | Trimmed; exact-duplicate rows removed (Step 6) | A unique code for each library activity record | Business key. Grain = one event. Not a relationship key (dims join on natural keys). Dedupe is whole-row, not on this column alone. |
| `EventDate` | Date | Derived from `event_date` | Multi-format parse (Step 2); unparseable → reject | The calendar date the activity happened | Parsed via ordered `try…otherwise` over 4 formats, `en-IE`. Nulls split to `Fact_Events_Rejects`. Joins `Dim_Date[Date]`. |
| `Branch` | Text | SharePoint List | Trimmed; blanks → `"Unspecified"` (Step 4) | Which library building the activity happened in | Joins `Dim_Branch`. Blank-handling keeps referential integrity intact. |
| `EventType` | Text | SharePoint List | Trimmed, cleaned (Step 4) | The kind of activity (loan, return, footfall, etc.) | Discriminator for type-scoped measures. Joins `Dim_EventType`. Drives the meaning of `Value`. |
| `item_type` | Text | SharePoint List | Trimmed; left on fact (no dimension) | What kind of item (book, laptop, study room…) | Deliberately not promoted to a dimension — low cardinality, filter-only use. New types need manual model extension. |
| `PatronCategory` | Text | Derived from `patron_category` | Conformed to 4 values; else `"Unknown"` (Step 3) | The type of library user (undergrad, postgrad, staff, external) | Spelling variants mapped via lowercase lookup lists. `"Unknown"` is surfaced (measure 11), not hidden. Joins `Dim_Patron`. |
| `Value` | Int64 | SharePoint List | Type-cast; footfall range-checked (Step 7) | A count for the activity — usually 1, but a headcount for footfall | Unit depends on `EventType`. Footfall `<0` or `>2000` → `Fact_Events_Outliers`. Sum is additive within an EventType filter. |

## Dim_Date

| Field | Type | Source | Transformation logic | General-audience description | SME description |
|---|---|---|---|---|---|
| `Date` | Date | Generated | Continuous calendar min→max of `EventDate` | Every calendar day in the period | Relationship key. Continuous (incl. zero-activity days) so daily averages are correct. |
| `YearMonth` | Text | Generated | `Date.ToText(... "yyyy-MM")` | The month an activity falls in | Sort/group key for monthly trend visuals. |
| `MonthName` | Text | Generated | Month long name | Name of the month | Display label; sorted by month number. |
| `IsExamPeriod` | Bool | Generated | Flag for Dec & April exam windows | Whether the date is in an exam period | Drives `Exam Period Events` and time-axis shading. |
| `IsWeekend` | Bool | Generated | `Date.DayOfWeek` ≥ 5 | Whether the date is a weekend | Optional filter for staffing analysis. |

## Dim_Patron / Dim_EventType / Dim_Branch

| Field | Type | Source | Transformation logic | General-audience description | SME description |
|---|---|---|---|---|---|
| `PatronCategory` | Text | Distinct from fact | `Table.Distinct` post-conformance | List of user types | 5 values incl. `"Unknown"`. Single-direction filter to fact. |
| `EventType` | Text | Distinct from fact | `Table.Distinct` | List of activity types | 6 values. Single-direction filter to fact. |
| `Branch` | Text | Distinct from fact | `Table.Distinct` incl. `"Unspecified"` | List of library branches | Single-direction filter to fact. |

## Audit queries (loaded, not in relationships)

| Query | Type | Purpose | Surfaced where |
|---|---|---|---|
| `Fact_Events_Rejects` | Audit | Rows where `event_date` could not be parsed by any of the 4 format attempts | Data-quality footer — row count only |
| `Fact_Events_Outliers` | Audit | Footfall rows filtered for value `<0` or `>2000` | Data-quality footer — row count only |
