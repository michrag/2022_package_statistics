# Package Statistics (Generator)
*Package Statistics (Generator)* is a Python command line tool that takes the architecture (amd64, arm64, mips, etc.) as an argument, and downloads the compressed Contents file associated with it from a Debian mirror.
The program parses the file and output the statistics of the top 10 packages that have the most files associated with them.


## Usage (and Requirements)
*Package Statistics (Generator)* requires Python 3.7 or newer.

If you prefer, create a virtual environment like:

> `python3 -m venv venv`

and activate it with:

> `source venv/bin/activate`

Then install the required packages (actually, just `tqdm`) with:

> `python -m pip install -r requirements.txt`

Now you can run the script with:

> `python package_statistics.py`

and follow the instruction on how to actually use it (i.e., just pass it an architecture name).

When finished you can deactivate the virtual environment simply with:

> `deactivate`

Note: since every time it is run, it downloads the required Contents Index file, it also removes it before exiting. You can easily disable this behaviour by just modifying the source code. 
