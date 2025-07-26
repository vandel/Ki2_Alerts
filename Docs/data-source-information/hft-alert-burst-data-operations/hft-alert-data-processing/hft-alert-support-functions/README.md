# HFT Alert Support Functions

`extract_date_from_filename_datetime`, is designed to extract a date from a filename that contains a date in the format `YYYYMMDD` (YearMonthDay).

Here's a step-by-step breakdown of what the function does:

1. The function takes one argument, `filename`, which is expected to be a string.
2. It uses the `re.search` function from the `re` module (Python's built-in regular expression module) to search for a sequence of 8 digits (`\d{8}`) in the `filename`. This sequence is assumed to represent a date in the `YYYYMMDD` format.
3. The `re.search` function returns a match object if it finds a match, or `None` if it doesn't. The `group(0)` method is called on the match object to get the actual matched string.
4. The matched string (which should be a date in the `YYYYMMDD` format) is then passed to the `datetime.strptime` function, which converts it into a `datetime` object. The second argument to `datetime.strptime` is a format string that specifies the expected format of the date string (`'%Y%m%d'`).
5. The function then returns this `datetime` object.

In summary, this function extracts a date in the `YYYYMMDD` format from a filename and returns it as a `datetime` object.
