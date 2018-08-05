import pytest
from pytest import approx

import rpi.client
from rpi.commcomm import CommComm

class MockClient:
    def __init__(self):
        self.msg = ""

    def recv_msg(self):
        return self.msg

def test_commcomm(monkeypatch):
    # monkeypatch.patch.object(rpi.client.CommClient, MockClient)
    comm_comm = CommComm(MockClient())

    comm_comm.comm.msg = "(0,0,0)"
    comm_comm.run()
    assert comm_comm.latest_prob     == approx(0.0)
    assert comm_comm.latest_coord[0] == approx(0.0)
    assert comm_comm.latest_coord[1] == approx(0.0)

    comm_comm.comm.msg = "(0.1, -0.123, -0.5813)"
    comm_comm.run()
    assert comm_comm.latest_prob     == approx(0.1)
    assert comm_comm.latest_coord[0] == approx(-0.123)
    assert comm_comm.latest_coord[1] == approx(-0.5813)
