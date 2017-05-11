#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File-Pryer: File Name Swiss Army Knife

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import re
import sys
import time
import glob
import tty
import termios
import functools
import subprocess

###############################################################################
# GLOBALS

SHORT_USAGE = """
Usage:
    -h
    -v [0 | 1 | 2 | 3]
    --git
    -y
    -u
    -F FILENAME
    -D DIR
    -R
    -M [f | d | b]
    -g GLOB
    -p SOURCE_PATTERN DESTINATION_PATTERN
        {#}                      {numX+Y}                         {monthname}
        {L}                      {randX-Y,Z}                      {monthsimp}
        {C}                      {date}                           {day}
        {X}                      {year}                           {dayname}
        {@}                      {month}                          {daysimp}
    -c [lc | uc | tc | sc]
    -C
    +C
    -d X (Y | end)
    +e EXT
    -e [EXT]
    -i X (Y | end)
    -n
    -r X Y
    -s [sd | sp | su | ud | up | us | pd | ps | pu | dp | ds | du ]
        s: spaces         d: dashes         u: underscores         p: periods
    -t [1 | 2 | 3]
"""

LONG_USAGE = """
Usage:
    -h
        Help, print this message
    -v X
        Verbosity level. X may be one of 0, 1, 2 or 3
        lvl 0: silent running, no output
        lvl 1: default, show original filenames and after final transformation
        lvl 2: show lvl 1 output and actions to be applied
        lvl 3: show lvl 2 output and state of file name buffer after each step
        Counts as an action, so several may be present between other actions
        to raise or lower the verbosity during operation.
    --git
        Make filename modifications by calling git instead of directly.
    -y
        Yes mode, do not prompt for confirmation.
    -u
        Creates an undo script.
    -F FILENAME
        Run on file FILENAME
    -D DIR
        Specify the working directory.
    -R
        Recurse directories.
    -M [f | d | b]
        f: operate only on files (default)
        d: operate only on directories
        b: operate both on directories and files
    -g GLOB
        Filter files using a glob expression.
    -p SOURCE_PATTERN DESTINATION_PATTERN
        Pattern match.
        {#}         Numbers
        {L}         Letters
        {C}         Characters (Numbers & letters, not spaces)
        {X}         Numbers, letters, and spaces
        {@}         Trash
        {numX+Y}    Number, padded to X characters with leading 0s, step by Y
        {randX-Y,Z} Random number between X and Y padded to Z characters
        {date}      Date (2014-12-31)
        {year}      Year (2014)
        {month}     Month number (12)
        {monthname} Month name (December)
        {monthsimp} Month simple name (Dec)
        {day}       Day number (31)
        {dayname}   Day name (Wednesday)
        {daysimp}   Day simple name (Wed)
    -c [lc | uc | tc | sc]
        Change case:
            lc: lowercase
            uc: uppercase
            tc: title case
            sc: sentence case
    -C
        Split camelCase words.
    +C
        Join underscore words into camelCase.
    -d X (Y | end)
        Delete from position X to Y [or end]
    +e EXT
        Add extension.
    -e [EXT]
        Modify or remove extension.
    -i X (Y | end)
        Insert X at position Y [or end]
        X must be a string
        Y must be either the string "end" or an integer
    -n
       Sanitize the filename by removing anything that is not alfanumeric.
    -r X Y
        Replace X with Y.
    -s [sd | sp | su | ud | up | us | pd | ps | pu | dp | ds | du ]
        Substitute characters, X for Y, where X and Y may be one of:
            s: spaces
            d: dashes
            u: underscores
            p: periods
    -t [1 | 2 | 3]
        Tokenize and select tokens for filename pattern.
        1: input pattern is a space-separated list of token refs
        2: input pattern is a match expression
        3: same as 2 except token refs do not need to be surrounded by braces
"""

