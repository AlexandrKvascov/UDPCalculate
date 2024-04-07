import socket
import pytest
import json
import struct
# Функция для отправки запроса на сервер и получения ответа

def send_request(request):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    location_data = request
    json_data = json.dumps(location_data)
    data_size = min(len(json_data), 1000) + 8
    json_data = json_data[:1000]
    header = struct.pack('!2sII', b'EE', 1, data_size)
    request = header + json_data.encode('utf-8')
    client_socket.sendto(request, (UDP_IP, UDP_PORT))
    response, addr = client_socket.recvfrom(1024)
   
    return response.decode('utf-8')

# Пример тестовых функций

def test_multiplication():
    response = send_request('8*6')
    assert response == '48'

def test_subtraction():
    response = send_request("12-4")
    assert response == "8"

def test_clear():
    send_request("8*6")
    send_request("12-4")
    send_request('"clear"')
    response = send_request("57-5")
    assert response == "52"



def test_overwrite():
    response = send_request("52*x")
    assert response == "Ошибка записи"
    response = send_request("y*x")
    assert response == "Ошибка записи"
    response = send_request("y*65465")
    assert response == "Ошибка записи"


def test_priority():
    response1 = send_request("10+20") 
    response2 = send_request("5*5")
    response3 = send_request("30-15")
    assert response2 == '25'  
    assert response1 == '30'  
    assert response3 == '15'  



def test_division():
    response = send_request("10/2")
    assert response == "5"
    response = send_request("10/4")
    assert response == "2.5"

    response = send_request("10/0")
    assert response == "Нельзя делить на 0"


def test_full():
    response = send_request("50+2")
    response = send_request("50+2")
    
    assert response == "52"
    response = send_request("clear")
    assert response == "clear"

    response = send_request("+9")
    assert response ==  "Ошибка записи"
    response = send_request("h")
    assert response == "help"
