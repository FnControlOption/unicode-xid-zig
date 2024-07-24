// Based on https://github.com/unicode-rs/unicode-xid
//
// Copyright 2012-2015 The Rust Project Developers. See <COPYRIGHT-RUST>
// or <https://github.com/rust-lang/rust/blob/master/COPYRIGHT>.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
// <http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

//! Determine if a char is a valid identifier for a parser and/or lexer according to
//! [Unicode Standard Annex #31](http://www.unicode.org/reports/tr31/) rules.

const std = @import("std");
const sort = std.sort;
const math = std.math;
const testing = std.testing;

const tables = @import("tables.zig");
const Range = tables.Range;

pub const unicode_version = tables.unicode_version;

fn bsearchRangeTable(c: u21, r: []const Range) bool {
    const compare = struct {
        fn func(_: void, key: u21, mid_item: Range) math.Order {
            const lo, const hi = mid_item;
            return if (lo > key) .lt else if (hi < key) .gt else .eq;
        }
    };
    return sort.binarySearch(Range, c, r, {}, compare.func) != null;
}

/// Returns whether the specified character satisfies the 'XID_Start'
/// Unicode property.
///
/// 'XID_Start' is a Unicode Derived Property specified in
/// [UAX #31](http://unicode.org/reports/tr31/#NFKC_Modifications),
/// mostly similar to ID_Start but modified for closure under NFKx.
pub inline fn isXidStart(c: u21) bool {
    // Fast-path for ascii idents
    return ('a' <= c and c <= 'z') or
        ('A' <= c and c <= 'Z') or
        (c > '\x7f' and bsearchRangeTable(c, tables.XID_Start));
}

/// Returns whether the specified char satisfies the 'XID_Continue'
/// Unicode property.
///
/// 'XID_Continue' is a Unicode Derived Property specified in
/// [UAX #31](http://unicode.org/reports/tr31/#NFKC_Modifications),
/// mostly similar to 'ID_Continue' but modified for closure under NFKx.
pub inline fn isXidContinue(c: u21) bool {
    // Fast-path for ascii idents
    return ('a' <= c and c <= 'z') or
        ('A' <= c and c <= 'Z') or
        ('0' <= c and c <= '9') or
        c == '_' or
        (c > '\x7f' and bsearchRangeTable(c, tables.XID_Continue));
}

test isXidStart {
    try testing.expect(isXidStart('A'));
    try testing.expect(isXidStart('Z'));
    try testing.expect(isXidStart('a'));
    try testing.expect(isXidStart('z'));
    try testing.expect(isXidStart('\u{1000d}'));
    try testing.expect(isXidStart('\u{10026}'));

    try testing.expectEqual(false, isXidStart('\x00'));
    try testing.expectEqual(false, isXidStart('\x01'));
    try testing.expectEqual(false, isXidStart('0'));
    try testing.expectEqual(false, isXidStart('9'));
    try testing.expectEqual(false, isXidStart(' '));
    try testing.expectEqual(false, isXidStart('['));
    try testing.expectEqual(false, isXidStart('<'));
    try testing.expectEqual(false, isXidStart('{'));
    try testing.expectEqual(false, isXidStart('('));
    try testing.expectEqual(false, isXidStart('\u{02c2}'));
    try testing.expectEqual(false, isXidStart('\u{ffff}'));
}

test isXidContinue {
    try testing.expect(isXidContinue('0'));
    try testing.expect(isXidContinue('9'));
    try testing.expect(isXidContinue('A'));
    try testing.expect(isXidContinue('Z'));
    try testing.expect(isXidContinue('a'));
    try testing.expect(isXidContinue('z'));
    try testing.expect(isXidContinue('_'));
    try testing.expect(isXidContinue('\u{1000d}'));
    try testing.expect(isXidContinue('\u{10026}'));

    try testing.expectEqual(false, isXidContinue('\x00'));
    try testing.expectEqual(false, isXidContinue('\x01'));
    try testing.expectEqual(false, isXidContinue(' '));
    try testing.expectEqual(false, isXidContinue('['));
    try testing.expectEqual(false, isXidContinue('<'));
    try testing.expectEqual(false, isXidContinue('{'));
    try testing.expectEqual(false, isXidContinue('('));
    try testing.expectEqual(false, isXidContinue('\u{02c2}'));
    try testing.expectEqual(false, isXidContinue('\u{ffff}'));
}
