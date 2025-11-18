# BurstDataProcessor User Guide

## Overview

The `BurstDataProcessor` class is a comprehensive data processing utility designed to read, enrich, and aggregate High-Frequency Trading (HFT) Alert Burst Monitor data. It automatically combines daily burst event records with symbol-specific details and provides multiple export formats and aggregation capabilities.

This class follows the DCAS (Data Capture and Archival System) logging pattern and uses Polars for high-performance data manipulation without external dependencies like pandas.

## Purpose and Use Cases

The `BurstDataProcessor` is designed for scenarios where you need to:

1. **Consolidate burst event data** from multiple daily CSV files into a unified dataset
2. **Enrich event records** with precise datetime information derived from filenames and event timestamps
3. **Incorporate symbol details** from burst-specific symbol files into each event record
4. **Export results** in multiple formats (Parquet, Excel)
5. **Generate statistical summaries** aggregated by date to identify trends and patterns
6. **Track high-frequency trading activity** with per-second granularity across different market symbols

## Initialization

### Constructor: `__init__(data_root: str, logger: Optional[logging.Logger] = None)`

**Purpose:** Initialize the BurstDataProcessor with required file paths and configuration.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_root` | `str` | Yes | Root directory path containing `Data_Burst` and `Data_Burst_Symbols` subdirectories. This is the base path where your burst event and symbol data are located. Example: `"C:\Users\username\Desktop\Projects\Ki2_Alerts\Data\Burst_Data\2025\11"` |
| `logger` | `Optional[logging.Logger]` | No | Custom logger instance for DCAS logging pattern compliance. If not provided, a default logger named `"DCAS.BurstDataProcessor"` will be created automatically. |

**Raises:**

- `FileNotFoundError`: If either `Data_Burst` or `Data_Burst_Symbols` folders do not exist at the specified `data_root` path.

**Example Usage:**

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger for BurstDataProcessor
processor_logger = logging.getLogger("DCAS.BurstDataProcessor")
processor_logger.setLevel(logging.INFO)

# Initialize processor
processor = BurstDataProcessor(
    data_root="C:\\Users\\vande\\Desktop\\Projects\\Ki2_Alerts\\Data\\Burst_Data\\2025\\11",
    logger=processor_logger
)
```

## Core Methods

### 1. `process_burst_data(date_filter: Optional[str] = None) -> pl.DataFrame`

**Purpose:** Read and process all burst event data files from the `Data_Burst` folder, enriching them with datetime information and symbol details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_filter` | `Optional[str]` | No | Optional date filter in format `'yyyymmdd'` to process only a specific date. If not provided, all CSV files in the folder are processed. Example: `'20251115'` processes only November 15, 2025 data. |

**Returns:** 

A Polars DataFrame with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `Event_Date_Time` | `Datetime` | Full datetime combining the date from filename and time from EventTime field (format: `YYYY-MM-DD HH:MM:SS`) |
| `Date` | `Date` | Date extracted from the filename (format: `YYYY-MM-DD`) |
| `EventTime` | `Int64` | Time in HHMMSS format from the original CSV (e.g., `93015` for 09:30:15) |
| `Grade` | `Int64` | Burst event grade classification |
| `ProgType` | `String` | Programming type ('0' or '1') indicating burst category |
| `Bckgrnd` | `Int64` | Background activity indicator |
| `S1` | `Int64` | Statistic 1 metric |
| `S2` | `Int64` | Statistic 2 metric |
| `CT` | `Int64` | Count Top indicator |
| `CB` | `Int64` | Count Bottom indicator |
| `CS` | `Int64` | Count Spread indicator |
| `Symbols` | `List[Dict]` | Struct containing symbol details with Symbol name, NumTrades, NumQuotes, and BBO values |

**Processing Steps:**

1. Locates all CSV files in the `Data_Burst` folder matching the pattern `yyyymmdd.csv`
2. For each file, extracts the date from the filename
3. Reads the burst event CSV with predefined schema
4. For each event row:
   - Parses the EventTime field from HHMMSS format
   - Creates a full Event_Date_Time by combining date and time
   - Searches for the corresponding symbol file: `Burst_yyyymmdd_hhmmss.csv`
   - Reads symbol details and stores as a struct
5. Combines all processed rows into a single unified DataFrame
6. Returns the complete dataset with all dates merged together

**Example Usage:**

```python
# Process all burst data
df = processor.process_burst_data()

