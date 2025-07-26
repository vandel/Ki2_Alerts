# General Data Framework

Large quantities of real-time queried data and streaming data are required to obtain the information need to execute the analysis.  This make the issue of efficiently capturing and storing information one of upmost importance.  This section of this document will describe the methodology settled on to accomplish this.

Design principles that have been settled on are as follows:

* When messages arrive from data sources they must be stored with minimal processing and in a manner that existing information does not need to be rewritten when capturing the new information to file.  This has lead to the determination that NDJSON (Newline Deliiminted JSON ) will be the first storage format used.  This allows data capture files to be opened in "Append" mode with data being added to the end of each file when new data arrives.  Each line of the NDJSON file will contain the information from one response message from the data source.  This does not mean that the information in a particular message pertains to only one symbol or event, but rather it means that whatever is returned by the data source in a single message is saved to file as an individual line of JSON code.  This also does not mean that the file saving process always occurs as son as the data arrives.  IN the case of streaming data, incoming data may be buffer for some period of time or until some number of messages are available and then written to disk on a periodic basis and the buffers zeroed out.  This is done to take advantage of any situations where multiple messages may be mode efficently processed through vector type operations rather than individual calculations as each message arrive.  The desire to have this as an option is one of the reasons why Polars has been chosen as the primary dataframe storage solution rather than Pandas, although there may be situations where operations are done in Pandas if functionality is available there and not available in Polars.  The use of Pandas, however, is intended to be minimize and when possible avoided.
* The recovery of data from an NDJSON file begins with the definition of a base\_schema that describes the form that format of the various data elements and the dictionaries and structure within the file.  Here is an example of the base-schema for Items streamed from the LEVELONE\_EQUITES  and NASDAQ\_BOOK streaming endpoints from Charlse Schwab.  The particular data file used in this example was obtained using the following code to capture the data.

````
```python
ticker_list = ['SPY', 'QQQ', 'TQQQ', 'IWM', 'AAPL', 'SQQQ', 'GOOG', 'TLT', 'GOOGL', 'SH']

stream_client = StreamClient(c)

async def read_stream():
    try:
        await stream_client.login()

        def print_message(message):
            # Convert the message to a JSON string
            message_str = json.dumps(message)
            # Print the message
            print(message_str)
            # Append the message to the ndjson file
            with open('messages.ndjson', 'a') as f:
                f.write(message_str + '\n')

        #Status - Returning Values    
        stream_client.add_level_one_equity_handler(print_message)
        await stream_client.level_one_equity_subs(ticker_list)

        #Status - Returns Values
        stream_client.add_nasdaq_book_handler(print_message)
        await stream_client.nasdaq_book_subs(ticker_list)

        while True:
            await stream_client.handle_message()
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        # Add any cleanup code here

# asyncio.run(read_stream())

# Create a task for the coroutine
task = asyncio.create_task(read_stream())

# Run the task
await task
```
````

