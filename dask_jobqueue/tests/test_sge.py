import os
from time import time, sleep

import pytest

from dask.distributed import Client
from distributed.utils_test import loop  # noqa: F401

from dask_jobqueue.sge import SGECluster

pytestmark = pytest.mark.env("sge")


def test_basic(loop):  # noqa: F811
    with SGECluster(walltime='00:02:00', threads=2, memory='7GB',
                    loop=loop) as cluster:
        with Client(cluster) as client:
            workers = cluster.start_workers(2)
            future = client.submit(lambda x: x + 1, 10)
            assert future.result(60) == 11
            assert cluster.jobs

            info = client.scheduler_info()
            w = list(info['workers'].values())[0]
            assert w['memory_limit'] == 7e9
            assert w['ncores'] == 2

            cluster.stop_workers(workers)

            start = time()
            while len(client.scheduler_info()['workers']) > 0:
                sleep(0.100)
                assert time() < start + 10

            assert not cluster.jobs
