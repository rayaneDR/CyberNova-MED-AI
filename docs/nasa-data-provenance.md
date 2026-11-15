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

The initial processed-file REST response failed ZIP validation. On November 15 the official file manifest at `https://osdr.nasa.gov/osdr/data/osd/files/53` identified the unrestricted 10,552-byte `GLDS-53_microarray_E-GEOD-47126.processed.zip`. Its direct download at `https://osdr.nasa.gov/geode-py/ws/studies/OSD-53/download?source=datamanager&file=GLDS-53_microarray_E-GEOD-47126.processed.zip` succeeded and had a valid ZIP signature and thirteen sample-table entries. Format inspection found `Reporter Identifier` and `VALUE` columns, including blank values. Reporter semantics, normalization and units were not fully established; these values were not integrated, scientifically analyzed or visualized. The application continues to use catalog metadata only.

## Official NASA resource requirement

The November 13, 2026 Project Submission Guide, read directly on November 15, requires at least one NASA data source **or resource**. The app genuinely uses and cites HRP risks, sleep/scheduling and space-radiation resources as design context, as well as retrieved OSDR metadata. This satisfies that stated use criterion; it is not a guarantee of overall eligibility. No NASA experimental measurement analysis is claimed. Synthetic telemetry remains separate. See `OFFICIAL_SUBMISSION.md` for exact references and disclosures.

## NASA references

Other NASA Human Research Program pages in the dashboard provide background only. They do not validate synthetic telemetry, statistical settings, or the fatigue check-in. Research sources are not labeled as datasets. NASA-STD-3001 limits are not implemented.

## Product data separation

- Demo mode: invented deterministic fixtures.
- Live mode: synthetic simulator/backend records and user-entered demo check-ins.
- NASA research card: derived OSDR catalog counts only.
- No NASA dataset contributes to vital signs, alerts, radiation values, or statistical baselines.
