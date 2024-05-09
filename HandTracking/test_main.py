import cv2
import numpy as np
import pytest
import socket
import math
from main import alter_distance_value, create_socket_connection, alter_latency, alter_precision, alter_distance_value, draw_hexagon, get_distance_between_fingers

@pytest.fixture
def setup_socket(monkeypatch):
    class MockSocket:
        def __init__(self, family, type):
            self.family = family
            self.type = type
            self.connected = False
        def connect(self, addr):
            if addr == ("127.0.0.1", 8080):
                self.connected = True
            else:
                raise ConnectionError("Failed to connect")
        def close(self):
            self.connected = False

    monkeypatch.setattr(socket, 'socket', MockSocket)

def test_create_socket_connection_success(setup_socket):
    client_socket = create_socket_connection("127.0.0.1", 8080)
    assert client_socket.connected

def test_create_socket_connection_failure(setup_socket):
    with pytest.raises(ConnectionError):
        create_socket_connection("unknown_host", 1234)

def test_alter_latency():
    alter_latency(3)
    from main import artificial_latency
    assert artificial_latency == 90

def test_alter_precision():
    alter_precision(4)
    from main import precision_factor
    assert precision_factor == 0.60

def test_alter_distance_values():
    distance = 1.0
    precision_factor = 0.15
    alteredDistance = distance + alter_distance_value(distance, precision_factor)
    assert 0.85 <= alteredDistance <= 1.15


def test_draw_hexagon():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    center = (50, 50)
    size = 10
    color = (255, 0, 0) 
    thickness = 2
    alpha = 0.5

    draw_hexagon(img, center, size, color, thickness, alpha)

    assert np.any(img != 0), "The hexagon drawing should modify the image."

class MockLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def test_get_distance_between_fingers():
    index_finger_tip = MockLandmark(1, 1, 1)
    thumb_tip = MockLandmark(4, 5, 1)
    expected_distance = math.sqrt((3 ** 2) + (4 ** 2))
    actual_distance = get_distance_between_fingers(index_finger_tip, thumb_tip)
    assert actual_distance == expected_distance

pytest.main()
