
# NYC Taxi Data Pipeline — Architecture

```mermaid
flowchart TD
    A["NYC TLC Trip Records<br/>Parquet Files"]
    B["Source Manifest<br/>24 files: 4 taxi types × 6 months"]
    C["Schema Inspection<br/>DuckDB + httpfs"]
    D["Data Ingestion<br/>Read Parquet from CloudFront"]
    E["Transformation<br/>Parse pickup datetime<br/>Filter Jan–Jun 2024"]
    F["Data Quality Validation<br/>Nulls, date range,<br/>row accounting, coverage"]
    G["Curated Dataset<br/>Monthly trip counts"]
    H["Analysis<br/>Aggregate trips by taxi type<br/>Calculate percentage and rank"]
    I["Final Result<br/>HVFHV — 120,864,668 trips"]
    J["Execution Evidence<br/>Pipeline status, logs,<br/>quality reports and summaries"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    F --> J
    H --> J
```
