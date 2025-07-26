# Read\_Levelone\_Equities Stream Data

LevelOne\_Equities is a stream of Quotation related data at the top level of the Order Book.  This includes a wide variety of timestamped data as well as an assortment of historical data such as 52 Week highs and dividend information.  The function to read this along with the schema is detailed below.

````
//```python
analysis_file='messages_L1.ndjson'

def read_level_one_equities(analysis_File):
    base_schema = {
        "service": pl.String,
        "timestamp":  pl.Int64,
        # "command": pl.String,
        "content": pl.List(
            pl.Struct(
                {
                    'key': pl.String,
                    # 'value': pl.String,
                    # 'delayed': pl.Boolean,
                    'assetMainType': pl.String,
                    'assetSubType': pl.String,
                    # 'cusip': pl.String,
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
                    # 'MARGINABLE': pl.Boolean,
                    # 'DESCRIPTION': pl.String,
                    'LAST_ID': pl.String,
                    'OPEN_PRICE': pl.Float64,
                    'NET_CHANGE': pl.Float64,
                    'HIGH_PRICE_52_WEEK': pl.Float64,
                    'LOW_PRICE_52_WEEK': pl.Float64,
                    # 'PE_RATIO': pl.Float64,
                    # 'DIVIDEND_AMOUNT': pl.Float64,
                    # 'DIVIDEND_YIELD': pl.Float64,
                    # 'NAV': pl.Int64,
                    'EXCHANGE_NAME': pl.String,
                    # 'DIVIDEND_DATE': pl.String,
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
                    # 'HTB_QUALITY': pl.Int64,
                    # 'HTB_RATE': pl.Int64,
                    # 'HARD_TO_BORROW': pl.Int64,
                    # 'IS_SHORTABLE': pl.Int64,
                    'POST_MARKET_NET_CHANGE': pl.Float64,
                    'POST_MARKET_NET_CHANGE_PERCENT': pl.Float64,
                }
            )
        )
    }

    df1 = pl.read_ndjson(analysis_file, schema=base_schema)
    # df1 = pl.read_ndjson(analysis_file)
    timestamp_fields = ['Event_Date_Time', 'QUOTE_TIME_MILLIS', 'TRADE_TIME_MILLIS', 'REGULAR_MARKET_TRADE_MILLIS', 'BID_TIME_MILLIS','ASK_TIME_MILLIS']

    # df2 = df_level_one_equities
    df2 = df1

    df2 = df2.with_columns(pl.col("content")).explode("content")

    df2 = df2.unnest('content')

    df2 = df2.rename({"timestamp":"Event_Date_Time"})
    df2 = df2.rename({"key":"Symbol"})

    for field in timestamp_fields:
        df2 = df2.with_columns(pl.from_epoch(df2['Event_Date_Time'], time_unit='ms').dt.convert_time_zone('US/Eastern').alias('Event_Date_Time'))

    return df2

df2 = read_level_one_equities(analysis_file)
df2
```
````

The use of  "explode" and "unnest" to unpack the content fields is described in the document above at:

{% content-ref url="../../design-considerations/general-data-framework.md" %}
[general-data-framework.md](../../design-considerations/general-data-framework.md)
{% endcontent-ref %}

The preliminary visualization implementation for this data will be documented here later.
