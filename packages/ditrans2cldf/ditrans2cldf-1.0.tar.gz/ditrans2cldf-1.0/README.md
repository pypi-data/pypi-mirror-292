ditrans2cldf
============

Python package for processing Filemaker databases following the structure of
Malchukov & Haspelmath's *Ditranstive constructions* data base.

This package reads the Excel export from the Filemaker database and converts it
into the [CLDF][cldf] format.

[cldf]: https://cldf.clld.org

## Set up

Ditrans2cldf can be installed using pip:

    $ pip install ditrans2cldf

## Basic usage

*pydictionaria* is built on top of [cldfbench][cldfbench].  You can set up a
*ditrans2cldf* project using the provided cldfbench template.

    $ cldfbench new --template=ditransitive_db

[cldfbench]: https://github.com/cldf/cldfbench

The conversion process involves exporting the views in the Filemaker database as
Excel files and putting them into the `raw/` folder of the cldfbench.  See
[`doc/export-tutorial.pdf`](doc/export-tutorial.pdf) for a list of table columns
that you need to export.  The exported Excel files need then to be converted to
CSV (unfortunately Filemaker's builtin CSV/TSV exports lack column headers,
otherwise we would have used those directly).  After that you can run `makecldf`
to generate the CLDF data.

    $ # convert excel to csv
    $ cldfbench download cldfbench_*.py
    $ # generate cldf data
    $ cldfbench makecldf cldfbench_*.py

*ditrans2cldf* supports a configuration file in the `etc/` folder of the
cldfbench, which gives more control over which Filemaker columns map to which
CLDF columns.  For all supported options refer to
[`doc/configuration-file.md`](doc/configuration-file.md).