ERRMSGS = {
    "file-arity"      : "-f takes a filename parameter",
    "case-arity"      : "-c takes one parameter",
    "case-type"       : "valid parameters for -c: lc uc tc sc",
    "extension-arity" : "+e requires one parameter",
    "delete-arity"    : "-d requires two parameters",
    "delete-type-1"   : "1st parameter to -d must be an integer",
    "delete-type-2"   : "2nd parameter to -d must be either 'end' or integer",
    "delete-type-3"   : "integer parameters to -d must be non negative",
    "delete-index-1"  : "1st parameter to -d is out of range",
    "delete-index-2"  : "2nd parameter to -d is out of range",
    "delete-index-3"  : "1st parameter to -d is greater than second argument",
    "insert-arity"    : "-i requires two parameters",
    "insert-type-1"   : "2nd parameter to -i must be either 'end' or an integer",
    "insert-type-2"   : "integer parameters to -i must be non-negative",
    "indert-index"    : "2nd parameter to -i is out of range",
    "pattern-arity"   : "-p requires two parameters",
    "replace-arity"   : "-r requires two parameters",
    "subs-arity"      : "-s requires a parameter",
    "subs-type"       : "valid parameters for -s: sd sp su ud up us pd ps pu dp ds du",
    "verbosity-arity" : "-vX requires a parameter",
    "verbosity-type"  : "valid parameters for -v: 0 1 2 3",
    "duplicate"       : "action will result in two or more identical file names!",
    "tokenize-arity"  : "-t requires one parameter",
    "too_many_tokens" : "a file has too many tokens",
    "filemode-arity"  : "-m requires one parameter",
    "directory-arity" : "-D requires one parameter",
    "glob-arity"      : "-g requires one parameter"
}

VALID_FLAGS = frozenset([
    "-c", "-C", "+C", "-d", "-D", "-e", "+e", "-F", "-g", "-h", "-i", "-M",
    "-n", "-p", "-r", "-R", "-s", "-u", "-v", "-y"
    ])
VALID_SUBTITUTION_OPTIONS = frozenset([
    "sd", "sp", "su", "ud", "up", "us", "pd", "ps", "pu", "dp", "ds", "du"
    ])
VALID_CASE_OPTIONS = frozenset(["lc", "uc", "tc", "sc"])

SPLIT_REGEX        = re.compile(r"[a-zA-Z0-9]+|[^a-zA-Z0-9]+")
FIRST_CAP_REGEX    = re.compile(r"(.)([A-Z][a-z]+)")
ALL_CAP_REGEX      = re.compile(r"([a-z0-9])([A-Z])")
ALPHANUMERIC_REGEX = re.compile(r"[a-zA-Z0-9]+")

ACTION_HANDLERS = {}
CASE_FUNS       = {}
SUBSTITUTE_FUNS = {}


###############################################################################
# CLASSES


class Config:

    def __init__(self):
        rows, cols = os.popen('stty size', 'r').read().split()
        self.rows  = int(rows)
        self.cols  = int(cols)
        # 0: silent running
        # 1: default, show file name buffer before confirmation
        # 2: verbose, show actions and file name buffer before confirmation
        # 3: very verbose, show file name buffer state after each action
        self.verbosity = 1
        self.file_mode = 'f'
        self.yes_mode  = False
        self.undo      = False
        self.recursive = False
        self.directory = os.getcwd()
        self.pattern   = None


class Action:
    def __init__(self, name, arg1=None, arg2=None):
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2


class File:
    def __init__(self, path, name, ext=""):
        self.path = path
        self.name = name
        self.ext  = ext

    def full(self):
        if self.ext:
            return self.name + "." + self.ext
        else:
            return self.name

    def fullpath(self):
        if self.ext:
            return os.path.join(self.path, self.name + "." + self.ext)
        else:
            return os.path.join(self.path, self.name)

    def set_name(self, name):
        self.name = name

    def set_ext(self, ext):
        self.ext = ext


###############################################################################
# FILE AND BUFFER HANDLING


def escape_pattern(pattern):
    """ Escape special chars on patterns, so glob doesn"t get confused """
    return pattern.replace("[", "[[]")


