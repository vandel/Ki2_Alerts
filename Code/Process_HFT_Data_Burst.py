"""
HFT Alert Burst Monitor Data Processor
Reads burst event data and associated symbol details into a unified Polars DataFrame.
"""

import polars as pl
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import datetime


class BurstDataProcessor:
    """
    Processes HFT Alert Burst Monitor data from Data_Burst and Data_Burst_Symbols folders.
    
    Reads daily burst event CSV files, enriches them with event datetime information,
    and joins with detailed symbol data from corresponding burst-specific files.
    """
    
    def __init__(
        self,
        data_root: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize BurstDataProcessor.
        
        Args:
            data_root: Root directory containing Data_Burst and Data_Burst_Symbols folders
            logger: Optional logger instance
        """
        # Setup logger
        self.logger = logger or logging.getLogger(f"DCAS.{self.__class__.__name__}")
        
        # Initialize paths
        self.data_root = Path(data_root)
        self.data_burst_path = self.data_root / "Data_Burst"
        self.data_burst_symbols_path = self.data_root / "Data_Burst_Symbols"
        
        # Validate paths
        if not self.data_burst_path.exists():
            raise FileNotFoundError(f"Data_Burst folder not found: {self.data_burst_path}")
        if not self.data_burst_symbols_path.exists():
            raise FileNotFoundError(f"Data_Burst_Symbols folder not found: {self.data_burst_symbols_path}")
        
        self.dataframe: Optional[pl.DataFrame] = None
        
        self.logger.info(
            f"{self.__class__.__name__} initialized with data_root: {data_root}"
        )
    
    def _parse_date_from_filename(self, filename: str) -> datetime.date:
        """
        Extract date from filename in format yyyymmdd.csv.
        
        Args:
            filename: Filename in format yyyymmdd.csv
            
        Returns:
            datetime.date object
        """
        try:
            date_str = filename.replace('.csv', '')
            return datetime.datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError as e:
            self.logger.error(f"Failed to parse date from filename {filename}: {e}")
            raise
    
    def _parse_eventtime(self, eventtime: int) -> datetime.time:
        """
        Parse EventTime from HHMMSS integer format to time object.
        
        Args:
            eventtime: Time in HHMMSS format (e.g., 93015 for 09:30:15)
            
        Returns:
            datetime.time object
        """
        try:
            eventtime_str = str(eventtime).zfill(6)
            hour = int(eventtime_str[0:2])
            minute = int(eventtime_str[2:4])
            second = int(eventtime_str[4:6])
            return datetime.time(hour, minute, second)
        except (ValueError, IndexError) as e:
            self.logger.error(f"Failed to parse EventTime {eventtime}: {e}")
            raise
    
    def _read_symbol_file(
        self, 
        date: datetime.date, 
        eventtime: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Read the corresponding symbol file for a burst event.
        
        Args:
            date: Date of the burst event
            eventtime: EventTime in HHMMSS format
            
        Returns:
            List of dictionaries containing symbol details, or None if file not found
        """
        try:
            # Format filename: Burst_yyyymmdd_hhmmss.csv
            date_str = date.strftime('%Y%m%d')
            time_str = str(eventtime).zfill(6)
            symbol_filename = f"Burst_{date_str}_{time_str}.csv"
            symbol_filepath = self.data_burst_symbols_path / symbol_filename
            
            if not symbol_filepath.exists():
                self.logger.warning(f"Symbol file not found: {symbol_filepath}")
                return None
            
            # Read symbol data
            symbol_df = pl.read_csv(
                symbol_filepath,
                schema={
                    'Symbol': pl.Utf8,
                    'NumTrades': pl.Int64,
                    'NumQuotes': pl.Int64,
                    'BBO': pl.Int64
                }
            )
            
            # Convert to list of dicts for struct creation
            symbol_list = symbol_df.to_dicts()
            
            self.logger.debug(
                f"Read {len(symbol_list)} symbols from {symbol_filename}"
            )
            
            return symbol_list
            
        except Exception as e:
            self.logger.error(
                f"Error reading symbol file for {date} {eventtime}: {e}"
            )
            return None
    
    def process_burst_data(self, date_filter: Optional[str] = None) -> pl.DataFrame:
        """
        Process all burst data files from Data_Burst folder.
        
        Args:
            date_filter: Optional date filter in format 'yyyymmdd' to process only specific date
            
        Returns:
            Polars DataFrame with burst events and associated symbol details
        """
        try:
            self.logger.info("Starting burst data processing")
            
            # Find all CSV files in Data_Burst folder
            csv_files = sorted(self.data_burst_path.glob('*.csv'))
            
            if date_filter:
                csv_files = [f for f in csv_files if f.stem == date_filter]
            
            if not csv_files:
                raise FileNotFoundError(
                    f"No CSV files found in {self.data_burst_path}"
                )
            
            self.logger.info(f"Found {len(csv_files)} burst data files to process")
            
            # Collect all processed rows across all files
            all_data = []
            
            for csv_file in csv_files:
                self.logger.debug(f"Processing file: {csv_file.name}")
                
                # Parse date from filename
                file_date = self._parse_date_from_filename(csv_file.name)
                
                # Read burst event data
                burst_df = pl.read_csv(
                    csv_file,
                    schema={
                        'EventTime': pl.Int64,
                        'Grade': pl.Int64,
                        'ProgType': pl.Utf8,
                        'Bckgrnd': pl.Int64,
                        'S1': pl.Int64,
                        'S2': pl.Int64,
                        'CT': pl.Int64,
                        'CB': pl.Int64,
                        'CS': pl.Int64
                    }
                )
                
                # Process each row to add Event_Date_Time and Symbols
                for row in burst_df.iter_rows(named=True):
                    eventtime = row['EventTime']
                    
                    # Create Event_Date_Time
                    event_time = self._parse_eventtime(eventtime)
                    event_datetime = datetime.datetime.combine(file_date, event_time)
                    
                    # Read corresponding symbol file
                    symbols_data = self._read_symbol_file(file_date, eventtime)
                    
                    # Build row with all data
                    processed_row = {
                        'Event_Date_Time': event_datetime,
                        'Date': file_date,
                        'EventTime': eventtime,
                        'Grade': row['Grade'],
                        'ProgType': row['ProgType'],
                        'Bckgrnd': row['Bckgrnd'],
                        'S1': row['S1'],
                        'S2': row['S2'],
                        'CT': row['CT'],
                        'CB': row['CB'],
                        'CS': row['CS'],
                        'Symbols': symbols_data
                    }
                    
                    all_data.append(processed_row)
                
                self.logger.info(
                    f"Processed {burst_df.height} events from {csv_file.name}"
                )
            
            # Create final DataFrame from all collected data
            self.dataframe = pl.DataFrame(all_data)
            
            # Ensure proper schema for Symbols struct
            if self.dataframe.height > 0:
                self.logger.info(
                    f"Successfully created DataFrame with {self.dataframe.height} rows "
                    f"and {self.dataframe.width} columns across {len(csv_files)} file(s)"
                )
                self.logger.debug(f"DataFrame schema: {self.dataframe.schema}")
            
            return self.dataframe
            
        except Exception as e:
            self.logger.error(f"Error processing burst data: {e}")
            raise
    
    def get_dataframe(self) -> pl.DataFrame:
        """
        Get the processed dataframe.
        
        Returns:
            Polars DataFrame with burst events and symbol details
            
        Raises:
            RuntimeError: If data has not been processed yet
        """
        if self.dataframe is None:
            self.logger.error("No dataframe available. Call process_burst_data() first.")
            raise RuntimeError(
                "Data has not been processed. Call process_burst_data() first."
            )
        
        return self.dataframe
    
    def save_to_parquet(
        self, 
        output_path: str,
        compression: str = 'snappy'
    ) -> None:
        """
        Save the dataframe to a Parquet file.
        
        Args:
            output_path: Path where the Parquet file will be saved
            compression: Compression algorithm ('snappy', 'gzip', 'brotli', 'lz4', 'zstd')
        """
        try:
            if self.dataframe is None:
                raise RuntimeError(
                    "No dataframe to save. Call process_burst_data() first."
                )
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Saving dataframe to Parquet: {output_path}")
            
            self.dataframe.write_parquet(
                output_path,
                compression=compression
            )
            
            self.logger.info(
                f"Successfully saved {self.dataframe.height} rows to {output_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Error saving to Parquet: {e}")
            raise
    
    def save_to_excel(
        self, 
        output_path: str,
        exclude_symbols: bool = True
    ) -> None:
        """
        Save the dataframe to an Excel file.
        
        Args:
            output_path: Path where the Excel file will be saved
            exclude_symbols: If True, exclude the Symbols struct column (default: True)
        """
        try:
            if self.dataframe is None:
                raise RuntimeError(
                    "No dataframe to save. Call process_burst_data() first."
                )
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Saving dataframe to Excel: {output_path}")
            
            # Select columns (exclude Symbols if requested)
            if exclude_symbols and 'Symbols' in self.dataframe.columns:
                df_to_save = self.dataframe.drop('Symbols')
                self.logger.debug("Excluding Symbols column from Excel export")
            else:
                df_to_save = self.dataframe
            
            # Format EventTime as 6-digit string (e.g., 090003 instead of 90003)
            # This preserves leading zeros in Excel
            df_to_save = df_to_save.with_columns(
                pl.col('EventTime').cast(pl.Utf8).str.zfill(6).alias('EventTime')
            )
            
            # Write directly to Excel using Polars
            df_to_save.write_excel(
                output_path,
                worksheet='Burst Data',
                autofit=True,
                dtype_formats={
                    pl.Datetime: 'yyyy-mm-dd hh:mm:ss'
                }
            )
            
            self.logger.info(
                f"Successfully saved {df_to_save.height} rows and "
                f"{len(df_to_save.columns)} columns to {output_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")
            raise

    def extract_statistics(self) -> pl.DataFrame:
        """
        Extract aggregated statistics from the burst data by date.
        
        Returns a single row per date with:
        - Total count of ProgType == '1'
        - Total count of ProgType == '0'
        - Total count for each unique Grade value
        
        Returns:
            Polars DataFrame with date-level statistics
            
        Raises:
            RuntimeError: If data has not been processed yet
        """
        try:
            if self.dataframe is None:
                self.logger.error("No dataframe available. Call process_burst_data() first.")
                raise RuntimeError(
                    "Data has not been processed. Call process_burst_data() first."
                )
            
            self.logger.info("Extracting date-level statistics")
            
            # Get unique grades for dynamic column creation
            unique_grades = sorted(self.dataframe.select('Grade').unique().to_series().to_list())
            self.logger.debug(f"Found unique grades: {unique_grades}")
            
            # Aggregate by Date
            stats_df = self.dataframe.group_by('Date').agg([
                # Count total events per date
                pl.count().alias('Total_Events'),
                
                # Count ProgType == '1'
                pl.col('ProgType').filter(pl.col('ProgType') == '1').count().alias('ProgType_1_Count'),
                
                # Count ProgType == '0'
                pl.col('ProgType').filter(pl.col('ProgType') == '0').count().alias('ProgType_0_Count'),
                
                # Count each unique grade
                *[
                    pl.col('Grade').filter(pl.col('Grade') == grade).count().alias(f'Grade_{grade}_Count')
                    for grade in unique_grades
                ]
            ]).sort('Date')
            
            self.logger.info(
                f"Extracted statistics for {stats_df.height} date(s) with {stats_df.width} columns"
            )
            self.logger.debug(f"Statistics schema: {stats_df.schema}")
            
            return stats_df
            
        except Exception as e:
            self.logger.error(f"Error extracting statistics: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize processor
    processor = BurstDataProcessor(
        data_root="/path/to/hft/data"
    )
    
    # Process all burst data
    df = processor.process_burst_data()
    
    # Display summary
    print(f"\nProcessed DataFrame:")
    print(f"Rows: {df.height}")
    print(f"Columns: {df.width}")
    print(f"\nSchema:")
    print(df.schema)
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nLast few rows:")
    print(df.tail())
    
    # Verify we have data from multiple dates
    print(f"\nUnique dates in dataset:")
    print(df.select('Date').unique().sort('Date'))
    
    # Save results
    processor.save_to_parquet("output/burst_data.parquet")
    processor.save_to_excel("output/burst_data.xlsx")
    
    # Get dataframe for further analysis
    result_df = processor.get_dataframe()
