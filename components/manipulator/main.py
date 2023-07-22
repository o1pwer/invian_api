import socket


def start_server():
    # Создадим сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Установим нашему сокету айпишник и порт
    server_address = ('localhost', 55555)
    print(f"I am a manipulator and i'm starting up on {server_address[0]} port {server_address[1]}")
    server_socket.bind(server_address)

    # Прослушиваем входящие соединения
    server_socket.listen(1)

    while True:
        # Ждем подключения контроллера
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()

        try:
            print(f"Connection from {client_address}")

            # Получаем данные частями и обрабатываем их
            data = ""
            while True:
                chunk = client_socket.recv(16)
                data += chunk.decode()
                if "\n" in data:
                    break

            print(f"Received: {data}")

        finally:
            # Закроем сокет. Можно использовать контекстный менеджер, но пока пусть так будет
            client_socket.close()
            print(f"Closed connection with {client_address}")

if __name__ == '__main__':
    start_server()