def get_file_listing(config):
    cwd    = config.directory
    result = []
    items  = []

    if config.recursive:
        if config.pattern:
            for root, subfolders, files in os.walk(cwd):
                items += glob.glob(os.path.join(root, config.pattern))
        else:
            for root, subfolders, files in os.walk(cwd):
                for item in subfolders:
                    items.append(os.path.join(root, item))
                for item in files:
                    items.append(os.path.join(root, item))
    else:
        if config.pattern:
            items = glob.glob(os.path.join(config.directory, config.pattern))
        else:
            items = os.listdir(config.directory)
        items = [os.path.join(config.directory, item) for item in items]

    items.sort(key=str.lower)
    if config.file_mode == 'f':
        # Get files
        for item in items:
            abspath = os.path.abspath(item)
            if not os.path.isdir(abspath):
                path, name = os.path.split(abspath)
                path += os.sep
                name, ext = os.path.splitext(name)
                result.append(File(path, name, ext[1:]))

    elif config.file_mode == 'd':
        # Get directories
        for item in items:
            abspath = os.path.abspath(item)
            if os.path.isdir(abspath):
                path, name = os.path.split(abspath)
                path += os.sep
                result.append(File(path, name, ""))

    elif config.file_mode == 'b':
        # Get both
        for item in items:
            abspath = os.path.abspath(item)
            path, name = os.path.split(abspath)
            path += os.sep
            if os.path.isdir(abspath):
                result.append(File(path, name, ""))
            else:
                name, ext = os.path.splitext(name)
                result.append(File(path, name, ext[1:]))

    return result


def init_fn_buffer(config):
    fn_buffer = {}
    files = get_file_listing(config)
    if config.recursive:
        for f in files:
            fn_buffer[f.fullpath()] = f
    else:
        for f in files:
            fn_buffer[f.full()] = f
    return fn_buffer


def rename_file(config, old, new):
    try:
        if old == new:
            return True
        if config.git_mode:
            subprocess.call(["git", "mv", old, new])
        else:
            os.renames(old, new)
        return True
    except Exception:
        print("error while renaming {} to {}".format(old, new))
        return False


def rename_files(config, fn_buffer):
    for k, v in fn_buffer.items():
        if (k != fn_buffer[k].full()) and os.path.exists(fn_buffer[k].full()):
            t = fn_buffer[k].name + fn_buffer[k].ext
            error_msg = "error while renaming {} to {}! -> {} already exists!"
            sys.exit(error_msg.format(k, t, t))
    for k, v in sorted(fn_buffer.items()):
        rename_file(config, v.path + k, v.path + v.full())


def output_undo_script(fn_buffer):
    f = open("undo.sh", "w")
    for k, v in fn_buffer.items():
        f.write('mv "{}" "{}"\n'.format(v.full(), k))
    f.close()


def verify_fn_buffer(fn_buffer):
    for k1, v1 in fn_buffer.items():
        for k2, v2 in fn_buffer.items():
            if (k1 != k2) and (v1.fullpath() == v2.fullpath()):
                print(ERRMSGS["duplicate"])
                print(v1.full())
                print(v2.full())
                sys.exit("")


def clean_fn_buffer(fn_buffer):
    new_fn_buffer = fn_buffer.copy()
    for k, v in fn_buffer.items():
        if (k == v.full()):
            del new_fn_buffer[k]
    return new_fn_buffer


###############################################################################
# LIST AND STRING MANGLING


def split(string):
    return SPLIT_REGEX.findall(string)


def split_camel_case(string):
    s = FIRST_CAP_REGEX.sub(r"\1 \2", string)
    return ALL_CAP_REGEX.sub(r"\1 \2", s)


def split_alphanumeric(string):
    return ALPHANUMERIC_REGEX.findall(string)


def join_camel_case(string):
    return "".join([CASE_FUNS["sc"](x) for x in string.split("_")])


###############################################################################
# PARSING


