## Name Pryer

**pry** *transitive verb*

1. to raise, move, or pull apart with a lever :  prize
2. to extract, detach, or open with difficulty <pried the secret out of my sister>

**pry** *noun*

1. a tool for prying
2. leverage

### Overview

**name-pryer** is a simple command-line script for manipulating
file names, a file name swiss army knife.
It operates on single files or groups of files.
It's name (and code) is an anagram of
[pyRenamer](https://github.com/SteveRyherd/pyRenamer)
by Adolfo González Blázquez, from which it inherits much.

Other work similar to this:
* [kevbradwick/pyrenamer](https://github.com/kevbradwick/pyrenamer)
* [italomaia/renamer](https://github.com/italomaia/renamer)
* [Donearm/Renamer](https://github.com/Donearm/Renamer)

**name-pryer** operates by populating a buffer with a listing of
files in the current directory, parsing the arguments to generate actions,
processing the actions in order passed and applying their effects to the
contents of the file name buffer until the final form is obtained.
This final form for each file name is shown and confirmation is
requested before renaming the files.

### License

The original **pyRenamer** has a GPL 2 license, so this is what **name-pryer**
has.

### Requirements

**name-pryer** requires Python 3 and has no other dependencies.

### Installation

**name-pryer** is a stand-alone script.
Just download the ``name-pryer.py`` file, set it as executable, put it in your
``$PATH`` and alias to your finger's content.

### Flags without effects on file names

``-h``

Help. Print a message with a summary of the options.

---
``-y``

Yes mode. Do not ask for confirmation.
Useful for non-interactive batch scripts.

---
``-v0 -v1 -v2 -v3``

Verbosity level.

* Level 0 is silent running and will produce no output.
* Level 1 will show the final state of the file name buffer and is the default.
* Level 2 will in addition list the actions to be applied.
* Level 3 will in addition show the state of the file name buffer at each step.

The ``-vX`` flags count as actions, but do not affect the file name buffer.
They can be listed several times with different levels, interspersed among the
other actions to raise or lower the verbosity during operation.

If the ``-v2`` or ``-v3`` parameter is present, regardless of position, a list
of actions will be output at the beginning.

### Filters

Filters will specify which files remain in the buffer in addition to
applying transformations on the file names therein.

---
``-f FILE``

Operate on a single file instead of all files in the current directory.
Essentially drops all file names from the buffer that do not match its
value, so be sure to specify this at the beginning, or it will be
difficult to have it match something.

---
``-p SOURCE_PATTERN DESTINATION_PATTERN``

The pattern matching filter makes regular expressions usable.
This is the most useful operator and is taken directly from **pyRenamer**'s code.

**Pattern**     | **Description**
----------------|----------------
``{#}``         | Numbers
``{L}``         | Letters
``{C}``         | Characters (Numbers & letters, not spaces)
``{X}``         | Numbers, letters, and spaces
``{@}``         | Trash
``{numX+Y}``    | Generates a number, padded to **X** characters with leading 0s, stepping by **Y**. **X** may be absent. **Y** may be absent and defaults to 1.
``{rand}``      | Generates a random number from 0 to 100.
``{randX}``     | Generates a random number from 0 to **X**.
``{randX-Y}``   | Generates a random number from **X** to **Y**.
``{randX-Y,Z}`` | Generates a random number from **X** to **Y**, padded to **Z**. characters.
``{date}``      |
``{year}``      |
``{month}``     |
``{monthname}`` |
``{monthsimp}`` |
``{day}``       |
``{dayname}``   |
``{daysimp}``   |

### Transformations

Transformations visit every file name in the buffer and transform them in some way.
None of the transformations will affect the extension or the period just before
the extension.

---
``-C``

Split words in camelCase.

---
``-c [lc | uc | tc | sc]``

Change case.
If you wish to capitalize the extension, use the ``-e`` flag.

* Options
  * **lc**: lowercase
  * **uc**: uppercase
  * **tc**: title case
  * **sc**: sentence case

---
``-d X [Y | end]``

Delete from position X to Y [or end].
The end is just before the last period.

* X must be a non-negative integer.
* Y must be a either the string 'end' or a non-negative integer.

---
``[+|-]e [EXT]``

Modifies the extension.
* ``+e EXT`` adds the extension to the file name.
* ``-e`` removes the existing extension from the file name.
* ``-e EXT`` changes the existing extension to ``EXT``.

---
``-i X [Y | end]``

Insert X at position Y [or end].
The end is just before the last period.

* X must be a string
* Y must be either the string 'end' or a non-negative integer

---
``-n``

Sanitizes filenames by removing anything that is not an alphanumeric field.

---
``-t [1 | 2 | 3]``

Interactive tokenization mode. Tokenizes the file name and prints out
each token with a reference character underneath it.
It then waits for the user to input a pattern indicating how the tokens
should be rearranged.

If mode is 1, then the input pattern is expected to be simple a
space-separated list of token indicators.

If mode is 2, then the input pattern is expected to be a match expression
similar to the ones used with the ``-p`` flag. The input string will be the
new filename, after having all occurrences of ``{X}`` patterns replaced,
where ``X`` is a token reference.

If mode is 3, it behaves exactly the same as mode 2 except that the token
references do not need to be surrounded by braces, but anything matching
a token reference will be replaced by the referenced token.

---
``-r X Y``

Replace X with Y.

---
``-s [sd | sp | su | ud | up | us | pd | ps | pu | dp | ds | du ]``

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

### Examples

<!--
python3 name-pryer.py
-s us -s sp -s pd -s du -s ud -s ds -s su -s up -s ps -s sd -s dp -s pu -r e x -c lc -c uc -c tc -c sc
-i _ins_ 0 -i _ins_ 3 -i _ins_ end
-d X 0
-d X end
-d X Y
-->

---
```bash
% pwd
/Users/inaki/Music/Thriftworks - Deviation (2013)/Thriftworks - Deviation (2013)

% ls -1
01 - Untrue.mp3
02 - Fits the Bill.mp3
03 - Feeding Time.mp3
04 - Someone (feat. Oriel Poole).mp3
05 - The Touch.mp3
06 - Metal Tho.mp3
07 - Terminally Chill.mp3
08 - Nanometer.mp3

% name-pryer.py -v 3 -p "{#} - {X}" "{1} {2}"
actions:
verbosity 3
pattern   {#} - {X} {1} {2}

setting verbosity level to 3
----------------------------------------------------------------------
pattern {#} - {X} {1} {2}
01 - Untrue.mp3                      => 01 Untrue.mp3
02 - Fits the Bill.mp3               => 02 Fits the Bill.mp3
03 - Feeding Time.mp3                => 03 Feeding Time.mp3
04 - Someone (feat. Oriel Poole).mp3 => 04 Someone (feat. Oriel Poole).mp3
05 - The Touch.mp3                   => 05 The Touch.mp3
06 - Metal Tho.mp3                   => 06 Metal Tho.mp3
07 - Terminally Chill.mp3            => 07 Terminally Chill.mp3
08 - Nanometer.mp3                   => 08 Nanometer.mp3

y/n?
y

% ls -1
01 Untrue.mp3
02 Fits the Bill.mp3
03 Feeding Time.mp3
04 Someone (feat. Oriel Poole).mp3
05 The Touch.mp3
06 Metal Tho.mp3
07 Terminally Chill.mp3
08 Nanometer.mp3
```

### TODO

---
Add flag to specify creation of an undo script, which when run will undo changes.

``-u``

---
* Add flag to specify operation only on files (default), only on dirs, or both.

``-m [f | d | b]``

Operation mode.

* Options:
  * **f**: Operate only on files (default).
  * **d**: Operate only on directories.
  * **b**: Operate both on directories and files.

---
* Add flag to specify working directory, default is current working directory.

``-D DIR``

Set working directory. Default is current directory.

---
* Add flag to specify recursive operation.

``-R``

Recursive operation.

---
* Add flag to specify a filter by glob pattern , e.g. ``-g "*.mp3"``

``-g GLOB``

Operate only on files matching the glob pattern.

---
* Add a vim-like macro recording and playback system.

---
* Make PEP8 conforming.
* Make pip friendly.
* Add some examples in motion.