#!/bin/python
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

################################################################################
# GLOBALS

"""
    -m [f | d | b]
        f: operate only on files (default)
        d: operate only on directories
        b: operate both on directories and files
"""

USAGE = """
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
    -y
        Yes mode, do not prompt for confirmation.

    -f FILENAME
        Run on file FILENAME
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
    -d X (Y | end)
        Delete from position X to Y [or end]
    [+|-]e [EXT]
        Modify extension.
    -i X (Y | end)
        Insert X at position Y [or end]
        X must be a string
        Y must be either the string "end" or an integer
    -n
       Sanitize the filename by removing anything that is not alfanumeric.
    -r X Y
        Replace X with Y.
    -s [sd | sp | su | ud | up | us | pd | ps | pu | dp | ds | du ]
        Substitute characters:
            sd: spaces to dashes
            sp: spaces to periods
            su: spaces to underscores
            ud: underscores to dashes
            up: underscores to periods
            us: underscores to spaces
            pd: periods to dashes
            ps: periods to space
            pu: periods to underscores
            dp: dashes to periods
            ds: dashes to spaces
            du: dashes to underscores
"""

YES_MODE = False
# lvl 0: silent running
# lvl 1: default, show file name buffer before getting confirmation
# lvl 2: verbose, show actions and file name buffer before getting confirmation
# lvl 3: very verbose, show actions and file name buffer state after each action
VERBOSITY_LEVEL = 1
# mode 0: operate on files only
# mode 1: operate on directories only
# mode 2: operate on fiels and directories
FILE_MODE = 0 # operate on files only by default
VALID_FLAGS = frozenset(
    [ "-c", "-C", "-d", "-e", "+e", "f", "-h", "-i", "-n", "-p", "-r", "-s",
      "-t", "-y", "-v0", "-v1", "-v2", "-v3"
    ])
VALID_SUBTITUTION_OPTIONS = frozenset(
    ["sd", "sp", "su", "ud", "up", "us", "pd", "ps", "pu", "dp", "ds", "du"]
    )
VALID_CASE_OPTIONS = frozenset(
    ["lc", "uc", "tc", "sc"]
    )

ERRMSGS = {
    "file-arity"      : "-f flag requires a filename parameter",
    "case-arity"      : "-c flag requires a parameter",
    "case-type"       : "argument for -c may be one of: lc uc tc sc",
    "extension-arity" : "+e flag requires a parameter",
    "delete-arity"    : "-d flag requires two parameters",
    "delete-type-1"   : "first argument to -d must be an integer",
    "delete-type-2"   : "second argument to -d must be either 'end' or an integer",
    "delete-type-3"   : "numerical arguments to -d must be non negative integers",
    "delete-index-1"  : "first argument to -d is out of range",
    "delete-index-2"  : "second argument to -d is out of range",
    "delete-index-3"  : "first argument to -d is greater than second argument",
    "insert-arity"    : "-i flag requires two parameters",
    "insert-type-1"   : "second argument to -i must be either 'end' or an integer",
    "insert-type-2"   : "numerical arguments to -i must be non-negative integers",
    "indert-index"    : "second argument to -i is out of range",
    "pattern-arity"   : "-p flag requires two parameters",
    "replace-arity"   : "-r flag requires two parameters",
    "subs-arity"      : "-s flag requires a parameter",
    "subs-type"       : "argument for -s may be one of: sd | sp | su | ud | up | us | pd | ps | pu | dp | ds | du",
    "verbosity-arity" : "-vX flag requires a parameter",
    "verbosity-type"  : "argument to -vX flag requires an integer between 0 and 3",
    "duplicate"       : "action will result in two or more identical file names!",
    "tokenize-arity"  : "-t flag requires one parameter",
    "too_many_tokens" : "a file has too many tokens"
}
# mode 0: operate on files only
# mode 1: operate on directories only
# mode 2: operate on fiels and directories
FILE_MODE = 0 # operate on files only by default
UNDO = False
# lvl 0: silent running
# lvl 1: default, show file name buffer before getting confirmation
# lvl 2: verbose, show actions and file name buffer before getting confirmation
# lvl 3: very verbose, show actions and file name buffer state after each action
VALID_FLAGS = frozenset(
    [ "-c", "-C", "-d", "-e", "+e", "-f", "-h", "-i", "-n", "-p", "-r", "-s",
      "-u", "-v", "-y"
    ])
