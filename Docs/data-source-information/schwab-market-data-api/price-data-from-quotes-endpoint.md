# Price Data From Quotes Endpoint

The Function Schwab\_Trades\_1.py builds an NDJSON file with price data and also publishes this data to the MQTT topic price\_data.

The topic prices\_data,  when it arrives in Node-Red is processed by a function node that processes and scales numerical data associated with various properties (like 'Dollars', 'NumQuotes', 'BBO', 'NumTrades', etc.) from incoming messages (`msg.payload`). It performs the following operations:

1. **Scale Data Function (`scaleData`)**: A helper function that takes an array of numbers ([`data`](https://vscode-file/vscode-app/c:/Users/vandel/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)) as input and scales each number to a range between 0 and 1 based on the minimum and maximum values in the array. This is a common preprocessing step in data analysis and machine learning to normalize data.
2. **Retrieve or Initialize `value` Object**: It attempts to retrieve a previously stored object named `value` from the Node-RED context. If it doesn't exist, it initializes `value` as an empty object. This object is used to accumulate and manage data across multiple invocations of the function node.
3. **Determine Properties to Track**: It fetches a list of properties (`ticker_list`) from the global context, which represents the types of data to track and process. Alternatively, a hardcoded list of properties can be used.
4. **Update and Manage Data Arrays**: For each property in the `properties` list, it ensures there is an array in the `value` object to store its data. If the incoming message (`msg.payload`) contains data for a property, it converts that data to a number (assuming it represents the price), adds it to the corresponding array, and ensures the array does not exceed 900 elements by removing the oldest elements as needed.
5. **Store Updated `value` Object**: The updated `value` object is stored back in the context for future use, ensuring that data is accumulated and managed over time.
6. **Prepare Output Message (`msg`)**: The original message payload is replaced with the `value` object, containing arrays of raw data for each property.
7. **Scale Data for Each Property**: It creates a new object `scaledValue` to store the scaled data. For each property in `value`, it uses the `scaleData` function to scale the data array and stores the result in `scaledValue`.
8. **Set Scaled Data in Output Message**: The scaled data (`scaledValue`) is attached to the output message (`msg`) under `msg.scaled`.
9. **Return Modified Message**: Finally, the modified message, now containing both the raw and scaled data for each property, is returned from the function node.  The msg.payload contains the values and the msg.scaled has the scaled values.

