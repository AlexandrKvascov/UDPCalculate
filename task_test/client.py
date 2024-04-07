import socket
import json
import struct

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


new_line = ''
msg = True
answer = False
while True:
    if msg:
        print("Калькулятор для использования введите выражение в виде \n x+y \n Достпуные операторы:\n '*' - умножение \n '+' - сложение \n '-'- вычитание \n '/' - деление \n Дополнительные операторы:\n 'close' - выключить калькуляторы\n 'c'(eng) - очистить значения\n 'h' - настройки")
    msg = False
    answer = False
    stroka = input("Ввод: ")
    if stroka.lower() == 'close':
        break
    elif stroka.lower() == 'c':
        stroka = 'clear'
        answer = True
  
    elif stroka.lower() == 'h':
        print("Достпуные операторы:\n '*' - умножение \n '+' - сложение \n '-'- вычитание \n '/' - деление \n Дополнительные операторы:\n 'close' - выключить калькуляторы\n 'c'(eng) - очистить значения\n 'h' - настройки\n Для того чтобы рабоать с предыдщем ответом, просто не пишите первый операнд то есть '*y'")
        answer = True

    
    # Преобразование в JSON и отправка на сервер
    location_data = stroka
    json_data = json.dumps(location_data)
    data_size = min(len(json_data), 1000) + 8
    json_data = json_data[:1000]
    header = struct.pack('!2sII', b'EE', 1, data_size)
    message = header + json_data.encode('utf-8')
    client_socket.sendto(message, (UDP_IP, UDP_PORT))
    # Получение ответа от сервера и вывод в консоль
    data, addr = client_socket.recvfrom(1024)
    data = data.decode('utf-8')
    if answer:
        print(f"Ответ : {data}") 
    else:
        print(f"Ответ: {stroka} = {data}")
        

