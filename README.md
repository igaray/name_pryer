## Name Pryer

**pry** *transitive verb*

1. to raise, move, or pull apart with a lever: prize
2. to extract, detach, or open with difficulty <pried the secret out of my sister>

**pry** *noun*

1. a tool for prying
2. leverage

### Overview

**name-pryer** is a simple command-line script for manipulating file names, a file name swiss army knife. It operates on single files or groups of files by populating a buffer with a listing of files, parsing the arguments to generate a sequence of actions, processing the actions in order and applying their effects to the contents of the file name buffer. The final state for each file name is shown and confirmation is requested before renaming the files.

**Feature Overview**:
* `-h` will emit a helpful text with available flags
* `-v` allows setting the verbosity level
* `-y` yes mode will skip confirmation
* `-u` will create an undo script
* `-F FILENAME` will operate on a single file
* `-D DIR` will set the working directory
* `-R` will recurse directories
* `-M [f | d | b]` allows operating only on files, directories or both
* `-g GLOB` allows specifying a glob pattern to match files
* `-p` allows specifying a pattern with fields, extracting those fields into the new filename, and generating values such as counters, random numbers, and dates
* `-c [lc | uc | tc | sc]` allows changing to upper, lower, sentence or title case
* `-C` allows splitting words in camel case
* `+C` allows joining words separated by underscores into camel case
* `-d X (Y | end)` allows deleting a region
* `-i X (Y | end)` allows inserting
* `-n` will sanitize the filename, removing all non-alphanumeric characters
* `+e EXT` allows adding an extension
* `-e [EXT]` allows modifying the extension or removing it if not specified
* `-r X Y` allows replacing characters
* `-s` is a shortform for substituting spaces, periods, dashes and underscores
* `-t` will tokenize the filename and allow selecting which tokens remaing and in which order

### License and Credits

