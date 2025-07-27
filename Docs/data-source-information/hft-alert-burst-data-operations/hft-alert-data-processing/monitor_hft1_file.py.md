---
description: >-
  This is a python file that defines the necessary support functions and
  executes the monitoring of the hft1 file during the trading day.
---

# monitor\_hft1\_file.py

This Python script monitors a daily-updated CSV file containing high-frequency trading (HFT) burst data, processes any new data appended to the file, and stores the results in a Parquet file for efficient access and analysis.

**Key features:**

* **File Monitoring Loop:**\
  The script runs in a loop, checking the CSV file (named with today’s date) every 10 seconds for new data.
* **Incremental Processing:**\
  It remembers how much of the CSV file has already been processed (using a pickle file to store the last read position) and only reads and processes new lines.
* **Data Transformation:**\
  New data is loaded into a Polars DataFrame, where:
  * The event time is converted from integer format to a Python datetime.
  * A new column, `Trade_Size`, is calculated as `Dollars / NumTrades`.
  * Rows with missing `Dollars` values are dropped.
  * The data is sorted by event time.
* **Efficient Storage:**\
  The new data is appended to an existing Parquet file (or a new one is created if it doesn’t exist), allowing for fast future reads.
* **Schema Enforcement:**\
  The script enforces a strict schema for the data, ensuring correct data types for each column.
* **Robustness:**\
  The script handles keyboard interrupts gracefully and prints status updates to the console.

**Summary:**\
This script is designed for real-time or near-real-time ingestion and transformation of HFT burst data, making it suitable for automated trading analytics pipelines or alerting systems.
