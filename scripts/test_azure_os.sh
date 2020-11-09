
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


