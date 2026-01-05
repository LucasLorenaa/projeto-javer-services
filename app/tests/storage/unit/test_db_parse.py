import os
from storage import db


def test_parse_jdbc_to_sqlite_path_mem_and_file():
    p = db._parse_jdbc_to_sqlite_path("jdbc:h2:mem:abc;DB_CLOSE_DELAY=-1")
    assert isinstance(p, str) and p.startswith("file:")

    p2 = db._parse_jdbc_to_sqlite_path("jdbc:h2:/srv/data/javer.db;AUTO_SERVER=TRUE")
    assert p2.endswith("/srv/data/javer.db.sqlite") or p2.endswith("\\srv\\data\\javer.db.sqlite")

    # relative path should be joined with cwd
    p3 = db._parse_jdbc_to_sqlite_path("jdbc:h2:relative/path/javer.db;AUTO_SERVER=TRUE")
    assert p3.startswith("file:") or str(os.getcwd()) in p3

    # windows drive style path
    p4 = db._parse_jdbc_to_sqlite_path(r"jdbc:h2:C:\\data\\javer.db;AUTO_SERVER=TRUE")
    assert p4.endswith(".sqlite") and ("C:" in p4 or "\\" in p4 or "/" in p4)

    p3 = db._parse_jdbc_to_sqlite_path("notajdbc:whatever")
    assert p3 is None
