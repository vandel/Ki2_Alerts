---
description: >-
  This routine scans the  .hft1 files on a 10 second scan basis and generates a
  parquet file in a directory structure ./Code/Processed_Data/yyyy/mm with the
  file names yyyymmdd_hft1.parquet
---

# monitor\_and\_update\_hft1\_parquet

The [monitor\_and\_update\_hft1\_parquet](https://vscode-file/vscode-app/c:/Users/vande/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) function monitors a CSV file for new data and appends any new rows to a Parquet file, maintaining a record of the last read position to avoid reprocessing data.

**How it works:**

* It checks if a pickle file ([last\_size\_path](https://vscode-file/vscode-app/c:/Users/vande/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)) exists to determine the last read byte position in the CSV.
* It compares the current file size to the last read size. If unchanged and a Parquet file exists, it simply returns the Parquet data.
* If the file has grown, it reads only the new lines, processes them into a Polars DataFrame, and applies several transformations:
  * Converts the event time from integer to [datetime](https://vscode-file/vscode-app/c:/Users/vande/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html).
  * Calculates a `Trade_Size` column.
  * Drops rows with null `Dollars` values and sorts by event time.
* It appends the new data to the existing Parquet file (if present) or creates a new one.
* The function updates the pickle file with the new file size and returns the full DataFrame.

Here are the parameters for the [monitor\_and\_update\_hft1\_parquet](https://vscode-file/vscode-app/c:/Users/vande/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) function:

* **csv\_path**:\
  The file path to the CSV file being monitored for new data.
* **parquet\_path**:\
  The file path to the Parquet file where processed data is stored and updated.
* **last\_size\_path**:\
  The file path to a pickle file that stores the last read byte position in the CSV file, allowing the function to only process new data.
* **schema**:\
  A dictionary defining the expected column names and data types for the CSV/Polars DataFrame. This ensures correct parsing and typing of the incoming data.

This approach efficiently processes only new data as it arrives in the CSV, making it suitable for real-time or near-real-time data pipelines.
