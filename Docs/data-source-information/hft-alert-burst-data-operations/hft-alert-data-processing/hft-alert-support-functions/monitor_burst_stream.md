# monitor\_burst\_stream

This Python function, `monitor_burst_stream`, is designed to monitor a burst data stream. It reads new lines from a file, processes them, and writes the processed data to a new file. It also calculates a burst per second (bps) rate.

Here's a step-by-step breakdown of what the function does:

1. The function takes five arguments: `most_recent_file_1`, `output_file_1`, `topic_1`, `client`, and `last_size`.
2. It checks if a pickle file named `last_size_1.pkl` exists. If it does, it loads the `last_size` from this file. This is used to facilitate restarting the analysis midday if problems arise.
3. It checks if the size of `most_recent_file_1` has changed since the last check. If it has, it reads the new lines from the file, starting from the position of the last read (`last_size`).
4. For each new line, it creates a dictionary with keys 'Event\_Date\_Time', 'Grade', 'ProgType', 'Bckgrnd', 'S1', 'S2', 'CT', 'CB', and 'Burst\_Symbols'. It then processes the 'Event\_Date\_Time' field and reads the 'Burst\_Symbols' from a separate file and adds the information for these symbols to a new json key burst\_symbols.
5. It writes the processed data to `output_file_1` in JSON format.
6. It calculates the burst per second (bps) rate, which is the number of new lines divided by the time difference between the first and last new line. It publishes this information using mqtt so that other process in the analysis and user interface change can subscribe to these values.
7. It updates `last_size` to the current size of `most_recent_file_1` and saves it to `last_size_1.pkl`.
8. Finally, it returns `last_size`.

In summary, this function monitors a burst data stream, processes the new data, and writes it to a new file. It also calculates a burst per second (bps) rate and facilitates restarting the analysis midday if problems arise.
