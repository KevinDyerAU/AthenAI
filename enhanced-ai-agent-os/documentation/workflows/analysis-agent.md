# Analysis Agent Workflow

- __Purpose__: Data processing, statistical analysis, pattern recognition, predictive modeling, and reporting.
- __Entry__: `POST /webhook/analysis/run`
- __Tools__: Statistical Analysis, Data Visualization

## Nodes
- __Webhook Analysis Input__: receives payload `{ dataset, target?, timeKey?, features?, tasks?, options? }`.
- __Normalize Input__: validates dataset and shapes options.
- __Data Quality Assessment__: missing values, numeric/non-numeric counts, uniqueness.
- __Statistical Analysis__: calls tool endpoint `/webhook/analysis/tools/statistical-analysis`.
- __Visualization Builder__: calls tool endpoint `/webhook/analysis/tools/data-visualization`.
- __AI Synthesize Analysis Report__: composes structured JSON report.
- __Respond__: returns `{ status, report, quality }`.

## Payload Examples
```json
{
  "dataset": [
    {"date": "2024-01-01", "sales": 120, "visits": 1000},
    {"date": "2024-01-02", "sales": 150, "visits": 1100}
  ],
  "target": "sales",
  "timeKey": "date",
  "tasks": ["describe", "correlation", "regression", "anomaly", "visualize"]
}
```

## Tool: Statistical Analysis
- __Descriptive__: mean, median, std, quantiles per numeric field.
- __Correlation__: pairwise Pearson correlation for numeric fields.
- __Regression__: simple linear regression (one feature) when `target` provided.
- __Anomaly__: z-score based outlier detection on `target`.
- __Inferential (optional)__: Welch t-test with `features:[groupKey]` and numeric `target`.

Endpoint: `POST /webhook/analysis/tools/statistical-analysis`

## Tool: Data Visualization
- Returns Vega-Lite specs for typical charts: time series, histogram, scatter.

Endpoint: `POST /webhook/analysis/tools/data-visualization`

## Outputs
- __report__: structured JSON with sections: executive_summary, data_quality_findings, key_insights, statistical_tests, predictive_models, anomalies, visualizations, recommendations, limitations, confidence.
- __quality__: summary from Data Quality Assessment node.

## Notes
- Ensure datasets are small-to-medium to avoid performance issues in a Function node.
- For heavier analytics or advanced ML, replace tool nodes with services (e.g., Python API) and keep interfaces unchanged.
