---
description: >-
  This page describes how to use the code to perrorm experiments on live market
  data.
---

# Daily Operation

The initial code for this project consists of a python file monitor\_hft1\_file.py that handles the scanning of the HFT Alert Burst Monitor files to generate a near real time .parquet file of the days events.

This file should be executed from a terminal command line in VS Code and can be terminated by CTRL-C in the same terminal.  It will generate a yyyymm\_hftq.parquet file in a ./Code/Processed\_Data/yyyy/mm/yyyymmdd\_hft1\_parquet file.

During the course of the trading day this file can be loaded for further analysis into the cells of the Jupyter Notebook Burst\_Monitor\_Capture.ipynb. The analysis in the notebook is experimental at this stage to present an introduction to what is possible.  It is the intent of this project to elaborate on this notebook and in our efforts to identify actionable edges using this data.
