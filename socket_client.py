import os
import socket
import errno
from threading import Thread



HEADER_LENGTH = 10
client_socket = None
global client_list
client_list = {}
user_names = []
user_passes = []
with open("users.txt", "r") as file:
    user_list = file.read().split(",")
    print("***")
    print(user_list)
    print("***")
    for i in range(len(user_list)):
        if i % 2 == 0:
            user_names.append(user_list[i])
        else:
            user_passes.append(user_list[i])
file.close()

# Savienojuma ar severi izveidošana
def check_user(user_name,user_pass):
    pass_mess = "_"
    if user_name in user_names:
        index =  user_names.index(user_name)
        if user_passes[index] == user_pass:
            pass_mess = "Autorizācija veiksmīga"
        else:
            pass_mess = "Autorizācija nav veiksmīga"

    else:
        pass_mess = "Jauns lietotājs!"
    return (pass_mess)
def connect(ip, port, my_username, my_password, error_callback):

    global client_socket

    # Servera ligzdas izveidošana
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to a given ip and port
        client_socket.connect((ip, port))
    except Exception as e:
        # Connection error
        error_callback('Connection error: {}'.format(str(e)))
        return False
    pass_mess = "_"

    if  my_username in user_names:
        index = user_names.index(my_username)
        if user_passes[index] == my_password:
            pass_mess = "Autorizācija veiksmīga"
        else:
            pass_mess = "Autorizācija nav veiksmīga"

    else:
        pass_mess = "Jauns lietotājs!"



    username = my_username.encode('utf-8')

    p_m = pass_mess.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)
    pass_header = f"{len(p_m):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(pass_header + p_m)

    return True



def send(message):


    message = message.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)


def start_listening(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()

# Listens for incomming messages
def listen(incoming_message_callback, error_callback):
    while True:

        try:

            while True:


                username_header = client_socket.recv(HEADER_LENGTH)

                # Savienojums tiek slegts, gadijuma, ja nav sanemti dati:
                if not len(username_header):
                    error_callback('Connection closed by the server')


                username_length = int(username_header.decode('utf-8').strip())


                username = client_socket.recv(username_length).decode('utf-8')


                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                incoming_message_callback(username, message)

        except Exception as e:

            error_callback('Kļūda: {}'.format(str(e)))