VALID_SUBTITUTION_OPTIONS = frozenset(
    [ "sd", "sp", "su", "ud", "up", "us", "pd", "ps", "pu", "dp", "ds", "du"
    ])
VALID_CASE_OPTIONS = frozenset(["lc", "uc", "tc", "sc"])
VERBOSITY_LEVEL = 1
YES_MODE = False

SPLIT_REGEX        = re.compile(r"[a-zA-Z0-9]+|[^a-zA-Z0-9]+")
FIRST_CAP_REGEX    = re.compile(r"(.)([A-Z][a-z]+)")
ALL_CAP_REGEX      = re.compile(r"([a-z0-9])([A-Z])")
ALPHANUMERIC_REGEX = re.compile(r"[a-zA-Z0-9]+")

ACTION_HANDLERS = {}
CASE_FUNS = {}
SUBSTITUTE_FUNS = {}


################################################################################
# CLASSES


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
        # full is a read-only attribute which stores the filename inlcuding the
        # final period and extension

    def full(self):
        if self.ext:
            return self.name + "." + self.ext
        else:
            return self.name

    def set_name(self, name):
        self.name = name

    def set_ext(self, ext):
        self.ext = ext


################################################################################
# FILE AND BUFFER HANDLING


def escape_pattern(pattern):
    """ Escape special chars on patterns, so glob doesn"t get confused """
    return pattern.replace("[", "[[]")


def get_file_listing(dir=os.getcwd(), mode=0, pattern=None, recursive=False):
    filelist = []
    if pattern:
        if dir != "/": dir += "/"
        dir = escape_pattern(dir + pattern)
        listaux = glob.glob(dir)
    else:
        listaux = os.listdir(dir)

    listaux.sort(key=str.lower)
    if recursive:
        pass
    else:
        if mode == 0:
            # Get files
            for elem in listaux:
                abspath = os.path.abspath(elem)
                if not os.path.isdir(abspath):
                    path, name = os.path.split(abspath)
                    path += os.sep
                    name, ext = os.path.splitext(name)
                    filelist.append(File(path, name, ext[1:]))
    return filelist


def init_fn_buffer():
    fn_buffer = {}
    files = get_file_listing()
    for f in files:
        fn_buffer[f.full()] = f
    return fn_buffer


def rename_file(old, new):
    try:
        if old == new:
            return True
        os.renames(old, new)
        return True
    except Exception:
        print("error while renaming {} to {}".format(old, new))
        return False


def rename_files(fn_buffer):
    for k, v in fn_buffer.items():
        if (k != fn_buffer[k].full()) and os.path.exists(fn_buffer[k].full()):
            t = fn_buffer[k].name + fn_buffer[k].ext
            sys.exit("error while renaming {} to {}! -> {} already exists!".format(k, t, t))
    for k, v in sorted(fn_buffer.items()):
        rename_file(v.path + k, v.path + v.full())


def output_undo_script(fn_buffer):
    f = open("undo.sh", "w")
    for k, v in fn_buffer.items():
        f.write('mv "{}" "{}"\n'.format(v.full(), k))
    f.close()


def verify_fn_buffer(fn_buffer):
    for k1, v1 in fn_buffer.items():
        for k2, v2 in fn_buffer.items():
            if (k1 != k2) and (v1.full() == v2.full()):
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


################################################################################
# LIST AND STRING MANGLING


def split(string):
    return SPLIT_REGEX.findall(string)


def split_camel_case(string):
    s = FIRST_CAP_REGEX.sub(r"\1 \2", string)
    return ALL_CAP_REGEX.sub(r"\1 \2", s)


def split_alphanumeric(string):
    return ALPHANUMERIC_REGEX.findall(string)


################################################################################
# PARSING


