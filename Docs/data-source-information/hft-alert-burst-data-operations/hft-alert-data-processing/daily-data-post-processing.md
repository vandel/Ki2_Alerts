# Daily Data Post Processing

The processing of the YYYYMMDD\_processed.json file is done with the following code:

<pre><code>// ```python
<strong>burst_analysis_file = "./Processed_Data/20240531_processed.json
</strong>
def read_daily_burst_data(burst_analysis_file):
    burst_base_schema = {
        "Symbol": pl.String,
        # "T1": pl.String,
        "Event_Date_Time": pl.Datetime,
        "NumQuotes":   pl.String,
        "BBO":   pl.String,
        "NumTrades":   pl.String,
        "Dollars":  pl.String,
        # "T3": pl.String,
        "Trade_Size": pl.Float64,
        "Price": pl.Float64,
        "Size": pl.Int64,
        "Volume": pl.Int64
    }

    df3 = pl.read_ndjson(burst_analysis_file, schema=burst_base_schema)
    fields_to_convert = ['NumQuotes', 'BBO', 'NumTrades', 'Dollars']  # replace with your actual fields

    for field in fields_to_convert:
        df3 = df3.with_columns(df3[field].cast(pl.Int64))
    return df3

df3 = read_daily_burst_data(burst_analysis_file)
df3

```
</code></pre>

The processing of the YYYYMMDD\_processed\_1.json file is done with the following code:

````
// TEMP PLACEHOLDER

```python
burst_analysis_1_file = "./Processed_Data/20240531_processed_1.json"

def read_daily_burst_data(burst_analysis_file):
    burst_base_schema = {
        "Symbol": pl.String,
        # "T1": pl.String,
        "Event_Date_Time": pl.Datetime,
        "NumQuotes":   pl.String,
        "BBO":   pl.String,
        "NumTrades":   pl.String,
        "Dollars":  pl.String,
        # "T3": pl.String,
        "Trade_Size": pl.Float64,
        "Price": pl.Float64,
        "Size": pl.Int64,
        "Volume": pl.Int64
    }

    df3 = pl.read_ndjson(burst_analysis_file, schema=burst_base_schema)
    fields_to_convert = ['NumQuotes', 'BBO', 'NumTrades', 'Dollars']  # replace with your actual fields

    for field in fields_to_convert:
        df3 = df3.with_columns(df3[field].cast(pl.Int64))
    return df3

df3 = read_daily_burst_data(burst_analysis_file)
df3

```


````