# Or process only a specific date
df = processor.process_burst_data(date_filter='20251115')

# Check results
print(f"Processed {df.height} events across {df.width} columns")
```

**Raises:**

- `FileNotFoundError`: If no CSV files are found in the `Data_Burst` folder.
- `ValueError`: If a filename cannot be parsed to a valid date.

### 2. `get_dataframe() -> pl.DataFrame`

**Purpose:** Retrieve the processed dataframe for further analysis or inspection.

**Parameters:** None

**Returns:** The stored Polars DataFrame from the most recent `process_burst_data()` call.

**Raises:** 

- `RuntimeError`: If `process_burst_data()` has not been called yet.

**Example Usage:**

```python
df = processor.get_dataframe()
print(df.shape)
print(df.schema)
print(df.head(10))
```

### 3. `save_to_parquet(output_path: str, compression: str = 'snappy') -> None`

**Purpose:** Save the processed dataframe to a Parquet file for efficient storage and future retrieval.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `output_path` | `str` | Yes | File path where the Parquet file will be saved. Parent directories are created automatically if they don't exist. Example: `"output/burst_data.parquet"` |
| `compression` | `str` | No | Compression algorithm for the Parquet file. Default: `'snappy'`. Valid options: `'snappy'`, `'gzip'`, `'brotli'`, `'lz4'`, `'zstd'` |

**Returns:** None

**Raises:**

- `RuntimeError`: If `process_burst_data()` has not been called yet.
- `Exception`: If the file write operation fails (e.g., permission denied, disk full).

**Example Usage:**

```python
# Save with default Snappy compression
processor.save_to_parquet("output/burst_data.parquet")

# Save with gzip compression for better compression ratio
processor.save_to_parquet("output/burst_data.parquet", compression='gzip')

# Save with zstandard (zstd) for fast compression
processor.save_to_parquet("output/burst_data.parquet", compression='zstd')
```

**Features:**

- Parquet format preserves all data types including the Symbols struct
- Significantly smaller file size than CSV while maintaining all information
- Efficient for future reads and filtering operations
- Automatically creates parent directories if needed

### 4. `save_to_excel(output_path: str, exclude_symbols: bool = True) -> None`

**Purpose:** Export the processed dataframe to an Excel file (.xlsx) for easy sharing and manual analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `output_path` | `str` | Yes | File path where the Excel file will be saved. Parent directories are created automatically. Example: `"output/burst_data.xlsx"` |
| `exclude_symbols` | `bool` | No | If `True` (default), excludes the Symbols struct column from the Excel export since Excel cannot directly display complex structures. Set to `False` to include the Symbols column (will be displayed as text). |

**Returns:** None

**Raises:**

- `RuntimeError`: If `process_burst_data()` has not been called yet.
- `Exception`: If the file write operation fails or required Excel engine is not installed.

**Example Usage:**

```python
# Save Excel file excluding complex Symbols column (recommended)
processor.save_to_excel("output/burst_data.xlsx")

