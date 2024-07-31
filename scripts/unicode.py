#!/usr/bin/env python
#
# Derived from https://github.com/unicode-rs/unicode-xid/blob/master/scripts/unicode.py
#
# Copyright 2011-2015 The Rust Project Developers. See <COPYRIGHT-RUST>
# or <https://github.com/rust-lang/rust/blob/master/COPYRIGHT>.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
# <http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

# This script uses the following Unicode tables:
# - DerivedCoreProperties.txt
# - ReadMe.txt
#
# Since this should not require frequent updates, we just store this
# out-of-line and check the unicode.rs file into git.

import fileinput, re, os, sys

preamble = '''// Based on https://github.com/unicode-rs/unicode-xid
//
// Copyright 2012-2015 The Rust Project Developers. See <COPYRIGHT-RUST>
// or <https://github.com/rust-lang/rust/blob/master/COPYRIGHT>.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
// <http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// NOTE: The following code was generated by "scripts/unicode.py", do not edit directly

pub const Range = struct { u21, u21 }; // FIXME: https://github.com/ziglang/zig/issues/20759
'''

def fetch(f):
    if not os.path.exists(os.path.basename(f)):
        os.system("curl -O http://www.unicode.org/Public/UNIDATA/%s"
                  % f)

    if not os.path.exists(os.path.basename(f)):
        sys.stderr.write("cannot load %s" % f)
        exit(1)

def group_cat(cat):
    cat_out = []
    letters = sorted(set(cat))
    cur_start = letters.pop(0)
    cur_end = cur_start
    for letter in letters:
        assert letter > cur_end, \
            "cur_end: %s, letter: %s" % (hex(cur_end), hex(letter))
        if letter == cur_end + 1:
            cur_end = letter
        else:
            cat_out.append((cur_start, cur_end))
            cur_start = cur_end = letter
    cat_out.append((cur_start, cur_end))
    return cat_out

def ungroup_cat(cat):
    cat_out = []
    for (lo, hi) in cat:
        while lo <= hi:
            cat_out.append(lo)
            lo += 1
    return cat_out

def load_properties(f, interestingprops):
    fetch(f)
    props = {}
    re1 = re.compile(r"^ *([0-9A-F]+) *; *(\w+)")
    re2 = re.compile(r"^ *([0-9A-F]+)\.\.([0-9A-F]+) *; *(\w+)")

    for line in fileinput.input(os.path.basename(f)):
        prop = None
        d_lo = 0
        d_hi = 0
        m = re1.match(line)
        if m:
            d_lo = m.group(1)
            d_hi = m.group(1)
            prop = m.group(2)
        else:
            m = re2.match(line)
            if m:
                d_lo = m.group(1)
                d_hi = m.group(2)
                prop = m.group(3)
            else:
                continue
        if interestingprops and prop not in interestingprops:
            continue
        d_lo = int(d_lo, 16)
        d_hi = int(d_hi, 16)
        if prop not in props:
            props[prop] = []
        props[prop].append((d_lo, d_hi))

    # optimize if possible
    for prop in props:
        props[prop] = group_cat(ungroup_cat(props[prop]))

    return props

def escape_char(c):
    return "'\\u{%x}'" % c

def emit_table(f, name, t_data, t_type = "[]const Range", is_pub=True,
        pfun=lambda x: ". { %s, %s }" % (escape_char(x[0]), escape_char(x[1]))):
    pub_string = "const"
    if is_pub:
        pub_string = "pub " + pub_string
    f.write("\n%s %s: %s = &.{\n" % (pub_string, name, t_type))
    for dat in t_data:
        f.write("    %s,\n" % pfun(dat))
    f.write("};\n")

if __name__ == "__main__":
    r = "tables.zig"
    if os.path.exists(r):
        os.remove(r)
    with open(r, "w") as rf:
        # write the file's preamble
        rf.write(preamble)

        # download and parse all the data
        fetch("ReadMe.txt")
        with open("ReadMe.txt") as readme:
            pattern = r"for Version (\d+)\.(\d+)\.(\d+) of the Unicode"
            unicode_version = re.search(pattern, readme.read()).groups()
        rf.write("""
/// The version of [Unicode](http://www.unicode.org/)
/// that this version of unicode-xid is based on.
pub const unicode_version: struct { u64, u64, u64 } = .{ %s, %s, %s };
""" % unicode_version)

        want_derived = ["XID_Start", "XID_Continue"]
        derived = load_properties("DerivedCoreProperties.txt", want_derived)
        for cat in sorted(want_derived):
            emit_table(rf, cat.lower(), derived[cat])
