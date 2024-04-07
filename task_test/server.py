import socket
import struct
import threading
from queue import PriorityQueue
UDP_IP = "127.0.0.1"
UDP_PORT = 5005


# Словарь для хранения предыдущих ответов клиентов
client_responses = {}
queue = PriorityQueue()
queue_lock = threading.Lock()

def multiplication(numbers):
    return numbers[0] * numbers[1]

def subtraction(numbers):
    return numbers[0] - numbers[1]

def division(numbers):
    try:
        num = numbers[0] / numbers[1]
        if num % 1 == 0:  # Если результат деления - целое число (остаток от деления равен 0)
            num = int(num)  # Преобразовать к целому числу
    except ZeroDivisionError:
        num = 'Нельзя делить на 0'
    return num


def addition(numbers):
    return sum(numbers)




def find_numbers(line, sign):
    numbers = line.split(sign)
    if number_memory is not None and numbers[0] == '"':
        numbers[0] = number_memory
    
    numbers = [num.strip('"') for num in numbers]
    try:
        numbers = [num.replace(',', '.') if ',' in num else num for num in numbers]

        return [float(num) if '.' in num else int(num) for num in numbers]
    except ValueError: 
        return 'Error'



def cache(func):
    cache_dict = {}
    
    def wrapper(args):
    
        operators = ['+', '-', '/', '*']
        argst = [arg.strip('"') for arg in args]
        
        if argst[1] in operators:
            return func(args)

        key = hash(args)
        
        if key in cache_dict:
            return cache_dict[key]
        
        # Если результат не найден, вызываем функцию и кэшируем результат
        result = func(args)
        cache_dict[key] = result
        return result
    
    return wrapper



operators = {'*': multiplication, '-': subtraction, '/': division, '+': addition}
@cache
def check_string(equile):
    for operator,func in operators.items():
        if operator in equile:
            numbers = find_numbers(equile, operator)
            if numbers == 'Error':
                return "Ошибка записи"
            return func(numbers)
    return "Ошибка записи"





def packet_get(server_socket):
    while True:
        data, addr = server_socket.recvfrom(1024)
        header = data[:10]
        _,_, data_size = struct.unpack('!2sII', header)
        message_data = data[10:]
        message_data = message_data.decode('utf-8')
        priority = 1 if data_size >= 15 else 2
      
        with queue_lock:  # Захватываем блокировку для изменения очереди
            queue.put((priority, message_data, addr))  # Добавляем элемент в очередь



def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((UDP_IP, UDP_PORT))
    print("UDP server started")
    try:
        global number_memory
        number_memory = None
        threading.Thread(target=packet_get, args=(server_socket,), daemon=True).start()
        while True:
            with queue_lock:  # Захватываем блокировку для доступа к очереди
                if not queue.empty():  # Проверяем, пуста ли очередь
                    _, message_data, addr = queue.get()
                      # Извлекаем элемент из очереди
                else: 
                    continue  # Переходим к следующей итерации цикла
                
                # Попытка декодирования JSON-данных
                try:
                    if message_data == '"clear"':
                        response_data = "clear"
                        client_responses.clear()
                        number_memory = None
                    elif message_data == '"h"':
                        response_data = "help"
                    else:

                    # Получение предыдущего ответа клиента, если есть
                        previous_response = client_responses.get(addr)
                        # Если предыдущий ответ есть, добавляем его в строку запроса
                        if previous_response is not None:
                             number_memory = str(previous_response)

                        # Обработка запроса
                        response_data = check_string(message_data)
                        try:
                            if response_data % 1 == 0:
                                response_data = int(response_data)
                        # Сохранение текущего ответа в словаре
                            client_responses[addr] = response_data
                        except TypeError:
                            response_data = response_data

                        print(f"Received message: {message_data}")
                        
                    # Отправка ответа клиенту
                    server_socket.sendto(str(response_data).encode('utf-8'), addr)

                except TypeError as e:
                    print("Received invalid JSON data", e)

    except KeyboardInterrupt:
        print("Server stopped by user") 
    finally:
        
        server_socket.close()

if __name__ == "__main__":
    main()