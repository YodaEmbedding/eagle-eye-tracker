import socket

import pytest
from pytest import approx

from rpi.client import CommClient

class MockSocket:
    def __init__(self):
        self.msg = ""

    def connect(self, *args):
        pass

    def recv(self, *args):
        return self.msg.encode()

def test_commclient(monkeypatch):
    monkeypatch.setattr(socket, 'socket', lambda *args: MockSocket())
    client = CommClient()

    client.sock.msg = "(0,0,0)"
    client.recv_msg()
    assert client.latest_prob     == approx(0.0)
    assert client.latest_coord[0] == approx(0.0)
    assert client.latest_coord[1] == approx(0.0)

    client.sock.msg = "(0.1, -0.123, -0.5813)"
    client.recv_msg()
    assert client.latest_prob     == approx(0.1)
    assert client.latest_coord[0] == approx(-0.123)
    assert client.latest_coord[1] == approx(-0.5813)
