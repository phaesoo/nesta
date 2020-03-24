import time
from nesta.server.define import define


def test_server(control):
    # send stop command and check status
    resp = control.execute(command="server", argv=["stop"])
    assert resp.exitcode == 0

    time.sleep(0.5)

    resp = control.execute(command="server", argv=["status"])
    assert resp.exitcode == 0
    assert resp.data == define.STATUS_STOPPED

    # send resume command and check status
    resp = control.execute(command="server", argv=["resume"])
    assert resp.exitcode == 0

    time.sleep(0.5)

    resp = control.execute(command="server", argv=["status"])
    assert resp.exitcode == 0
    assert resp.data == define.STATUS_RUNNING
    