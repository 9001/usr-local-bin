#!/usr/bin/env python3
# coding: utf-8
from __future__ import print_function, unicode_literals

"""
minimal replacement for the sqlite3 cli
for when youre stuck on a box with python2 and nothing else

2022, ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin
"""


import argparse
import atexit
import json
import os
import platform
import sqlite3
import sys

try:
    from pathlib import Path
except:
    pass

try:
    import readline

    histfile = os.path.join(os.path.expanduser("~"), ".sq3py_history")
    open(histfile, "ab+").close()
    readline.read_history_file(histfile)
    histlen = readline.get_current_history_length()

    def savehist():
        try:
            newhist = readline.get_current_history_length() - histlen
            readline.set_history_length(1000)
            readline.append_history_file(newhist, histfile)
        except:
            readline.write_history_file(histfile)

        try:
            os.system("stty sane")
        except:
            pass

        print()

    atexit.register(savehist)
except Exception as ex:
    print("readline unavailable:", ex)


try:
    readln = raw_input
except:
    readln = input


class C(object):
    def __init__(self, cur, of, sep):
        # type: (sqlite3.Cursor, str) -> None
        self.cur = cur
        self.of = of
        self.sep = sep

    def eval(self, sql):
        lsql = sql.lower()
        try:
            if lsql == "commit":
                self.cur.connection.commit()
                return

            self.cur.execute(sql)
            if lsql[:6] in ["select", "pragma"]:
                self.dump()

            return True

        except sqlite3.Error as ex:
            print("in [{}],\nerror: {}".format(sql, ex.args[0]))
            return False

    def dump(self):
        names = [x[0] for x in self.cur.description]
        if self.of == "list":
            print(self.sep.join(names) + "\n", end="")
            for row in self.cur:
                print(self.sep.join([str(x) for x in row]) + "\n", end="")
            return

        if self.of == "line":
            nw = max(len(max(names, key=len)) if names else 1, 5)
            fmt = "{{:>{}}} = {{!s}}\n".format(nw)
            for row in self.cur:
                t = ""
                for k, v in zip(names, row):
                    t += fmt.format(k, v)
                print(t + "\n", end="")
            return

        if self.of == "json":
            rows = self.cur.fetchall()
            rows = [{k: v for k, v in zip(names, r)} for r in rows]
            print(json.dumps(rows, indent="  "))
            return

        if self.of == "jsonl":
            for row in self.cur:
                t = json.dumps({k: v for k, v in zip(names, row)})
                print(t + "\n", end="")
            return

        while True:
            rows = self.cur.fetchmany(100)
            if not rows:
                break

            self.dump_rows(names, rows)

    def dump_rows(self, names, rows):
        x = [names] + rows
        cws = [
            len(max([str(row[col]) for row in x], key=len))  #
            for col in range(len(names))
        ]

        chrome = []
        if self.of == "box":
            edgesets = [["┌", "┬", "┐"], ["├", "┼", "┤"], ["└", "┴", "┘"]]
            align = "^"
            hbar = "─"
            sep = "│"
        elif self.of == "markdown":
            edgesets = [["|", "-", "|"]]
            align = "^"
            hbar = "-"
            sep = "|"
        elif self.of == "column":
            edgesets = []
            align = "<"
            sep = ""
        else:
            raise NotImplementedError()

        for edges in edgesets:
            t = ""
            lead = edges[0]
            for w in cws:
                t += "{}{}".format(lead, hbar * (w + 2))
                lead = edges[1]
            t += edges[2]
            chrome.append(t)

        t = ""
        csep = " " + sep + " "
        for w, k in zip(cws, names):
            t += "{}{:{al}{sz}}".format(csep, k, al=align, sz=w)
        t = (t + csep).strip()

        if self.of == "box":
            print("\n".join([chrome[0], t, chrome[1]]) + "\n", end="")
        elif self.of == "markdown":
            print("\n".join([t, chrome[0]]) + "\n", end="")
        elif self.of == "column":
            print(t)

        fmt = sep
        for w in cws:
            fmt += " {{:{}}} {}".format(w, sep)

        if self.of == "column":
            fmt = fmt[1:-1] + "\n"
        else:
            fmt += "\n"

        for row in rows:
            print(fmt.format(*["(/)" if x is None else x for x in row]), end="")

        if self.of == "box":
            print(chrome[2] + "\n", end="")


def main():
    ST = "store_true"
    SC = "store_const"

    # fmt: off
    ap = argparse.ArgumentParser()
    ap.add_argument("fn", metavar="FILENAME", nargs="?", default=":memory:")
    ap.add_argument("sql", metavar="SQL", nargs="*", default=None)

    se = ap.add_argument_group("db config")
    se.add_argument("-readonly", action=ST, help="lockfree, crashy")

    se = ap.add_argument_group("output format")
    se.add_argument("-box", const="box", dest="of", action=SC)
    se.add_argument("-column", const="column", dest="of", action=SC)
    se.add_argument("-json", const="json", dest="of", action=SC)
    se.add_argument("-jsonl", const="jsonl", dest="of", action=SC)
    se.add_argument("-line", const="line", dest="of", action=SC)
    se.add_argument("-list", const="list", dest="of", action=SC)
    se.add_argument("-markdown", const="markdown", dest="of", action=SC, help="(default)")

    se = ap.add_argument_group("format modifiers for -list")
    se.add_argument("-separator", default=" | ")

    se = ap.add_argument_group("info")
    se.add_argument("-V", "-version", action=ST)

    # fmt: on
    ar = ap.parse_args()

    if ar.V:
        try:
            cur = sqlite3.connect(":memory:")
            try:
                vs = cur.execute("select * from pragma_compile_options").fetchall()
            except:
                vs = cur.execute("pragma compile_options").fetchall()

            ms = next(x[0] for x in vs if x[0].startswith("THREADSAFE="))
        except:
            ms = "THREADSAFE=?"

        t = "sqlite {} {}\n{} {}\n".format(
            sqlite3.sqlite_version,
            ms,
            platform.python_implementation(),
            ".".join([str(x) for x in sys.version_info]).split(".final.")[0],
        )
        print(t, end="")
        return

    if not ar.of:
        ar.of = "markdown"

    if False:
        ar.of = "box"
        ar.sql = [
            "create table t(qw,er,ty,uiopasdfghjkl);",
            "insert into t values(1,2,3,4);",
            "insert into t values('qaz','wsx','edcrfvtgb','yhnujm');",
            "select * from t;",
        ]

    if ar.readonly:
        uri = "{}?mode=ro&nolock=1".format(Path(ar.fn).as_uri())
        cur = sqlite3.connect(uri, 2, uri=True).cursor()
    else:
        cur = sqlite3.connect(ar.fn, 2).cursor()

    c = C(cur, ar.of, ar.separator)

    if ar.sql:
        for sql in ar.sql:
            if not c.eval(sql):
                return sys.exit(1)
        return

    if not ar.sql and ar.fn == ":memory:":
        print("Connected to a transient in-memory database.")

    buf = ""
    while True:
        try:
            buf += readln("  ...> " if buf else "sq3py> ")
        except EOFError:
            break

        if not sqlite3.complete_statement(buf):
            continue

        c.eval(buf.strip())
        buf = ""

    conn = cur.connection
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