**name-pryer** is an anagram of [pyRenamer](https://github.com/SteveRyherd/pyRenamer) by Adolfo González Blázquez, from which it inherits much.
Other work similar to this:
* [kevbradwick/pyrenamer](https://github.com/kevbradwick/pyrenamer)
* [italomaia/renamer](https://github.com/italomaia/renamer)
* [Donearm/Renamer](https://github.com/Donearm/Renamer)

The original **pyRenamer** has a GPL 2 license, and since I used its code for the pattern match operator, this is what **name-pryer** has.

### Requirements

**name-pryer** requires Python 3 and has no other dependencies. It has been tested only on Linux.

### Installation

**name-pryer** is a stand-alone script. Just download the ``name-pryer.py`` file, set it as executable, put it in your ``$PATH`` and alias to your finger's content.

### Flags without effects on file names

``-h``

Help. Print a message with a summary of the options.

---
``-v 0 -v 1 -v 2 -v 3``

Verbosity level.

* Level 0 is silent running and will produce no output.
* Level 1 will show the final state of the file name buffer and is the default.
* Level 2 will in addition list the actions to be applied.
* Level 3 will in addition show the state of the file name buffer at each step.

The ``-v X`` flags count as actions, but do not affect the file name buffer. They can be listed several times with different levels, interspersed among the other actions to raise or lower the verbosity during operation.

If the ``-v 2`` or ``-v 3`` parameter is present, regardless of position, a list of actions will be output at the beginning.

---
``-y``

Yes mode. Do not ask for confirmation. Useful for non-interactive batch scripts.

* Example:

```bash
$ np -v 0 -y -s us
```

---
``-u``

Creates a script `undo.sh` which may be run to undo the last renaming operations.

### Filters

Filters will specify which files remain in the buffer in addition to applying transformations on the file names therein. They affect how the file name buffer is populated, before any actions are applied.

---
``-F FILE``

Operate on a single file instead of all files in the current directory. Essentially drops all file names from the buffer that do not match its value exactly.

* Example

```bash
$ ls
folder  eighth_ninth_tenth.txt  fifth_sixth_seventh.txt  first_second_third_fourth.txt

$ np -F eighth_ninth_tenth.txt -s us
eighth_ninth_tenth.txt => eighth ninth tenth.txt

y/n?
```

---
``-M [f | d | b]``

Operation mode.

* Options:
  * **f**: Operate only on files (default).
  * **d**: Operate only on directories.
  * **b**: Operate both on directories and files.

* Example

```bash
$ ls -l
total 4
drwxr-xr-x 3 igaray igaray 4096 Dec 28 05:26 folder
-rw-r--r-- 1 igaray igaray    0 Dec 28 04:22 eighth_ninth_tenth
-rw-r--r-- 1 igaray igaray    0 Dec 28 04:21 fifth_sixth_seventh
-rw-r--r-- 1 igaray igaray    0 Dec 27 21:04 first_second_third_fourth

$ np -M f +e txt
eighth_ninth_tenth        => eighth_ninth_tenth.txt
fifth_sixth_seventh       => fifth_sixth_seventh.txt
first_second_third_fourth => first_second_third_fourth.txt

$ np -M d +e txt
folder => folder.txt

$ np -M b +e txt
eighth_ninth_tenth        => eighth_ninth_tenth.txt
fifth_sixth_seventh       => fifth_sixth_seventh.txt
first_second_third_fourth => first_second_third_fourth.txt
folder                    => folder.txt
```

---
``-D DIR``

Set working directory. Default is current directory.

---
``-R``

Recurse directories, may be used in combination with `-m` and `-D` and `-g`.

---
``-g GLOB``

Operate only on files matching the glob pattern, e.g. `-g "*.mp3"`.

* Examples

```bash
$ tree
.
├── eighth_ninth_tenth.txt
├── fifth_sixth_seventh.txt
├── first_second_third_fourth.txt
└── folder
    ├── eighth_ninth_tenth.txt
    └── folder2
        └── fifth_sixth_seventh2.txt

2 directories, 5 files

# Add extension 666, only to files in the current directory.
$ np +e 666
eighth_ninth_tenth.txt        => eighth_ninth_tenth.666
fifth_sixth_seventh.txt       => fifth_sixth_seventh.666
first_second_third_fourth.txt => first_second_third_fourth.666

# Add extension 666, only to files in the current directory starting with f.
$ np -g "f*" +e 666
fifth_sixth_seventh.txt       => fifth_sixth_seventh.666
first_second_third_fourth.txt => first_second_third_fourth.666

# Add extension 666 recursively, defaults to only files.
$ np -R +e 666
/home/igaray/tmp/test/eighth_ninth_tenth.txt
    => /home/igaray/tmp/test/eighth_ninth_tenth.666
/home/igaray/tmp/test/fifth_sixth_seventh.txt
    => /home/igaray/tmp/test/fifth_sixth_seventh.666
/home/igaray/tmp/test/first_second_third_fourth.txt
    => /home/igaray/tmp/test/first_second_third_fourth.666
/home/igaray/tmp/test/folder/eighth_ninth_tenth.txt
    => /home/igaray/tmp/test/folder/eighth_ninth_tenth.666
/home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.txt
    => /home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.666

# Add extension 666 recursively, only to files starting with the letter f.
$ np -R -g "f*" +e 666
/home/igaray/tmp/test/fifth_sixth_seventh.txt
    => /home/igaray/tmp/test/fifth_sixth_seventh.666
/home/igaray/tmp/test/first_second_third_fourth.txt
    => /home/igaray/tmp/test/first_second_third_fourth.666
/home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.txt
    => /home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.666

# Add extension 666 recursively, only to directories starting with f.
$ np -M d -R -g "f*" +e 666
/home/igaray/tmp/test/folder         => /home/igaray/tmp/test/folder.666
/home/igaray/tmp/test/folder/folder2 => /home/igaray/tmp/test/folder/folder2.666

# Add extension 666 recursively, to both files and directories starting with f.
$ np -M b -R -g "f*" +e 666
/home/igaray/tmp/test/fifth_sixth_seventh.txt
    => /home/igaray/tmp/test/fifth_sixth_seventh.666
/home/igaray/tmp/test/first_second_third_fourth.txt
    => /home/igaray/tmp/test/first_second_third_fourth.666
/home/igaray/tmp/test/folder
    => /home/igaray/tmp/test/folder.666
/home/igaray/tmp/test/folder/folder2
    => /home/igaray/tmp/test/folder/folder2.666
/home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.txt
    => /home/igaray/tmp/test/folder/folder2/fifth_sixth_seventh2.666
```

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
``{date}``      | Generates the date (e.g. 2014-12-31)
``{year}``      | Generates the year (e.g. 2014)
``{month}``     | Generates the month number (e.g. 12)
``{monthname}`` | Generates the month’s name (December)
``{monthsimp}`` | Generates the months abbreviated name (e.g. Dec)
``{day}``       | Generates the day’s number (31)
``{dayname}``   | Generates the day’s name (e.g. Wednesday)
``{daysimp}``   | Generates the day’s abbreviated name (e.g. Wed)

* Examples

TODO

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

### Transformations

Transformations visit every file name in the buffer and transform them in some way. None of the transformations will affect the extension or the period just before the extension.

---
``-C``

Split words in camelCase.

* Example

```bash
% ls -1
folder
EighthNinthTenth.txt
FifthSixthSeventh.txt
FirstSecondThirdFourth.txt

$ np -C
EighthNinthTenth.txt       => Eighth Ninth Tenth.txt
FifthSixthSeventh.txt      => Fifth Sixth Seventh.txt
FirstSecondThirdFourth.txt => First Second Third Fourth.txt

y/n?

% ls -1
folder
Eighth Ninth Tenth.txt
Fifth Sixth Seventh.txt
First Second Third Fourth.txt
```

---
``+C``

Join words separated by underscores into camelCase.

* Example

```bash
% ls -1
folder
eighth_ninth_tenth.txt
fifth_sixth_seventh.txt
first_second_third_fourth.txt

$ np +C
eighth_ninth_tenth.txt        => EighthNinthTenth.txt
fifth_sixth_seventh.txt       => FifthSixthSeventh.txt
first_second_third_fourth.txt => FirstSecondThirdFourth.txt

y/n?

% ls -1
folder
EighthNinthTenth.txt
FifthSixthSeventh.txt
FirstSecondThirdFourth.txt
```

---
``-c [lc | uc | tc | sc]``

Change case.
If you wish to capitalize the extension, use the ``-e`` flag.

* Options
  * **lc**: lowercase
  * **uc**: uppercase
  * **tc**: title case
  * **sc**: sentence case

* Examples

```bash
$ ls
folder  eighth_ninth_tenth  fifth_sixth_seventh  first_second_third_fourth

$ np -c uc
eighth_ninth_tenth        => EIGHTH_NINTH_TENTH
fifth_sixth_seventh       => FIFTH_SIXTH_SEVENTH
first_second_third_fourth => FIRST_SECOND_THIRD_FOURTH

$ np -c tc
eighth_ninth_tenth        => Eighth_Ninth_Tenth
fifth_sixth_seventh       => Fifth_Sixth_Seventh
first_second_third_fourth => First_Second_Third_Fourth

$ np -c sc
eighth_ninth_tenth        => Eighth_ninth_tenth
fifth_sixth_seventh       => Fifth_sixth_seventh
first_second_third_fourth => First_second_third_fourth
```

---
``-d X [Y | end]``

Delete from position X to Y [or end].
The end is just before the last period.

* X must be a non-negative integer.
* Y must be a either the string 'end' or a non-negative integer.

* Examples

```bash
$ ls
folder  eighth_ninth_tenth  fifth_sixth_seventh  first_second_third_fourth

$ np -d 0 4
eighth_ninth_tenth        => h_ninth_tenth
fifth_sixth_seventh       => _sixth_seventh
first_second_third_fourth => _second_third_fourth

$ np -d 4 end
eighth_ninth_tenth        => eigh
fifth_sixth_seventh       => fift
first_second_third_fourth => firs
```

---
``-i X [Y | end]``

Insert X at position Y [or end].
The end is just before the last period.

* X must be a string
* Y must be either the string 'end' or a non-negative integer

* Examples

```bash
$ ls
folder  eighth_ninth_tenth  fifth_sixth_seventh  first_second_third_fourth

$ np -i xxx_ 0
eighth_ninth_tenth        => xxx_eighth_ninth_tenth
fifth_sixth_seventh       => xxx_fifth_sixth_seventh
first_second_third_fourth => xxx_first_second_third_fourth

$ np -i xxx_ 6
eighth_ninth_tenth        => eighthxxx__ninth_tenth
fifth_sixth_seventh       => fifth_xxx_sixth_seventh
first_second_third_fourth => first_xxx_second_third_fourth

$ np -i _xxx end
eighth_ninth_tenth        => eighth_ninth_tenth_xxx
fifth_sixth_seventh       => fifth_sixth_seventh_xxx
first_second_third_fourth => first_second_third_fourth_xxx
```

---
``[+|-]e [EXT]``

Modifies the extension.
* ``+e EXT`` adds the extension to the file name.
* ``-e`` removes the existing extension from the file name.
* ``-e EXT`` changes the existing extension to ``EXT``.

* Examples

TODO

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

* Examples

TODO

---
``-n``

Sanitizes filenames by removing anything that is not an alphanumeric field.

* Examples

TODO

---
``-t [1 | 2 | 3]``

Interactive tokenization mode. Tokenizes the file name and prints out each token with a reference character underneath it. It then waits for the user to input a pattern indicating how the tokens should be rearranged.

If mode is 1, then the input pattern is expected to be simple a space-separated list of token indicators.

If mode is 2, then the input pattern is expected to be a match expression similar to the ones used with the ``-p`` flag. The input string will be the new filename, after having all occurrences of ``{X}`` patterns replaced, where ``X`` is a token reference.

If mode is 3, it behaves exactly the same as mode 2 except that the token references do not need to be surrounded by braces, but anything matching a token reference will be replaced by the referenced token.

* Examples

TODO
