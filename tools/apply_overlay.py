#!/usr/bin/env python3
"""Puts the stock market mod into an OpenTTD source tree. Safe to run more than once.

Usage:  python3 tools/apply_overlay.py /path/to/openttd            (add the mod)
        python3 tools/apply_overlay.py /path/to/openttd --check    (only check that nothing clashes)

What it does:
  - copies the C++ files of the mod into the OpenTTD tree (see FILES for where every file goes)
  - adds the commands to the Commands enum in src/command_type.h
  - adds the new source files to src/CMakeLists.txt
  - adds the strings of lang/*.txt to src/lang/english.txt

The mod files are found by name anywhere in this repository, so the category folders (stock/, gui/, wallet/, bank/, ...)
can be rearranged without touching this script. A file name that exists twice is an error, so an old copy can never
silently win over the new one.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the repository
SKIP_DIRS = {".git", ".github", "docs", "patch"}

FILES = {  # file name -> folder in the OpenTTD tree
    "stock_base.h": "src", "stock_base.cpp": "src",
    "stock_cmd.h": "src", "stock_cmd.cpp": "src",
    "stock_gui.h": "src", "stock_gui.cpp": "src", "stock_order_gui.cpp": "src",
    "wallet_base.h": "src", "wallet_base.cpp": "src",
    "wallet_cmd.h": "src", "wallet_cmd.cpp": "src",
    "central_bank.h": "src", "central_bank.cpp": "src",
    "stock_sl.cpp": "src/saveload",
    "stock_sl_compat.h": "src/saveload/compat",
    "stock_widget.h": "src/widgets",
}
NEW_COMMANDS = [  # in the order they are added after CMD_STOCK_CLOSE
    ("CMD_STOCK_MODIFY", "change a position or a pending order"),
    ("CMD_STOCK_TRANSFER", "move money between the company cash and the first trading wallet"),
    ("CMD_STOCK_ENABLE_DAILY", "start recording daily candles"),
    ("CMD_WALLET_CREATE", "create a trading wallet"),
    ("CMD_WALLET_DELETE", "delete a trading wallet"),
    ("CMD_WALLET_TRANSFER", "move money between two wallets"),
    ("CMD_BANK_BORROW", "borrow from the central bank"),
    ("CMD_BANK_REPAY", "repay the central bank"),
]
NEW_SOURCES = ["wallet_base.cpp", "wallet_base.h", "wallet_cmd.cpp", "wallet_cmd.h", "central_bank.cpp", "central_bank.h"]
REPLACE_KEYS = {"STR_STOCK_TIP_TOOLBOX", "STR_STOCK_TIP_SUMMARY", "STR_STOCK_ORDER_INFO", "STR_STOCK_TIP_DEPOSIT", "STR_STOCK_TIP_WITHDRAW"}
STRING_FILES = ["english_stock_strings.txt", "english_wallet_strings.txt", "english_round8_strings.txt"]
ANCHORS = ["STR_STOCK_ERROR_NO_ORDER", "STR_STOCK_NEWS_ORDER_EXPIRED"]


def find(name):
    """The one file with this name (not case sensitive) in this repository. Stops when there is none or more than one."""
    hits = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.lower() == name.lower():
                hits.append(Path(root) / f)
    if not hits:
        stem = name.split(".")[0].lower()
        similar = [str(Path(r, f).relative_to(ROOT)) for r, d, fs in os.walk(ROOT)
                   if not (set(Path(r).relative_to(ROOT).parts) & SKIP_DIRS) for f in fs if stem[:8] in f.lower()]
        sys.exit(f"ERROR: {name} not found in the repository. Files with a similar name: {similar or 'none'}")
    if len(hits) > 1:
        sys.exit(f"ERROR: {name} exists {len(hits)} times: {[str(h.relative_to(ROOT)) for h in hits]}. Delete the old copy.")
    return hits[0]


def check(tree):
    """Fail when a file of the mod would overwrite a file that OpenTTD (or the patch) already has."""
    if not (tree / "src" / "command_type.h").exists():
        sys.exit(f"ERROR: {tree} does not look like an OpenTTD source tree")
    clashes = [f"{folder}/{name}" for name, folder in FILES.items() if (tree / folder / name).exists()]
    for name in FILES:
        find(name)  # also stops on a missing or duplicated mod file
    if clashes:
        for c in clashes:
            print(f"::error::{c} already exists in OpenTTD (or in the patch); refusing to overwrite it")
        sys.exit(1)
    print(f"check ok: {len(FILES)} mod files, no clash with the OpenTTD tree")


def main(tree):
    for name, folder in FILES.items():
        src = find(name)
        dst = tree / folder / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        print(f"copy {src.relative_to(ROOT)} -> {folder}/{name}")

    # command_type.h
    p = tree / "src" / "command_type.h"
    s = p.read_text(encoding="utf-8")
    m = re.search(r"^([ \t]*)CMD_STOCK_CLOSE,[^\n]*\n", s, re.M)
    if not m:
        sys.exit("ERROR: CMD_STOCK_CLOSE not found in command_type.h - was stock-market.patch applied?")
    indent, pos, added = m.group(1), m.end(), 0
    for name, text in NEW_COMMANDS:
        if re.search(r"^\s*" + name + r",", s, re.M):
            continue
        line = f"{indent}{name},".ljust(40) + f"///< {text}\n"
        s = s[:pos] + line + s[pos:]
        pos += len(line)
        added += 1
    p.write_text(s, encoding="utf-8")
    print(f"command_type.h: {added} commands added")

    # CMakeLists.txt
    p = tree / "src" / "CMakeLists.txt"
    s = p.read_text(encoding="utf-8")
    m = re.search(r"^([ \t]*)stock_gui\.h\n", s, re.M)
    if not m:
        sys.exit("ERROR: stock_gui.h not found in src/CMakeLists.txt - was stock-market.patch applied?")
    missing = [f for f in NEW_SOURCES if not re.search(r"^\s*" + re.escape(f) + r"\s*$", s, re.M)]
    if missing:
        s = s[:m.end()] + "".join(f"{m.group(1)}{f}\n" for f in missing) + s[m.end():]
        p.write_text(s, encoding="utf-8")
    print(f"CMakeLists.txt: {len(missing)} files added")

    # english.txt
    wanted = {}
    for name in STRING_FILES:
        for line in find(name).read_text(encoding="utf-8").replace("\r", "").splitlines():
            if line.startswith("STR_"):
                wanted[line.split()[0].split(":")[0]] = line  # a later file wins
    p = tree / "src" / "lang" / "english.txt"
    s = p.read_text(encoding="utf-8")
    for key in REPLACE_KEYS & wanted.keys():
        # Replace the string of OpenTTD / of the patch; leave it alone when it is already the wanted one (so a second run changes nothing).
        s = re.sub(r"^" + key + r"[ \t]+:(?!" + re.escape(wanted[key].split(":", 1)[1]) + r"\n)[^\n]*\n", "", s, flags=re.M)
    todo = [line for key, line in wanted.items() if not re.search(r"^" + key + r"[ \t]+:", s, re.M)]
    anchor = None
    for a in ANCHORS:
        anchor = re.search(r"^" + a + r"[ \t]+:[^\n]*\n", s, re.M)
        if anchor:
            break
    if not anchor:
        sys.exit("ERROR: no anchor string found in english.txt - was stock-market.patch applied?")
    s = s[:anchor.end()] + "\n".join(todo) + ("\n" if todo else "") + s[anchor.end():]
    p.write_text(s, encoding="utf-8")
    print(f"english.txt: {len(todo)} strings added")
    print("overlay applied")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 1 or not flags <= {"--check"}:
        print(__doc__)
        sys.exit(2)
    target = Path(args[0]).resolve()
    if "--check" in flags:
        check(target)
    else:
        main(target)