def parse_args(argv):
    config  = Config()
    actions = []
    l       = len(argv)
    i       = 1

    if l == 1:
        print(SHORT_USAGE)
        sys.exit()

    while (i < l):
        if argv[i] == "-c":
            msg = ERRMSGS["case-arity"]
            i, actions = parse_one(argv, i, actions, "case", msg)
            if not (actions[-1].arg1 in VALID_CASE_OPTIONS):
                msg = ERRMSGS["case-type"]
                sys.exit(msg)

        elif argv[i] in ["-C", "+C"]:
            actions.append(Action("camelcase", argv[i][0]))
            i += 1

        elif argv[i] == "-d":
            msg = ERRMSGS["delete-arity"]
            i, actions = parse_two(argv, i, actions, "delete", msg)
            s1 = actions[-1].arg1
            try:
                actions[-1].arg1 = int(s1)
            except ValueError:
                sys.exit(ERRMSGS["delete-type-1"])
            if actions[-1].arg1 < 0:
                sys.exit(ERRMSGS["delete-type-3"])
            s2 = actions[-1].arg2
            if s2 != "end":
                try:
                    actions[-1].arg2 = int(s2)
                except ValueError:
                    sys.exit(ERRMSGS["delete-type-2"])
                if actions[-1].arg2 < 0:
                    sys.exit(ERRMSGS["delete-type-3"])

        elif argv[i] == '-D':
            if i+1 < l:
                config.directory = argv[i+1]
            else:
                sys.exit(ERRMSGS["directory-arity"])
            i += 2

        elif argv[i] in ["-e", "+e"]:
            i, actions = parse_extension(argv, i, actions)

        elif argv[i] == "-F":
            msg = ERRMSGS["file-arity"]
            i, actions = parse_one(argv, i, actions, "file", msg)

        elif argv[i] == "-g":
            if i+1 < l:
                config.pattern = argv[i+1]
            else:
                sys.exit(ERRMSGS["glob-arity"])
            i += 2

        elif argv[i] == "-i":
            msg = ERRMSGS["insert-arity"]
            i, actions = parse_two(argv, i, actions, "insert", msg)
            s = actions[-1].arg2
            if s != "end":
                try:
                    actions[-1].arg2 = int(s)
                except ValueError:
                    sys.exit(ERRMSGS["insert-type-1"])
                if actions[-1].arg2 < 0:
                    sys.exit(ERRMSGS["insert-type-2"])

        elif argv[i] == "-M":
            if argv[i+1] in ['f', 'd', 'b']:
                config.file_mode = argv[i+1]
            else:
                sys.exit(ERRMSGS["filemode-arity"])
            i += 2

        elif argv[i] == "-n":
            actions.append(Action("sanitize"))
            i += 1

        elif argv[i] == "-p":
            msg = ERRMSGS["pattern-arity"]
            i, actions = parse_two(argv, i, actions, "pattern", msg)

        elif argv[i] == "-r":
            msg = ERRMSGS["replace-arity"]
            i, actions = parse_two(argv, i, actions, "replace", msg)

        elif argv[i] == "-R":
            config.recursive = True
            i += 1

        elif argv[i] == "-s":
            msg = ERRMSGS["subs-arity"]
            i, actions = parse_one(argv, i, actions, "substitute", msg)
            if not actions[-1].arg1 in VALID_SUBTITUTION_OPTIONS:
                msg = ERRMSGS["subs-type"]
                sys.exit(msg)

        elif argv[i] == "-t":
            msg = ERRMSGS['tokenize-arity']
            i, actions = parse_one(argv, i, actions, "tokenize", msg)

        elif argv[i] == "-u":
            config.undo = True
            i += 1

        elif argv[i] == "-v":
            msg = ERRMSGS["verbosity-arity"]
            i, actions = parse_one(argv, i, actions, "verbosity", msg)
            try:
                actions[-1].arg1 = int(actions[-1].arg1)
            except ValueError:
                sys.exit(ERRMSGS["verbosity-type"])
            if not actions[-1].arg1 in [0, 1, 2, 3]:
                sys.exit(ERRMSGS["verbosity-type"])

        elif argv[i] == "-h":
            print(LONG_USAGE)
            sys.exit()

        elif argv[i] == "-y":
            config.yes_mode = True
            i += 1

        elif argv[i] == "--git":
            config.git_mode = True
            i += 1

        else:
            print(SHORT_USAGE)
            msg = "unrecognized flag: {}".format(argv[i])
            sys.exit(msg)
    return config, actions


