import csv
import re
from pathlib import Path


def normalise_cell(cell):
    return re.sub(r'\s+', ' ', cell.strip())


def load_csv_data(folder):  # pragma: nocover
    """Return all Excel workbooks in `folder`.

    This returns a dictionary mapping the basenames of the Excel files to
    their data.

    Note: This assumes that every workbook consists of exactly one work sheet
    and that the first row of this sheet contains the column names.
    """
    data = {}
    for filename in Path(folder).glob('*.csv'):
        with open(filename, encoding='utf-8') as f:
            rdr = csv.reader(f)
            try:
                header = next(rdr)
            except StopIteration:
                continue
            table = [
                {k: norm_v
                 for k, v in zip(header, row)
                 if (norm_v := normalise_cell(v))}
                for row in rdr]
        table_name = filename.stem
        data[table_name] = table
    return data
