import polars as pl
import os
import io
import pickle
import time as pytime
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# class HFT1Handler(FileSystemEventHandler):
#     def __init__(self, csv_path, parquet_path, last_size_path, schema):
#         self.csv_path = csv_path
#         self.parquet_path = parquet_path
#         self.last_size_path = last_size_path
#         self.schema = schema

#     def on_modified(self, event):
#         if event.src_path.endswith(self.csv_path.split('/')[-1]):
#             df = monitor_and_update_hft1_parquet(
#                 csv_path=self.csv_path,
#                 parquet_path=self.parquet_path,
#                 last_size_path=self.last_size_path,
#                 schema=self.schema
#             )
#             print(f"Processed {df.height} rows. Last updated: {datetime.now()}")

def extract_date_from_filename_datetime(filename):
    import re
    date = re.search(r'\d{8}', filename)
    if date:
        return datetime.strptime(date.group(0), '%Y%m%d')
    return None

def int_to_time(time_int):
    time_str = str(time_int).zfill(6)
    hour = int(time_str[:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:])
    from datetime import time
    return time(hour=hour, minute=minute, second=second)

def monitor_and_update_hft1_parquet(csv_path, parquet_path, last_size_path, schema):
    last_size = 0
    if os.path.exists(last_size_path):
        with open(last_size_path, 'rb') as f:
            last_size = pickle.load(f)

    current_size = os.stat(csv_path).st_size

    if current_size == last_size and os.path.exists(parquet_path):
        return pl.read_parquet(parquet_path)

    with open(csv_path, 'r') as f:
        f.seek(last_size)
        new_lines = f.readlines()

    if not new_lines:
        if os.path.exists(parquet_path):
            return pl.read_parquet(parquet_path)
        else:
            return pl.DataFrame(schema=schema)

    new_df = pl.read_csv(
        source=io.StringIO(''.join(new_lines)),
        has_header=False,
        schema=schema
    )

    temp_date = extract_date_from_filename_datetime(csv_path)

    new_df = new_df.with_columns([
        pl.col('Event_Date_Time').map_elements(lambda x: int_to_time(int(x)), return_dtype=pl.Time).alias('Event_Date_Time')
    ])
    new_df = new_df.with_columns([
        pl.col('Event_Date_Time').map_elements(lambda x: datetime.combine(temp_date, x), return_dtype=pl.Datetime).alias('Event_Date_Time')
    ])
    new_df = new_df.with_columns([
        (pl.col('Dollars') / pl.col('NumTrades')).alias('Trade_Size')
    ])
    new_df = new_df.drop_nulls(subset=['Dollars'])
    new_df = new_df.sort('Event_Date_Time')

    if os.path.exists(parquet_path):
        old_df = pl.read_parquet(parquet_path)
        full_df = pl.concat([old_df, new_df])
    else:
        full_df = new_df

    full_df.write_parquet(parquet_path)

    with open(last_size_path, 'wb') as f:
        pickle.dump(current_size, f)

    return full_df

if __name__ == "__main__":
    schema = {
        "Symbol": pl.Utf8,
        "T1": pl.Utf8,
        "Event_Date_Time": pl.Utf8,
        "NumQuotes": pl.Int64,
        "BBO": pl.Int64,
        "NumTrades": pl.Int64,
        "Dollars": pl.Float64,
        "T3": pl.Utf8
    }
    # csv_path = "./Data/20250722_hft1.csv"
    # parquet_path = "./Processed_Data/20250722_hft1.parquet"
    # last_size_path = "./Data/20250722_hft1_lastsize.pkl"

    # filepath: c:\Users\vande\Desktop\Projects\Ki2_Alerts\Code\monitor_hft1_file.py

    # today_str = datetime.today().strftime('%Y%m%d')

    today_str = datetime.today().strftime('%Y%m%d')
    print(f"Today's date string: {today_str}")

    # make today-str year/month/day format
    today_str1 = datetime.today().strftime('%Y/%m/')
    print(f"Today's date string in year/month/day format: {today_str1}{today_str}")

    csv_path = f"./Code/Data/{today_str}_hft1.csv"
    print(f"Today's csv_path: {csv_path}")
    parquet_path = f"./Code/Processed_Data/{today_str1}{today_str}_hft1.parquet"
    print(f"Today's parquet_path: {parquet_path}")
    last_size_path = f"./Code/Data/{today_str}_hft1_lastsize.pkl"
    print(f"Today's last_size_path: {last_size_path}")
    print("Monitoring started. Press Ctrl+C to exit.")
    last_size=0
    try:
        while True:
            df = monitor_and_update_hft1_parquet(
                csv_path=csv_path,
                parquet_path=parquet_path,
                last_size_path=last_size_path,
                schema=schema
            )
            print(f"Processed {df.height} rows. Last updated: {datetime.now()}")
            pytime.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")

    # print(os.path.abspath("./Code/Data"))
    # print(os.path.isdir("./Code/Data")) 

    # event_handler = HFT1Handler(csv_path, parquet_path, last_size_path, schema)
    # observer = Observer()
    # observer.schedule(event_handler, path="./Code/Data", recursive=False)
    # observer.start()
    # print("Monitoring started. Press Ctrl+C to exit.")
    # try:
    #     while True:
    #         pytime.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()