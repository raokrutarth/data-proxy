#!/bin/bash -ex

# Run this script on the cloud machine terminal to make sure the data persistance library works.

# The library gets this (poorly designed) error when trying to initalize sqllite if the file system does not allow it.
# Traceback (most recent call last):
#   File "<string>", line 17, in <module>
#   File "<string>", line 10, in _get_queue_mapper_db_sesh
#   File "/opt/python/3.8.5/lib/python3.8/site-packages/persistqueue/pdict.py", line 22, in __init__
#     super(PDict, self).__init__(path, name=name,
#   File "/opt/python/3.8.5/lib/python3.8/site-packages/persistqueue/sqlbase.py", line 89, in __init__
#     self._init()
#   File "/opt/python/3.8.5/lib/python3.8/site-packages/persistqueue/sqlbase.py", line 101, in _init
#     self._conn = self._new_db_connection(
#   File "/opt/python/3.8.5/lib/python3.8/site-packages/persistqueue/sqlbase.py", line 129, in _new_db_connection
#     conn.execute('PRAGMA journal_mode=WAL;')
# sqlite3.OperationalError: database is locked
# Exception ignored in: <function SQLiteBase.__del__ at 0x7fb9913efaf0>
# Traceback (most recent call last):
#   File "/opt/python/3.8.5/lib/python3.8/site-packages/persistqueue/sqlbase.py", line 202, in __del__
#     self._getter.close()
# AttributeError: 'PDict' object has no attribute '_getter'

python -m pip install persist-queue

python -c '''
import persistqueue
def _get_queue_session() -> persistqueue.SQLiteQueue:

    db_path = "/tmp/sanity-test-queue"

    return persistqueue.SQLiteQueue(
        path=db_path,
        auto_commit=True,
        multithreading=True,
        timeout=10,
    )


q = _get_queue_session()
q.put("lll")
print(q.get())
'''

python -c '''
import persistqueue
def _get_queue_mapper_db_sesh() -> persistqueue.PDict:

    db_path = "/tmp/sanity-test-dict"

    return persistqueue.PDict(
        path=db_path,
        multithreading=True,
    )


p = _get_queue_mapper_db_sesh()
p["oo"] = (42, 99)
print(p["oo"])
'''