# Save Excel file including Symbols column as text
processor.save_to_excel("output/burst_data.xlsx", exclude_symbols=False)
```

**Features:**

- **Automatic date/time formatting**: Event_Date_Time column is formatted as `YYYY-MM-DD HH:MM:SS` for proper datetime display
- **EventTime formatting**: EventTime values are converted to 6-digit strings (e.g., `090003` instead of `90003`) to preserve leading zeros
- **Autofit columns**: Column widths are automatically adjusted to fit content
- **Clean data**: By default, removes the complex Symbols struct for easier Excel manipulation
- **Worksheet naming**: Creates a worksheet named "Burst Data"

**Requirements:**

- Either `xlsxwriter` or `openpyxl` package must be installed
- Install with: `pip install xlsxwriter` or `pip install openpyxl`

### 5. `extract_statistics() -> pl.DataFrame`

**Purpose:** Generate aggregated summary statistics from the burst data, providing one row per date with counts of event types and grades.

**Parameters:** None

**Returns:** A Polars DataFrame with one row per date containing:

| Column | Type | Description |
|--------|------|-------------|
| `Date` | `Date` | The date for this aggregation row |
| `Total_Events` | `UInt32` | Total number of burst events on this date |
| `ProgType_1_Count` | `UInt32` | Count of events where ProgType == '1' |
| `ProgType_0_Count` | `UInt32` | Count of events where ProgType == '0' |
| `Grade_X_Count` | `UInt32` | Count of events for each unique grade value (dynamically generated) |

**Raises:**

- `RuntimeError`: If `process_burst_data()` has not been called yet.

**Example Output:**

```
┌────────────┬──────────────┬──────────────────┬──────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Date       ┆ Total_Events ┆ ProgType_1_Count ┆ ProgType_0_Count ┆ Grade_1_Count   ┆ Grade_2_Count   ┆ Grade_3_Count   │
│ ---        ┆ ---          ┆ ---              ┆ ---              ┆ ---             ┆ ---             ┆ ---             │
│ date       ┆ u32          ┆ u32              ┆ u32              ┆ u32             ┆ u32             ┆ u32             │
╞════════════╪══════════════╪══════════════════╪══════════════════╪═════════════════╪═════════════════╪═════════════════╡
│ 2025-11-15 ┆ 150          ┆ 120              ┆ 30               ┆ 45              ┆ 60              ┆ 45              │
│ 2025-11-16 ┆ 180          ┆ 140              ┆ 40               ┆ 50              ┆ 70              ┆ 60              │
│ 2025-11-17 ┆ 165          ┆ 130              ┆ 35               ┆ 48              ┆ 65              ┆ 52              │
└────────────┴──────────────┴──────────────────┴──────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Example Usage:**

```python
# Extract statistics
stats = processor.extract_statistics()

# Display statistics
print(stats)

# Save statistics to Excel
stats.write_excel("output/burst_statistics.xlsx", worksheet="Statistics", autofit=True)

# Save statistics to CSV
stats.write_csv("output/burst_statistics.csv")

# Query specific dates
nov_15_stats = stats.filter(pl.col('Date') == datetime.date(2025, 11, 15))
print(nov_15_stats)
```

**Key Features:**

- **Dynamic Grade columns**: Automatically creates columns for each unique Grade value in the data
- **Chronological sorting**: Results are sorted by date in ascending order
- **Efficient aggregation**: Uses Polars' groupby operations for fast processing
- **Type preservation**: All counts are returned as UInt32 for memory efficiency

## Private Helper Methods

These methods are marked with an underscore prefix (internal use) but are documented for completeness:

### `_parse_date_from_filename(filename: str) -> datetime.date`

**Purpose:** Extract a date from a filename in format `yyyymmdd.csv`.

**Parameters:**
- `filename`: Filename string (e.g., `"20251115.csv"`)

**Returns:** `datetime.date` object

**Example:** `"20251115.csv"` → `datetime.date(2025, 11, 15)`

### `_parse_eventtime(eventtime: int) -> datetime.time`

**Purpose:** Convert EventTime from HHMMSS integer format to a `datetime.time` object.

**Parameters:**
- `eventtime`: Integer in HHMMSS format (e.g., `93015` for 09:30:15)

**Returns:** `datetime.time` object

**Example:** `93015` → `datetime.time(9, 30, 15)`

### `_read_symbol_file(date: datetime.date, eventtime: int) -> Optional[List[Dict[str, Any]]]`

**Purpose:** Read the corresponding symbol file for a burst event based on its date and time.

**Parameters:**
- `date`: Date of the burst event
- `eventtime`: EventTime in HHMMSS format

**Returns:** List of dictionaries containing symbol details, or `None` if the file doesn't exist

**File naming:** Looks for files named `Burst_yyyymmdd_hhmmss.csv`

## Data Flow Architecture

```
Data_Burst/
├── 20251115.csv ──┐
├── 20251116.csv ──┼─→ process_burst_data() ──→ Unified DataFrame ──┬─→ save_to_parquet()
└── 20251117.csv ──┘                                                ├─→ save_to_excel()
                                                                   └─→ extract_statistics()
Data_Burst_Symbols/
├── Burst_20251115_090003.csv
├── Burst_20251115_090004.csv
├── Burst_20251116_093015.csv
└── ...
```

## Complete Workflow Example

