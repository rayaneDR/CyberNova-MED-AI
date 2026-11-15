/** Snapshot of NASA OSDR catalog metadata fetched 2026-11-14. This is not a telemetry dataset. */
export const nasaCatalogSnapshot = {
  accession: "OSD-53",
  title: "Spaceflight modulates gene expression in the whole blood of astronauts",
  assay: "Whole-blood DNA microarray / transcription profiling",
  astronautCount: 6,
  astronautPreflightSamples: 6,
  astronautPostflightSamples: 6,
  nonAstronautControlRecords: 1,
  catalogSampleRecords: 13,
  preflightLabel: "L-10 (10 days before launch)",
  postflightLabel: "R+0 (landing day)",
  accessedAt: "2026-11-14",
  url: "https://osdr.nasa.gov/bio/repo/data/studies/OSD-53",
  apiUrl: "https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-53/assay/*/sample/*/metadata/",
  doi: "10.1038/npjmgrav.2016.39",
} as const;
