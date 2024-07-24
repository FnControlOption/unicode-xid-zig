# unicode-xid-zig

[![Docs](https://github.com/FnControlOption/unicode-xid-zig/actions/workflows/docs.yml/badge.svg)](https://fncontroloption.github.io/unicode-xid-zig/)
![License: MIT OR Apache-2.0](https://img.shields.io/crates/l/unicode-xid.svg)

Zig port of [unicode-xid](https://github.com/unicode-rs/unicode-xid) Rust crate

```zig
const std = @import("std");
const assert = std.debug.assert;
const unicode_xid = @import("unicode_xid");

pub fn main() void {
    assert(unicode_xid.isXidStart('a')); // 'a' is a valid start of an identifier
    assert(unicode_xid.isXidStart('△') == false); // '△' is a NOT valid start of an identifier
}
```