def parse_args(argv):
    global UNDO
    global VERBOSITY_LEVEL
    global YES_MODE

    actions = []
    l = len(argv)
    i = 1
    while (i < l):
        if argv[i] == "-c":
            msg =  ERRMSGS["case-arity"]
            i, actions = parse_one(argv, i, actions, "case", msg)
            if not (actions[-1].arg1 in VALID_CASE_OPTIONS):
                msg = ERRMSGS["case-type"]
                sys.exit(msg)
        elif argv[i] == "-C":
            actions.append(Action("camelcase"))
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
        elif argv[i] in ["-e", "+e"]:
            i, actions = parse_extension(argv, i, actions)
        elif argv[i] == "-f":
            msg = ERRMSGS["file-arity"]
            i, actions = parse_one(argv, i, actions, "file", msg)
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
        elif argv[i] == "-n":
            actions.append(Action("sanitize"))
            i += 1
        elif argv[i] == "-p":
            msg = ERRMSGS["pattern-arity"]
            i, actions = parse_two(argv, i, actions, "pattern", msg)
        elif argv[i] == "-r":
            msg = ERRMSGS["replace-arity"]
            i, actions = parse_two(argv, i, actions, "replace", msg)
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
            UNDO = True
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
            usage()
            sys.exit()
        elif argv[i] == "-y":
            YES_MODE = True
            i += 1
        else:
            usage()
            msg = "unrecognized flag: {}".format(argv[i])
            sys.exit(msg)
    return actions


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
    l    = len(argv)
    mode = argv[i][0] # will be either + or -
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
    if mode == "+" and action.arg2 == None:
        sys.exit(ERRMSGS["extension-arity"])
    actions.append( action )
    return i, actions


################################################################################
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


def print_fn_buffer(fn_buffer):
    maxlen = 0
    for k in fn_buffer.keys():
        maxlen = max(maxlen, len(k))

    for k, v in sorted(fn_buffer.items()):
        print("{}{}=> {}".format(
            k,
            (" " * (maxlen - len(k) + 1)),
            v.full()
        ))
    print()


################################################################################
# ACTION HANDLERS


def handle_actions(actions):
    fn_buffer = init_fn_buffer()
    for action in actions:
        fn_buffer = ACTION_HANDLERS[action.name](action, fn_buffer)
        if (VERBOSITY_LEVEL > 2) and (action.name != "verbosity"):
            print_sep()
            print_action(action)
            print_fn_buffer(fn_buffer)
        verify_fn_buffer(fn_buffer)
    return clean_fn_buffer(fn_buffer)


def handle_camel_case(action, fn_buffer):
    for k, v, in fn_buffer.items():
        fn_buffer[k].set_name(process_camel_case(v.name))
    return fn_buffer


def handle_case(action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_case(action.arg1, v.name))
    return fn_buffer


def handle_file(action, fn_buffer):
    new_fn_buffer = fn_buffer.copy()
    for k in fn_buffer.keys():
        if (k != action.arg1):
            del new_fn_buffer[k]
    return new_fn_buffer


def handle_delete(action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_delete(action.arg1, action.arg2, v.name))
    return fn_buffer


def handle_extension(action, fn_buffer):
    for k, v in fn_buffer.items():
        name, ext = process_extension(action.arg1, action.arg2, v.name)
        fn_buffer[k].set_name(name)
        fn_buffer[k].set_ext(ext)
    return fn_buffer


