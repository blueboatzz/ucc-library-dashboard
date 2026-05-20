# UCC Library Activity Dashboard — Portfolio Prototype

A small, end-to-end Power BI prototype built to mirror the UCC Library Business Dashboard stack: **SharePoint Lists → Power Query → Power BI**. Scoped as a single operations-focused page — proof of end-to-end stack competence, not a magnum opus.

Built for an internship application to UCC Library (Student Intern – End-to-End Data Visualisation).

## What's in this folder

| File | What it is |
|---|---|
| `01_generate_library_dataset.py` | Python script that generates a realistic, deliberately *imperfect* synthetic library dataset |
| `library_activity_raw.csv` | The generated dataset (~1,300 rows), ready to upload to a SharePoint List |
| `02_power_query_plan.md` | Step-by-step Power Query (M) cleaning logic → clean star schema + audit queries |
| `03_data_model.md` | Star-schema model: tables, relationships, cardinality, and the reasoning behind each choice |
| `04_dax_measures.md` | 11 DAX measures, each with expression + description |
| `05_dashboard_layout.md` | Single-page layout spec (operations audience, justified) — canvas regions, visuals, slicers |
| `06_data_dictionary.md` | Every field: type, source, transformation logic, general-audience + SME descriptions |
| `07_technical_architecture.md` | Data flow, refresh strategy, ownership, scalability |

## How the pieces connect

```
01 generate ──▶ library_activity_raw.csv ──▶ [upload to SharePoint List]
                                                    │
                                          02 Power Query cleans it
                                                    │
                                          03 model (star schema)
                                                    │
                                          04 DAX measures
                                                    │
                                          05 dashboard page
                                  (06 dictionary + 07 architecture document it all)
```

## How to demonstrate it

1. Run `python 01_generate_library_dataset.py` to (re)generate the CSV.
2. Upload the CSV to a SharePoint List called `LibraryActivity`.
3. Follow `02_power_query_plan.md` to build the dataflow.
4. Build the model per `03`, add the measures from `04`.
5. Lay out the page per `05`.
6. `06` and `07` are your supporting documentation — exactly the deliverables the role brief names.

## The narrative for an interview

The whole point of this prototype is to show end-to-end thinking against the role's actual language: working with **imperfect data** (deliberate quality issues, audited not hidden), **documented transformation logic**, a **data dictionary** with audience-specific descriptions, **version-controlled assets**, and **audience-specific visual storytelling** (one operations view, chosen deliberately because it's what the data can honestly support).

> Note: the dataset is **synthetic**. It's generated to be realistic and deliberately imperfect so the cleaning and documentation work has something real to act on. This is stated openly — it's a self-directed portfolio exercise, not real UCC Library data.
