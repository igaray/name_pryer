## Name Pryer 

### Overview

**name-pryer** is a simple script for manipulating file names, 
a file name swiss army knife.
It operates on single files or groups of files.
It's name (and code) is an anagram of 
[pyRenamer](https://github.com/SteveRyherd/pyRenamer)
by Adolfo González Blázquez, from which it inherits much.

Other work similar to this: 
* [kevbradwick/pyrenamer](https://github.com/kevbradwick/pyrenamer)
* [italomaia/renamer](https://github.com/italomaia/renamer)
* [Donearm/Renamer](https://github.com/Donearm/Renamer)

**name-pryer** operates by populating a buffer with a listing of 
files in the current directory, and successively applying filters 
and transformations on the names until the final form is obtained. 
This final form for each file name is shown and confirmation is 
requested before renaming the files.

### Flags

``-h``

Help. Print a message with a summary of the options.

---
``-y``

Yes mode. Do not ask for confirmation.
Useful for non-interactive batch scripts.

---
``-v``

Verbose mode. Will list the filters and its arguments in the order to be applied.

``-vv``

Two levels of verbosity will print the file name buffer at each step after a 
transformation is applied.

### Filters

Filters will specify which files remain in the buffer in addition to 
applying transformations on the file names therein. 

---
``-f FILE``

Operate on a single file instead of all files in the current directory.
Essentially drops all file names from the buffer that to not match its
value, so be sure to specify this at the beginning, or it will be 
difficult to have it match something.

---
``-p SOURCE_PATTERN DESTINATION_PATTERN``

### Transformations

``-s [sd, sp | su | ud | up | us | pd | ps | pu | dp | ds | du ]``

Convert one character to another.

* Options:
  * **sd**: spaces to dashes
  * **sp**: spaces to periods
  * **su**: spaces to underscores
  * **ud**: underscores to dashes
  * **up**: underscores to periods
  * **us**: underscores to spaces
  * **pd**: periods to dashes
  * **ps**: periods to space
  * **pu**: periods to underscores
  * **dp**: dashes to periods
  * **ds**: dashes to spaces
  * **du**: dashes to underscores

---
``-r X Y``

Replace X with Y.

---
``-c [lc | uc | tc | sc]``

Change case.

* Options
  * **lc**: lowercase
  * **uc**: uppercase
  * **tc**: title case
  * **sc**: sentence case

---
``-i X [Y | end]``

Insert X at position Y [or end]
X must be a string
Y must be either the string 'end' or an integer

---
``-d X [Y | end]``

Delete from position X to Y [or end]

### Examples

---
