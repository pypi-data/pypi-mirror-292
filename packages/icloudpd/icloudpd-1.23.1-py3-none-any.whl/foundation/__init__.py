import datetime
from typing import NamedTuple

import pytz
from tzlocal import get_localzone


class VersionInfo(NamedTuple):
    version: str
    commit_sha: str
    commit_timestamp: int


# will be updated by CI
version_info = VersionInfo(
    version="1.23.1",
    commit_sha="3593ed8",
    commit_timestamp=1724387456,
)


def version_info_formatted() -> str:
    vi = version_info
    ts = datetime.datetime.fromtimestamp(vi.commit_timestamp, tz=pytz.utc).astimezone(
        get_localzone()
    )
    return f"version:{vi.version}, commit sha:{vi.commit_sha}, commit timestamp:{ts:%c %Z}"
