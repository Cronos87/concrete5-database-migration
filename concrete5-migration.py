#!/usr/bin/env python

import sys
import pymysql


MYSQL_DUMP = False

if '--dump-sql' in sys.argv:
    MYSQL_DUMP = True

# Database in dev
DB1_HOST = "127.0.0.1"
DB1_USERNAME = "root"
DB1_PASSSWORD = ""
DB1_DATABASE = "concrete5_db1"

# Database to upgrade
DB2_HOST = "127.0.0.1"
DB2_USERNAME = "root"
DB2_PASSSWORD = ""
DB2_DATABASE = "concrete5_db2"

# Databases connections
conn_db1 = pymysql.connect(
    host=DB1_HOST,
    user=DB1_USERNAME,
    passwd=DB1_PASSSWORD,
    port=3306,
    db=DB1_DATABASE)

conn_db2 = pymysql.connect(
    host=DB2_HOST,
    user=DB2_USERNAME,
    passwd=DB2_PASSSWORD,
    port=3306,
    db=DB2_DATABASE)

# Queries
QUERY_SHOW_TABLES = "show tables"

QUERY_DESCRIBE = "DESCRIBE %s"

QUERY_CREATE_TABLE = "SHOW CREATE TABLE %s"

QUERY_ALTER_TABLE = "ALTER TABLE contacts ADD %s"

db1_cur = conn_db1.cursor()
db2_cur = conn_db2.cursor()

db1_cur.execute(QUERY_SHOW_TABLES)
db1_tables = {table[0] for table in db1_cur.fetchall()}

db2_cur.execute(QUERY_SHOW_TABLES)
db2_tables = {table[0] for table in db2_cur.fetchall()}

databases_tables_diff = db1_tables - db2_tables

# Check and print if the number of tables is not the equal
if len(databases_tables_diff) > 0:
    if MYSQL_DUMP is False:
        if len(db1_tables) > len(db2_tables):
            print("Database1 are more tables than Database2")
        else:
            print("Database2 are more tables than Database1")

    # Print all tables which doesn't exist
    for table in databases_tables_diff:
        if MYSQL_DUMP is False:
            print(' - %s' % table)
        else:
            db1_cur.execute(QUERY_CREATE_TABLE % table)
            print('%s;' % db1_cur.fetchone()[1])

    print()

# Now we compare all tables and its fields
for table in db1_tables:
    if not table in db2_tables:
        continue

    db1_cur.execute(QUERY_DESCRIBE % table)
    db1_fields = {field[0] for field in db1_cur.fetchall()}

    db2_cur.execute(QUERY_DESCRIBE % table)
    db2_fields = {field[0] for field in db2_cur.fetchall()}
    
    table_fields_diff = db1_fields - db2_fields
    
    if len(table_fields_diff) > 0:
        if MYSQL_DUMP is False:
            print('Table %s has more fields' % table)

            for field in table_fields_diff:
                print(' - %s' % field)
        else:
            db1_cur.execute(QUERY_CREATE_TABLE % table)
            table_structure = db1_cur.fetchone()[1].split("\n")

            for field in table_fields_diff:
                for line in table_structure:
                    if line.lstrip().startswith('`%s`' % field):
                        print(QUERY_ALTER_TABLE % line.strip()[:-1] + ';')