def parse_one(argv, i, actions, action_name, errmsg):
    if i + 1 < len(argv):
        actions.append(Action(action_name, argv[i+1]))
        i += 2
    else:
        sys.exit(errmsg)
    return i, actions


def parse_two(argv, i, actions, action_name, errmsg):
    if i + 2 < len(argv):
        actions.append(Action(action_name, argv[i+1], argv[i+2]))
        i += 3
    else:
        sys.exit(errmsg)
    return i, actions


def parse_extension(argv, i, actions):
    l = len(argv)
    mode = argv[i][0]  # will be either + or -
    if i == l - 1:
        # this flag is the last flag
        action = Action("extension", mode)
        i += 1
    elif i + 1 < l:
        # there is at least one more argument
        if argv[i+1] in VALID_FLAGS:
            # thane next argument is a new flag
            action = Action("extension", mode)
            i += 1
        else:
            # the next argument is the value of the extension flag
            action = Action("extension", mode, argv[i+1])
            i += 2
    if (mode == "+") and (action.arg2 is None):
        sys.exit(ERRMSGS["extension-arity"])
    actions.append(action)
    return i, actions


###############################################################################
# OUTPUT


def print_sep():
    print("-" * 70)


def print_action(action, maxlen_name=None, maxlen_arg1=None):
    arg1_str = str(action.arg1)
    if not maxlen_name:
        maxlen_name = len(action.name)
    if not maxlen_arg1:
        maxlen_arg1 = len(arg1_str)
    if action.arg2:
        arg2_str = str(action.arg2)
    else:
        arg2_str = ""
    print("{}{}{}{}{}".format(
        action.name,
        (" " * (maxlen_name - len(action.name) + 1)),
        arg1_str,
        (" " * (maxlen_arg1 - len(str(action.arg1)) + 1)),
        arg2_str
    ))


def print_actions(actions):
    maxlen_name = maxlen_arg1 = 0
    for a in actions:
        maxlen_name = max(maxlen_name, len(a.name))
        if a.arg1:
            maxlen_arg1 = max(maxlen_arg1, len(str(a.arg1)))

    print("actions:")
    for a in actions:
        print_action(a, maxlen_name, maxlen_arg1)
    print()


def print_fn_buffer(config, fn_buffer):
    maxlen = 0
    for k in fn_buffer.keys():
        maxlen = max(maxlen, len(k))

    if config.recursive:
        for k, v in sorted(fn_buffer.items()):
            s = "{}{}=> {}".format(k, (" " * (maxlen-len(k)+1)), v.fullpath())
            if len(s) > config.cols:
                s = "{}\n    => {}".format(k, v.fullpath())
            print(s)
    else:
        for k, v in sorted(fn_buffer.items()):
            s = "{}{}=> {}".format(k, (" " * (maxlen-len(k)+1)), v.full())
            if len(s) > config.cols:
                s = "{}\n    => {}".format(k, v.full())
            print(s)
    print()


###############################################################################
# ACTION HANDLERS


def handle_actions(config, actions):
    fn_buffer = init_fn_buffer(config)
    for action in actions:
        fn_buffer = ACTION_HANDLERS[action.name](config, action, fn_buffer)
        if (config.verbosity > 2) and (action.name != "verbosity"):
            print_sep()
            print_action(action)
            print_fn_buffer(config, fn_buffer)
        verify_fn_buffer(fn_buffer)
    return clean_fn_buffer(fn_buffer)


