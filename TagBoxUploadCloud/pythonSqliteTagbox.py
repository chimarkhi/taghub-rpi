#!/usr/bin/env python

import sqlite3

conn=sqlite3.connect('temphumidity.db')

curs=conn.cursor()

print "\nEntire database contents:\n"
for row in curs.execute("SELECT * FROM coldtag"):
    print row

conn.close()