def handle_insert(action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_insert(fn_buffer[k].name, action.arg1, action.arg2)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_pattern_match(action, fn_buffer):
    count = 0
    new_fn_buffer = fn_buffer.copy()
    for k, v in fn_buffer.items():
        n = process_pattern_match(v.name, action.arg1, action.arg2, count)
        if (n):
            new_fn_buffer[k].set_name(n)
        else:
            del new_fn_buffer[k]
        count += 1
    return new_fn_buffer


def handle_replace(action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_replace(v.name, action.arg1, action.arg2)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_sanitize(action, fn_buffer):
    for k, v in fn_buffer.items():
        fn_buffer[k].set_name(process_sanitize(v.name))
    return fn_buffer


def handle_substitute(action, fn_buffer):
    for k, v in fn_buffer.items():
        n = process_substitute(action.arg1, v.name)
        fn_buffer[k].set_name(n)
    return fn_buffer


def handle_tokenize(action, fn_buffer):
    for k, v in buffer.items():
        fn_buffer[k].set_name(process_tokenize(action.arg1, v.name))
    return fn_buffer


def handle_verbosity(action, fn_buffer):
    process_verbosity(action.arg1)
    return fn_buffer


################################################################################
# ACTION PROCESSORS


def process_camel_case(name):
    return split_camel_case(name)


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
    textend = name[end + 1 : len(name)]
    newname = textini + textend
    return newname


def process_extension(mode, ext, name):
    if mode == "+":
        pass
        # add an extension
        # if (ext and name):
            # name += ('.' + ext)
    if mode == "-":
        if ext and name:
            # change the extension to ext
            if "." in name:
                aux  = name.split(".")[-1]
                name = name[0 : len(name) - len(aux) - 1]
                name += ext
        else:
            # remove the extension
            if "." in name:
                ext  = name.split(".")[-1]
                name = name[0 : len(name) - len(ext) - 1]
                ext  = ""
            else:
                ext  = ""
    return name, ext


def process_insert(name, text, pos):
    if pos == "end":
        pos = len(name)
        newname = name + text
    elif (pos > len(name)):
        sys.exit(ERRMSGS["insert-index-1"])
    else:
        newname = name[0 : pos] + text + name[pos : len(name)]
    return newname


def process_pattern_match(name, pattern_ini, pattern_end, count):
    """
    This method parses the patterns given by the user.
    Possible patterns are:

    {#} Numbers
    {L} Letters
    {C} Characters (Numbers & letters, not spaces)
    {X} Numbers, letters, and spaces
    {@} Trash
    """

    pattern   = pattern_ini
    pattern   = pattern.replace(".","\.")
    pattern   = pattern.replace("[","\[")
    pattern   = pattern.replace("]","\]")
    pattern   = pattern.replace("(","\(")
    pattern   = pattern.replace(")","\)")
    pattern   = pattern.replace("?","\?")
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
                newname = newname.replace("{"+ str(i+1) +"}", groups[i])
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

    # Replace {dir} with directory name
    dir = os.path.abspath("./")
    dir = os.path.dirname(dir)
    dir = os.path.basename(dir)
    newname = newname.replace("{dir}", dir)

    # Some date replacements
    newname = newname.replace("{date}",      time.strftime("%Y-%m-%d", time.localtime()))
    newname = newname.replace("{year}",      time.strftime("%Y",       time.localtime()))
    newname = newname.replace("{month}",     time.strftime("%m",       time.localtime()))
    newname = newname.replace("{monthname}", time.strftime("%B",       time.localtime()))
    newname = newname.replace("{monthsimp}", time.strftime("%b",       time.localtime()))
    newname = newname.replace("{day}",       time.strftime("%d",       time.localtime()))
    newname = newname.replace("{dayname}",   time.strftime("%A",       time.localtime()))
    newname = newname.replace("{daysimp}",   time.strftime("%a",       time.localtime()))

    # Replace {rand} with random number between 0 and 100.
    # If {rand500} the number will be between 0 and 500
    # If {rand10-20} the number will be between 10 and 20
    # If you add ,5 the number will be padded with 5 digits
    # ie. {rand20,5} will be a number between 0 and 20 of 5 digits (00012)
    rnd = ""
    cr = re.compile("{(rand)([0-9]*)}"
                    "|{(rand)([0-9]*)(\-)([0-9]*)}"
                    "|{(rand)([0-9]*)(\,)([0-9]*)}"
                    "|{(rand)([0-9]*)(\-)([0-9]*)(\,)([0-9]*)}")
    try:
        cg = cr.search(newname).groups()
        if (len(cg) == 16):

            if (cg[0] == "rand"):
                if (cg[1] == ""):
                    # {rand}
                    rnd = random.randint(0, 100)
                else:
                    # {rand2}
                    rnd = random.randint(0, int(cg[1]))

            elif (cg[2] == "rand") and (cg[4] == "-") and (cg[3] != "") and (cg[5] != ""):
                # {rand10-100}
                rnd = random.randint(int(cg[3]), int(cg[5]))

            elif (cg[6] == "rand") and (cg[8] == ",") and (cg[9] != ""):
                if (cg[7] == ""):
                    # {rand,2}
                    rnd = str(random.randint(0, 100)).zfill(int(cg[9]))
                else:
                    # {rand10,2}
                    rnd = str(random.randint(0, int(cg[7]))).zfill(int(cg[9]))

            elif (cg[10] == "rand") and (cg[12] == "-") and (cg[14] == ",") and (cg[11] != "") and (cg[13] != "") and (cg[15] != ""):
                # {rand2-10,3}
                rnd = str(random.randint(int(cg[11]), int(cg[13]))).zfill(int(cg[15]))

        newname = cr.sub(str(rnd), newname)
    except:
        pass

    return newname


def process_replace(name, old, new):
    return name.replace(old, new)


def process_sanitize(name):
    return " ".join(split_alphanumeric(name))


def process_substitute(mode, name):
    return SUBSTITUTE_FUNS[mode](name)


def process_tokenize(mode, name):
    token_refs = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tokens     = split_alphanumeric(name)

    if len(token_refs) < len(tokens):
        sys.exit(ERRMSGS['too_many_tokens'])

    i   = 0
    t2i = {}
    i2t = {}
    for token in tokens:
        i2t[token_refs[i]] = token
        if not token in t2i:
            t2i[token] = token_refs[i]
        i += 1

    print(name)
    for token in tokens:
        print(t2i[token] + ' ' * len(token), end="")
    print("\n> ", end="")
    sys.stdout.flush()

    pattern = sys.stdin.readline()
    result  = pattern[:-1]
    try:
        if mode == "1":
            result = " ".join([ i2t[i] for i in result.strip().split(' ')])
        elif mode == "2":
            for i, t in i2t.items():
                result = result.replace("{" + i + "}", t)
        elif mode == "3":
            for i in i2t.keys():
                result = result.replace(i, "{" + i + "}")
            for i, t in i2t.items():
                result = result.replace("{" + i + "}", t)
        else:
            sys.exit("unknown mode: " ++ mode)
    except Exception as e:
        sys.exit("unknown error: ", e)
    return result


def process_verbosity(lvl):
    global VERBOSITY_LEVEL
    print("setting verbosity level to {}".format(lvl))
    VERBOSITY_LEVEL = lvl


################################################################################
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
    "uc" : lambda x: x.upper(),
    "lc" : lambda x: x.lower(),
    "sc" : lambda x: x.capitalize(),
    "tc" : lambda x: "".join([y.capitalize() for y in split(x)])
}
SUBSTITUTE_FUNS = {
    "sd" : lambda x: x.replace(" ", "-"),
    "sp" : lambda x: x.replace(" ", "."),
    "su" : lambda x: x.replace(" ", "_"),
    "ud" : lambda x: x.replace("_", "-"),
    "up" : lambda x: x.replace("_", "."),
    "us" : lambda x: x.replace("_", " "),
    "pd" : lambda x: x.replace(".", "-"),
    "ps" : lambda x: x.replace(".", " "),
    "pu" : lambda x: x.replace(".", "_"),
    "dp" : lambda x: x.replace("-", "."),
    "ds" : lambda x: x.replace("-", " "),
    "du" : lambda x: x.replace("-", "_")
}

################################################################################
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


def obtain_confirmation(filename_fn_buffer):
    if YES_MODE:
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


def usage():
    print(USAGE)


def main():
    actions = parse_args(sys.argv)

    if len(actions) > 0:
        f = lambda x, y: x or y
        l = [(a.name == "verbosity") and (a.arg1 > 1) for a in actions]
        r = functools.reduce(f, l, False)
        if r:
            print_actions(actions)

        fn_buffer = handle_actions(actions)

        if VERBOSITY_LEVEL in [1, 2]:
            print_fn_buffer(fn_buffer)
        confirmed = obtain_confirmation(fn_buffer)

        if UNDO:
            output_undo_script(fn_buffer)
        if confirmed:
            rename_files(fn_buffer)

################################################################################
if (__name__ == "__main__"):
    main()