````
```python
base_schema = {
    "service": pl.String,
    "timestamp":  pl.Int64,
    "command": pl.String,
    "content": pl.List(
        pl.Struct(
            {
                'key': pl.String,
                # 'value': pl.String,
                'delayed': pl.Boolean,
                'assetMainType': pl.String,
                'assetSubType': pl.String,
                'cusip': pl.String,
                'BID_PRICE': pl.Float64,
                'ASK_PRICE': pl.Float64,
                'LAST_PRICE': pl.Float64,
                'BID_SIZE': pl.Int64,
                'ASK_SIZE': pl.Int64,
                'ASK_ID': pl.String,
                'BID_ID': pl.String,
                'TOTAL_VOLUME': pl.Int64,
                'LAST_SIZE': pl.Int64,
                'HIGH_PRICE': pl.Float64,
                'LOW_PRICE': pl.Float64,
                'CLOSE_PRICE': pl.Float64,
                'EXCHANGE_ID': pl.String,
                'MARGINABLE': pl.Boolean,
                'DESCRIPTION': pl.String,
                'LAST_ID': pl.String,
                'OPEN_PRICE': pl.Float64,
                'NET_CHANGE': pl.Float64,
                'HIGH_PRICE_52_WEEK': pl.Float64,
                'LOW_PRICE_52_WEEK': pl.Float64,
                'PE_RATIO': pl.Float64,
                'DIVIDEND_AMOUNT': pl.Float64,
                'DIVIDEND_YIELD': pl.Float64,
                'NAV': pl.Int64,
                'EXCHANGE_NAME': pl.String,
                'DIVIDEND_DATE': pl.String,
                'REGULAR_MARKET_QUOTE': pl.Boolean,
                'REGULAR_MARKET_TRADE': pl.Boolean,
                'REGULAR_MARKET_LAST_PRICE': pl.Float64,
                'REGULAR_MARKET_LAST_SIZE': pl.Int64,
                'REGULAR_MARKET_NET_CHANGE': pl.Float64,
                'SECURITY_STATUS': pl.String,
                'MARK': pl.Float64,
                'QUOTE_TIME_MILLIS': pl.Int64,
                'TRADE_TIME_MILLIS': pl.Int64,
                'REGULAR_MARKET_TRADE_MILLIS': pl.Int64,
                'BID_TIME_MILLIS': pl.Int64,
                'ASK_TIME_MILLIS': pl.Int64,
                'ASK_MIC_ID': pl.String,
                'BID_MIC_ID': pl.String,
                'LAST_MIC_ID': pl.String,
                'NET_CHANGE_PERCENT': pl.Float64,
                'REGULAR_MARKET_CHANGE_PERCENT': pl.Float64,
                'MARK_CHANGE': pl.Float64,
                'MARK_CHANGE_PERCENT': pl.Float64,
                #'HTB_QUALITY': pl.Int64,
                #'HTB_RATE': pl.Int64,
                'HARD_TO_BORROW': pl.Int64,
                'IS_SHORTABLE': pl.Int64,
                'POST_MARKET_NET_CHANGE': pl.Float64,
                'POST_MARKET_NET_CHANGE_PERCENT': pl.Float64,
            }
        )
    )
}

analysis_file = 'messages.ndjson'
df1 = pl.read_ndjson(analysis_file, schema=base_schema)
df1

base_schema
```
````

The above code reads in the entire file.  It should be noted that the list of fields presented in the base\_schema is intended to be complete, but many of the fields are likely not relevant to the analysis.  If the field is considered to be not required, all that is required to eliminate it from further consideration is to comment out the line in the base\_schema out and this field will not be included.  This is far more efficient than writing code after the data has been read to eliminate it, and far easier to maintain should requirements change.  The "value", "HTB\_QUALITY" and "HTB\_RATE" items in the above code are examples of this.  The data is now ready for further operations such as replacing Epoch formatted time in millisecond timestamps with Datetime information. This can now be accomplished as follows:

````
```python
timestamp_fields = ['timestamp', 'QUOTE_TIME_MILLIS', 'TRADE_TIME_MILLIS', 'REGULAR_MARKET_TRADE_MILLIS', 'BID_TIME_MILLIS','ASK_TIME_MILLIS']

df2 = df1

df2 = df2.with_columns(pl.col("content")).explode("content")

df2 = df2.unnest('content')

for field in timestamp_fields:
    df2 = df2.with_columns(
        (df2[field].cast(pl.Int64) * 1000).cast(pl.Datetime).alias(field)
    )

df2
```
````

A detailed look at the base\_schema defined above shows that when a list of tickers is requested from the streaming API that the "content" returned is a list of structs with one element of the list for every ticker.  The code snippet immediately above shows the polars function "explode" and "unnest" in action.  The explode command expands the content list into individual structs, one for each symbol. Once in this form the unnest command breaks the struct into its constituent columns for processing using the iterator over the list of fields that need modification.

