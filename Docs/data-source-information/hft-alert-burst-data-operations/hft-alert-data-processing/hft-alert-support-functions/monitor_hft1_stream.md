# monitor\_hft1\_stream

This Python function, `monitor_hft1_stream`, is designed to monitor a high-frequency trading (HFT) data stream encoded as a CSV file, read it, transform it's information and save it as and NDJson file in a new directory.. It reads new lines from a file, processes them, and writes the processed data to a new file ndjson file.  It also calculates an events per second (eps) rate.  A pickle file is used to mark how much of the daily file has already been processed to facilitate situations where the datastream is lost and restarted so that repeated date is not written to the output file that is opened in Append mode to minimize file processing operations.

Here's a step-by-step breakdown of what the function does:

1. The function takes five arguments: `most_recent_file`, `output_file`, `topic`, `client`, and `last_size`.
2. It checks if a pickle file named `last_size.pkl` exists. If it does, it loads the `last_size` from this file. This is used to facilitate restarting the analysis midday if problems arise.
3. It checks if the size of `most_recent_file` has changed since the last check. If it has, it reads the new lines from the file, starting from the position of the last read (`last_size`).
4. For each new line, it creates a dictionary with keys 'Symbol', 'T1', 'Event\_Date\_Time', 'NumQuotes', 'BBO', 'NumTrades', 'Dollars', 'T3', and 'Trade\_Size'. It then processes the 'Event\_Date\_Time' and 'Trade\_Size' fields.
5. It writes the processed data to `output_file` in JSON format.
6. It calculates the events per second (eps) rate, which is the number of new lines divided by the time difference between the first and last new line. This values published to the mqtt tope so that it can be monitor by other processes to implement analysis and user interface charting functions.
7. It updates `last_size` to the current size of `most_recent_file` and saves it to `last_size.pkl so that it is available for checking where future activities should begin.`
8. Finally, it returns `last_size`.

In summary, this function monitors a high-frequency trading (HFT) data stream, processes the new data, and writes it to a new file. It also calculates an events per second (eps) rate and facilitates restarting the analysis midday if problems arise.