def handle_camel_case(config, action, fn_buffer):
    for k, v, in fn_buffer.items():
        fn_buffer[k].set_name(process_camel_case(v.name, action.arg1))
    return fn_buffer


def handle_case(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_case(action.arg1, v.name))
    return fn_buffer


def handle_file(config, action, fn_buffer):
    new_fn_buffer = fn_buffer.copy()
    for k in fn_buffer.keys():
        if (k != action.arg1):
            del new_fn_buffer[k]
    return new_fn_buffer


def handle_delete(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_delete(action.arg1, action.arg2, v.name))
    return fn_buffer


def handle_extension(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        name, ext = process_extension(action.arg1, action.arg2, v.name)
        fn_buffer[k].set_name(name)
        fn_buffer[k].set_ext(ext)
    return fn_buffer


def handle_insert(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_insert(fn_buffer[k].name, action.arg1, action.arg2)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_pattern_match(config, action, fn_buffer):
    count = 0
    new_fn_buffer = fn_buffer.copy()
    for k, v in fn_buffer.items():
        n = process_pattern_match(v.name, action.arg1, action.arg2, count)
        if n:
            new_fn_buffer[k].set_name(n)
        else:
            del new_fn_buffer[k]
        count += 1
    return new_fn_buffer


def handle_replace(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_replace(v.name, action.arg1, action.arg2)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_sanitize(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_sanitize(v.name))
    return fn_buffer


def handle_substitute(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_substitute(action.arg1, v.name)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_tokenize(config, action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_tokenize(action.arg1, v.name))
    return fn_buffer


def handle_verbosity(config, action, fn_buffer):
    process_verbosity(config, action.arg1)
    return fn_buffer


###############################################################################
# ACTION PROCESSORS


def process_camel_case(name, mode):
    if mode == '-':
        return split_camel_case(name)
    if mode == '+':
        return join_camel_case(name)


def process_case(mode, name):
    return CASE_FUNS[mode](name)


def process_delete(ini, end, name):
    if end == "end":
        end = len(name)
    elif end > len(name):
        sys.exit(ERRMSGS["delete-index-2"])

    if ini > len(name):
        sys.exit(ERRMSGS["delete-index-1"])
    elif ini > end:
        sys.exit(ERRMSGS["delete-index-3"])

    textini = name[0:ini]
    textend = name[end+1:len(name)]
    newname = textini + textend
    return newname


def process_extension(mode, ext, name):
    if mode == "+":
        pass
        # add an extension
        # if (ext and name):
        #    name += ('.' + ext)
    if mode == "-":
        if ext and name:
            # change the extension to ext
            if "." in name:
                aux  = name.split(".")[-1]
                name = name[0:len(name) - len(aux) - 1]
                name += ext
        else:
            # remove the extension
            if "." in name:
                ext  = name.split(".")[-1]
                name = name[0:len(name) - len(ext) - 1]
                ext  = ""
            else:
                ext = ""
    return name, ext


def process_insert(name, text, pos):
    if pos == "end":
        pos = len(name)
        newname = name + text
    elif (pos > len(name)):
        sys.exit(ERRMSGS["insert-index-1"])
    else:
        newname = name[0:pos] + text + name[pos:len(name)]
    return newname


def process_pattern_match(name, pattern_ini, pattern_end, count):
    pattern   = pattern_ini
    pattern   = pattern.replace(".", "\.")
    pattern   = pattern.replace("[", "\[")
    pattern   = pattern.replace("]", "\]")
    pattern   = pattern.replace("(", "\(")
    pattern   = pattern.replace(")", "\)")
    pattern   = pattern.replace("?", "\?")
    pattern   = pattern.replace("{#}", "([0-9]*)")
    pattern   = pattern.replace("{L}", "([a-zA-Z]*)")
    pattern   = pattern.replace("{C}", "([\S]*)")
    pattern   = pattern.replace("{X}", "([\S\s]*)")
    pattern   = pattern.replace("{@}", "(.*)")
    repattern = re.compile(pattern)
    newname   = pattern_end
    try:
        search = repattern.search(name)
        if search:
            groups = search.groups()
            for i in range(len(groups)):
                newname = newname.replace("{" + str(i+1) + "}", groups[i])
        else:
            return None
    except Exception as e:
        return None

    # Replace {num} with item number.
    # If {num2} the number will be 02
    # If {num3+10} the number will be 010
    count = str(count)
    cr = re.compile("{(num)([0-9]*)}|{(num)([0-9]*)(\+)([0-9]*)}")
    try:
        cg = cr.search(newname).groups()
        if len(cg) == 6:
            if cg[0] == "num":
                # {num2}
                if cg[1] != "":
                    count = count.zfill(int(cg[1]))
                newname = cr.sub(count, newname)
            elif cg[2] == "num" and cg[4] == "+":
                # {num2+5}
                if cg[5] != "":
                    count = str(int(count)+int(cg[5]))
                if cg[3] != "":
                    count = count.zfill(int(cg[3]))
        newname = cr.sub(count, newname)
    except:
        pass

    # Some date replacements
    n = newname
    n = n.replace("{date}",      time.strftime("%Y-%m-%d", time.localtime()))
    n = n.replace("{year}",      time.strftime("%Y",       time.localtime()))
    n = n.replace("{month}",     time.strftime("%m",       time.localtime()))
    n = n.replace("{monthname}", time.strftime("%B",       time.localtime()))
    n = n.replace("{monthsimp}", time.strftime("%b",       time.localtime()))
    n = n.replace("{day}",       time.strftime("%d",       time.localtime()))
    n = n.replace("{dayname}",   time.strftime("%A",       time.localtime()))
    n = n.replace("{daysimp}",   time.strftime("%a",       time.localtime()))
    newname = n

    # Replace {rand} with random number between 0 and 100.
    # If {rand500} the number will be between 0 and 500
    # If {rand10-20} the number will be between 10 and 20
    # If you add ,[ 5 the number will be padded with 5 digits
    # ie. {rand20,5} will be a number between 0 and 20 of 5 digits (00012)
    rnd = ""
    cr = re.compile("{(rand)([0-9]*)}"
                    "|{(rand)([0-9]*)(\-)([0-9]*)}"
                    "|{(rand)([0-9]*)(\,)([0-9]*)}"
                    "|{(rand)([0-9]*)(\-)([0-9]*)(\,)([0-9]*)}")
    try:
        cg = cr.search(newname).groups()
        if len(cg) == 16:
            if (cg[0] == "rand"):
                if (cg[1] == ""):
                    # {rand}
                    rnd = random.randint(0, 100)
                else:
                    # {rand2}
                    rnd = random.randint(0, int(cg[1]))
            elif rand_case_1(cg):
                # {rand10-100}
                rnd = random.randint(int(cg[3]), int(cg[5]))
            elif rand_case_2(cg):
                if (cg[7] == ""):
                    # {rand,2}
                    rnd = str(random.randint(0, 100)).zfill(int(cg[9]))
                else:
                    # {rand10,2}
                    rnd = str(random.randint(0, int(cg[7]))).zfill(int(cg[9]))
            elif rand_case_3(cg):
                # {rand2-10,3}
                s = str(random.randint(int(cg[11]), int(cg[13])))
                rnd = s.zfill(int(cg[15]))
        newname = cr.sub(str(rnd), newname)
    except:
        pass
    return newname


def rand_case_1(cg):
    r = ((cg[2] == "rand") and
         (cg[4] == "-") and
         (cg[3] != "") and
         (cg[5] != ""))
    return r


def rand_case_2(cg):
    r = ((cg[6] == "rand") and
         (cg[8] == ",") and
         (cg[9] != ""))
    return r


def rand_case_3(cg):
    r = ((cg[10] == "rand") and
         (cg[12] == "-") and
         (cg[14] == ",") and
         (cg[11] != "") and
         (cg[13] != "") and
         (cg[15] != ""))
    return r


def process_replace(name, old, new):
    return name.replace(old, new)


def process_sanitize(name):
    return " ".join(split_alphanumeric(name))


def process_substitute(mode, name):
    return SUBSTITUTE_FUNS[mode](name)


def process_tokenize(mode, name):
    refs = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tokens = split_alphanumeric(name)

    if len(refs) < len(tokens):
        sys.exit(ERRMSGS['too_many_tokens'])

    i = 0
    t2i = {}
    i2t = {}
    for token in tokens:
        i2t[refs[i]] = token
        if token not in t2i:
            t2i[token] = refs[i]
        i += 1

    print(name)
    for token in tokens:
        print(t2i[token] + ' ' * len(token), end="")
    print("\n> ", end="")
    sys.stdout.flush()

    pattern = sys.stdin.readline()
    result = pattern[:-1]
    try:
        if mode == "1":
            result = " ".join([i2t[i] for i in result.strip().split(' ')])
        elif mode == "2":
            for i, t in i2t.items():
                result = result.replace("{" + i + "}", t)
        elif mode == "3":
            for i in i2t.keys():
                result = result.replace(i, "{" + i + "}")
            for i, t in i2t.items():
                result = result.replace("{" + i + "}", t)
        else:
            sys.exit("unknown mode: " + mode)
    except Exception as e:
        sys.exit("unknown error: ", e)
    return result


def process_verbosity(config, lvl):
    config.verbosity = lvl


###############################################################################
# GLOBALS


ACTION_HANDLERS = {
    "camelcase"  : handle_camel_case,
    "case"       : handle_case,
    "delete"     : handle_delete,
    "extension"  : handle_extension,
    "file"       : handle_file,
    "insert"     : handle_insert,
    "pattern"    : handle_pattern_match,
    "replace"    : handle_replace,
    "sanitize"   : handle_sanitize,
    "substitute" : handle_substitute,
    "tokenize"   : handle_tokenize,
    "verbosity"  : handle_verbosity
}
CASE_FUNS = {
    "uc": lambda x: x.upper(),
    "lc": lambda x: x.lower(),
    "sc": lambda x: x.capitalize(),
    "tc": lambda x: "".join([y.capitalize() for y in split(x)])
}
SUBSTITUTE_FUNS = {
    "sd": lambda x: x.replace(" ", "-"),
    "sp": lambda x: x.replace(" ", "."),
    "su": lambda x: x.replace(" ", "_"),
    "ud": lambda x: x.replace("_", "-"),
    "up": lambda x: x.replace("_", "."),
    "us": lambda x: x.replace("_", " "),
    "pd": lambda x: x.replace(".", "-"),
    "ps": lambda x: x.replace(".", " "),
    "pu": lambda x: x.replace(".", "_"),
    "dp": lambda x: x.replace("-", "."),
    "ds": lambda x: x.replace("-", " "),
    "du": lambda x: x.replace("-", "_")
}

###############################################################################
# MAIN


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def obtain_confirmation(config, filename_fn_buffer):
    if config.yes_mode:
        return True
    else:
        print("y/n?")
        ch = getch()
        if (ch == "y"):
            return True
        elif (ch == "n"):
            return False
        else:
            sys.exit("unrecognized input")


def verbosity_set(actions):
    f = lambda x, y: x or y
    l = [(a.name == "verbosity") and (a.arg1 > 1) for a in actions]
    r = functools.reduce(f, l, False)
    return r


def main():
    config, actions = parse_args(sys.argv)

    if len(actions) > 0:
        if verbosity_set(actions):
            print_actions(actions)

        fn_buffer = handle_actions(config, actions)

        if 1 <= config.verbosity <= 2:
            print_fn_buffer(config, fn_buffer)
        confirmed = obtain_confirmation(config, fn_buffer)

        if config.undo:
            output_undo_script(fn_buffer)
        if confirmed:
            rename_files(config, fn_buffer)

###############################################################################
if (__name__ == "__main__"):
    main()