```python
import logging
import datetime
import polars as pl
from pathlib import Path

# Step 1: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

processor_logger = logging.getLogger("DCAS.BurstDataProcessor")
processor_logger.setLevel(logging.INFO)

# Step 2: Initialize processor
processor = BurstDataProcessor(
    data_root="C:\\Users\\vande\\Desktop\\Projects\\Ki2_Alerts\\Data\\Burst_Data\\2025\\11",
    logger=processor_logger
)

# Step 3: Process all burst data
df = processor.process_burst_data()

# Step 4: Inspect data
print(f"\n=== Data Summary ===")
print(f"Rows: {df.height}")
print(f"Columns: {df.width}")
print(f"\nSchema:")
print(df.schema)
print(f"\nFirst 5 rows:")
print(df.head(5))
print(f"\nUnique dates:")
unique_dates = df.select('Date').unique().sort('Date')
print(unique_dates)

# Step 5: Generate statistics
stats = processor.extract_statistics()
print(f"\n=== Statistics by Date ===")
print(stats)

# Step 6: Save results
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

processor.save_to_parquet(str(output_dir / "burst_data.parquet"))
processor.save_to_excel(str(output_dir / "burst_data.xlsx"))
stats.write_excel(str(output_dir / "burst_statistics.xlsx"))

# Step 7: Perform custom analysis on DataFrame
# Example: Find all events with Grade 3
grade_3_events = df.filter(pl.col('Grade') == 3)
print(f"\n=== Grade 3 Events ===")
print(f"Count: {grade_3_events.height}")

# Example: Count ProgType distribution
progtype_dist = df.group_by('ProgType').agg(pl.count().alias('Count'))
print(f"\n=== ProgType Distribution ===")
print(progtype_dist)

# Example: Get detailed symbol information for a specific event
event_with_symbols = df.filter(
    (pl.col('Date') == datetime.date(2025, 11, 15)) &
    (pl.col('EventTime') == 93015)
).select(['Event_Date_Time', 'Grade', 'Symbols'])
print(f"\n=== Event Details with Symbols ===")
print(event_with_symbols)
```

## Error Handling and Logging

The class implements comprehensive error handling and logging:

### Logging Levels

- **INFO**: Major operations (initialization, file processing completion, data saved)
- **DEBUG**: Detailed operations (file names being processed, symbol counts, schema details)
- **WARNING**: Missing symbol files (event processed without symbol details)
- **ERROR**: Critical failures (invalid dates, missing folders, read/write errors)

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: Data_Burst folder not found` | Path specified doesn't contain required folders | Verify `data_root` path exists and contains `Data_Burst` and `Data_Burst_Symbols` subdirectories |
| `No CSV files found in Data_Burst` | CSV files don't exist in the folder | Ensure CSV files in `yyyymmdd.csv` format exist in `Data_Burst` folder |
| Symbol files not found (warnings) | Corresponding `Burst_yyyymmdd_hhmmss.csv` files missing | This is non-fatal; events are still processed without symbol details |
| `RuntimeError: Data has not been processed` | Called save/export methods before `process_burst_data()` | Always call `process_burst_data()` first |
| Excel file shows dates as numbers (45964.38) | Excel formatting issue | Use `save_to_excel()` method which handles formatting automatically |

## Performance Considerations

- **Processing Speed**: Uses Polars for efficient in-memory operations; typically processes thousands of records per second
- **Memory Usage**: Entire dataset loaded into memory; for very large datasets (>1M records), consider filtering by date
- **File I/O**: Symbol files read individually per event; for performance, keep symbol files on fast storage
- **Parquet vs Excel**: Parquet format is 5-10x smaller and 10-20x faster for large datasets

## Dependencies

- **polars**: Core dataframe library for data manipulation
- **pathlib**: Filesystem path handling (built-in)
- **logging**: Logging framework (built-in)
- **datetime**: Date/time handling (built-in)
- **typing**: Type hints (built-in)
- **Optional Excel engine**: xlsxwriter or openpyxl (required only for Excel export)

## Conclusion

The `BurstDataProcessor` provides a complete solution for managing HFT Alert Burst Monitor data with minimal configuration, comprehensive logging, and flexible export options. It follows industry best practices with DCAS-compliant logging patterns and clean, maintainable code structure suitable for production environments.