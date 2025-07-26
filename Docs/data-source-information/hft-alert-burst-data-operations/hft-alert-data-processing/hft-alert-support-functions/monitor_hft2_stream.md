# monitor\_hft2\_stream

The function `monitor_hft2_stream` that monitors changes in a specific file and publishes new data to a specified MQTT topic. Here's a step-by-step description of what the function does:

1. The function starts by checking if a pickle file named 'last\_size\_2.pkl' exists. This file is used to store the size of the last read from the monitored file. If it exists, the function loads this size.
2. The function then checks the current size of the monitored file.
3. If the current size is different from the last size (which means the file has changed), the function does the following:
   * It opens the file and seeks to the position of the last read.
   * It reads the new lines from the file.
   * For each new line, it creates a dictionary with keys 'Event\_Date\_Time' and 'S2' and the corresponding values from the line.
   * It converts the 'Event\_Date\_Time' value from an integer to a time object.
   * It combines 'Event\_Date\_Time' with the date extracted from the filename.
   * It converts 'Event\_Date\_Time' to a string in ISO 8601 format.
   * It generates an MQTT message for the Node-RED dashboard and publishes it to the specified MQTT topic.
4. Finally, the function updates the last size to the current size and saves it to a pickle file for future use.

The function returns the last size of the file. This can be used in subsequent calls to the function to continue reading from where it left off.
