# NASA data provenance

**Status at 2026-11-14: a real NASA OSDR catalog metadata snapshot is displayed; no NASA experimental data values are processed by the application.**

## OSDR OSD-53

- Study: [Spaceflight modulates gene expression in the whole blood of astronauts](https://osdr.nasa.gov/bio/repo/data/studies/OSD-53)
- Accession: OSD-53 / GLDS-53
- Catalog API used: `https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-53/assay/*/sample/*/metadata/`
- Access date: 2026-11-14
- Publication DOI: [10.1038/npjmgrav.2016.39](https://doi.org/10.1038/npjmgrav.2016.39)
- Catalog fields represented in the UI: sample record count, astronaut sample phase labels (L-10 and R+0), study assay description, and the presence of a catalog control record. The API snapshot exposed 13 records: six astronauts' preflight records, six postflight records, and one record representing a healthy non-astronaut control group.
- Transformation: count records grouped by the catalog's study factor/time-point metadata. The app stores only this small derived count snapshot in `frontend/src/lib/nasa-catalog.ts`. It does not contain gene expression values or any participant-level molecular values.
- Feature: NASA Research screen displays the metadata counts in a separate research-context card, visually and textually distinguished from mission telemetry.
- Limitations: this is human whole-blood gene-expression research, not heart rate, SpO2, respiration, or a validated clinical monitoring protocol. A metadata record count is not a research result and does not establish a biological effect. The control record represents a group, not an individual count.
- Reuse: the queried catalog metadata did not expose a clear study-specific license field. We attribute NASA OSDR and link to the study; we do not redistribute raw measurement data. Check current OSDR/NASA reuse terms before expanding use.

The OSDR processed-file REST URL was queried during this integration attempt but returned non-ZIP content, failing ZIP validation. For that reason no processed dataset values were imported or analyzed. This integration is a verified catalog metadata snapshot, not a processed NASA dataset.

## NASA references

Other NASA Human Research Program pages in the dashboard provide background only. They do not validate synthetic telemetry, statistical settings, or the fatigue check-in. Research sources are not labeled as datasets. NASA-STD-3001 limits are not implemented.

## Product data separation

- Demo mode: invented deterministic fixtures.
- Live mode: synthetic simulator/backend records and user-entered demo check-ins.
- NASA research card: derived OSDR catalog counts only.
- No NASA dataset contributes to vital signs, alerts, radiation values, or statistical baselines.
