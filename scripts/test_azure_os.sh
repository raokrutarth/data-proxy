
# run this script on could machine shell to make sure the queue library works.

cd /home/site/wwwroot

python -m pip install persist-queue

python -c '''
import persistqueue
def _get_queue_session() -> persistqueue.SQLiteQueue:
    # Use a file system persisted FIFO queue that uses sqllite internally.
    # TODO check approx memory usage per event and restrict size
    db_path = "/tmp/lll-test-q"
    assert db_path is not None, f"Invalid queue db path: {db_path}"

    return persistqueue.SQLiteQueue(
        path=db_path,
        auto_commit=False,
        multithreading=True,
        timeout=8,  # wait upto 30 sec to acquire a DB lock.
    )


q = _get_queue_session()
q.put("lll")
q.get()
'''

python -c '''
import persistqueue


def _get_queue_mapper_db_sesh() -> persistqueue.PDict:

    db_path = "ppp-test-db"
    assert db_path is not None, f"Invalid queue mapping db path: {db_path}"
    # dict containing queue ID to persist-queue path
    return persistqueue.PDict(
        path=db_path,
        name="/tmp/generic_proxy_queues_mapppings",
        multithreading=True,
    )


p = _get_queue_mapper_db_sesh()
p["oo"] = (42, 99)
'''


# TODO so far; the library gets this error when trying to initalize sqllite in every dir. I.e. unable to write DB file.

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