import os
import shutil
import socket
import tempfile
import datetime
from unittest.mock import patch

import pytest


CICD = 'CI' in os.environ \
    and os.environ['CI'] \
    and 'GITHUB_RUN_ID' in os.environ


@pytest.fixture
def cicd():
    return CICD


@pytest.fixture
def mockupfs():
    temp_directories = []

    def create_nodes(root, **kw):
        for k, v in kw.items():
            name = os.path.join(root, k)

            if isinstance(v, dict):
                os.mkdir(name)
                create_nodes(name, **v)
                continue

            if hasattr(v, 'read'):
                f = v
                v = f.read()
                f.close()

            with open(name, 'w') as f:
                f.write(v)

    def _make_temp_directory(**kw):
        """Structure example: {'a.html': 'Hello', 'b': {}}."""
        root = tempfile.mkdtemp()
        temp_directories.append(root)
        create_nodes(root, **kw)
        return root

    yield _make_temp_directory

    for d in temp_directories:
        shutil.rmtree(d)


@pytest.fixture
def freshdb(cicd):
    """ Creates a fresh database for each test.

    Default configuration is using peer authentication method on
    Postgresql's Unix Domain Socket.
    """
    from yhttp.ext.dbmanager import PostgresqlManager

    host = os.environ.get('YHTTP_DB_DEFAULT_HOST', 'localhost' if cicd else '')
    user = os.environ.get('YHTTP_DB_DEFAULT_USER', 'postgres' if cicd else '')
    pass_ = os.environ.get('YHTTP_DB_DEFAULT_PASS', 'postgres' if cicd else '')

    dbname = f'freshdb_{datetime.datetime.now():%Y%m%d%H%M%S}'
    dbmanager = PostgresqlManager(host, 'postgres', user, pass_)
    dbmanager.create(dbname, dropifexists=True)
    freshurl = f'postgresql://{user}:{pass_}@{host}/{dbname}'
    yield freshurl
    dbmanager.dropifexists(dbname)


@pytest.fixture
def freetcpport():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', 0))
        return s.getsockname()[1]
    finally:
        s.close()


@pytest.fixture
def redis():

    class RedisMock:
        def __init__(self, **kw):
            self.info = kw
            self.maindict = dict()

        def flushdb(self):
            self.maindict.clear()

        def srem(self, key, member):
            set_ = self.maindict.setdefault(key, set())
            if member in set_:
                set_.remove(member)

        def sadd(self, key, member):
            set_ = self.maindict.setdefault(key, set())
            set_.add(member)

        def sismember(self, key, member):
            if key not in self.maindict:
                return False

            return member in self.maindict[key]

        def get(self, key):
            return self.maindict.get(key, '').encode()

        def set(self, key, value):
            self.maindict[key] = value

        def setnx(self, key: str, value):
            if not self.maindict.get(key):
                self.set(key, value)
                return 1
            return 0

        def hset(self, key, field, value):
            hashtable = self.maindict.setdefault(key, {})
            hashtable[field] = value

        def hget(self, key, field, value):
            hashtable = self.maindict.setdefault(key, {})
            return hashtable[field]

        def close(self):
            # Do nothing here, this methog is needed for just compatibiliy.
            pass

    with patch('redis.Redis', new=RedisMock) as p:
        yield p
