# spmtool

Read/write Kelly SPM brushed motor controller
configuration over serial connection. Tested with:

   - SPM24121


## Usage

Test serial connection:

	$ spmtool

Show help:

	$ spmtool -h
	usage: spmtool [-h] [-r | -w | -c] [-v] [-d DEVICE] [-s SETTINGS] [file]
	
	positional arguments:
	  file           config file
	
	options:
	  -h, --help     show this help message and exit
	  -r, --read     read controller memory to file
	  -w, --write    write config to controller
	  -c, --check    check and compare controller config
	  -v, --verbose  show debug log
	  -d DEVICE      serial port device
	  -s SETTINGS    settings schema preset or file


### Read Memory

Connect to controller, read memory, optionally mask settings
and then save to nominated file.

Read controller settings into conf.bin using SPM24121 preset:

	$ spmtool -r -s SPM24121 conf.bin


### Write Memory

Load config from nominated file, connect to controller,
update any settings listed in settings schema
on controller and save. A settings schema file or preset is
mandatory in this mode, see "Settings Schema" below for details.

Write settings from conf.bin to controller using SPM24121 preset:

	$ spmtool -w -s SPM24121 conf.bin


### Check Memory

Load config file, connect to controller and then list any differences
between config and controller memory. Optionally mask config and
memory with a settings schema.

Compare controller memory with contents of conf.bin using SPM24121 preset:

	$ spmtool -c -s SPM24121 conf.bin


## Settings Schema

Controller settings are listed in the settings schema
one per line with the whitespace delimited
columns:

	offset mask description

Where offset is a hexadecimal byte offset in the memory,
mask limits the bits that are set/cleared and description
is a text description for the setting. See included file
SPM24121.txt for an example.

To use a defined preset, use preset name as the schema, eg:

	$ spmtool -s SPM24121


## Installation

Install with pip, or run script file directly:

	$ python3 spmtool.py
