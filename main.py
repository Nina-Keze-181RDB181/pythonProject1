import os
import sys

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import socket_client
# Minimāla freimvorka versija, kas nepieciešama lietotnes palaišanai
kivy.require("1.10.1")
pass_mess = ""
#loga ar ritjoslu (scrollbar) izveidošana
class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)
        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()
        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)
    # Jauno ziņojumu atspoguļošana
    def update_chat_history(self, message):
        self.chat_history.text += '\n' + message
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)
        self.scroll_to(self.scroll_to_point)
    # Interfeisa izskata pielagošana jauniem ziņojumiem
    def update_chat_history_layout(self, _=None):
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

# Pieslēgšanas loga izveidošana
class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        #Fila ar iepriekšēja piesleguma informāciju pieejamības pārbaude
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                # Dati failā glabājas formatā "ip,ports,lietotāja_vārds,lietotāja_parole"
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
                prev_password = d[3]
        # Gadījumā, ja fails netiek atrasts, parametru vērtības ir tuksas rindas
        # Tos lietotājs aizvieto ar manuali ievaditiem datiem
        else:
            prev_ip = ""
            prev_port = ""
            prev_username = ""
            prev_password = ""
        # Lietotājs ievada IP adresi, porta numuru, liatotāja vārdu un paroli
        self.add_widget(Label(text="IP adrese"))
        self.ip = TextInput(text=prev_ip, multiline=False)
        self.add_widget(self.ip)
        self.add_widget(Label(text="Pieslēgšanas ports"))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)
        self.add_widget(Label(text="Lietotāja vārds"))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text="Parole"))
        self.password = TextInput(text=prev_password, multiline=False)
        self.add_widget(self.password)
        # Izvēles rutiņa reģīstrācijai
        # Gadījumā, jā rutiņa ir atzīmēta, tiek pārbaudīts, vai lietotājs ar doto vārdu ir reģistrēts sistēmā
        # Jā tas tā nav, sistēma tiek reģistrēts jaunais lietotājs
        # Jā tas tā ir, tiek izvadīts paziņojums par to, kā lieotājs ar doto vārdu jau eksistē
        # Ja rutiņa nav atzīmēta, arī tiek pārbaudīts, vai lietotājs ar doto vārdu ir reģistrēts sistēmā
        # Jā tas tā nav, tiek izvadīts paziņojums par vienraizeju pieslēgšanu
        # Jā tas tā ir, bet parole nav pareiza, tiek izvadits paziņojums par to
        # Jā tas tā ir, un parole ir pareiza, tiek izvadits paziņojums par veiksmigu autentifikāciju
        self.add_widget(Label(text='Reģistrācija'))
        self.checkbox = CheckBox(active=True)
        self.add_widget(self.checkbox)
        self.join = Button(text="Pievienoties")
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())
        self.add_widget(self.join)
    # Jaunā lietotāja reģistrācija
    def add_user(self):
        print("Adding...")
        username = self.username.text
        password = self.password.text

        with open("users.txt", "a+") as file:
            file.write(f"{username},{password},")
        file.close()

    # Pieslēguma izveidošans meģinājums

    def join_button(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text
        password = self.password.text
        if self.checkbox.active:
            self.add_user()

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username},{password}")

        info = f"Attempting to join{ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        username = self.username.text
        password = self.password.text
        pass_mess = socket_client.check_user(username,password)


        chat_app.info_page.update_info2(pass_mess)
        chat_app.screen_manager.current = "Info"
        Clock.schedule_once(self.connect, 1)
    # Pieslēgšana. Lietotāja autentifikācijas meģinājums

    def connect(self, _):
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text
        password = self.password.text

        if not socket_client.connect(ip, port, username, password, show_error):
            return
        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"

# Lapas ar informāciju par veiksmīgu savienojumu vai savienojuma kļūdu izvade
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.message = Label(halign="center", valign="middle", font_size=30)
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

        self.info2 = Label(text=pass_mess)
        self.add_widget(self.info2)



    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)
    def update_info(self, message):
        self.message.text = message

    def update_info2(self, message):


        self.info2.text = message
# čata lapa izveidošana
class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.rows = 3
        self.history = ScrollableLabel(height=Window.size[1] * 0.9, size_hint_y=None)
        self.add_widget(self.history)

        self.new_message = TextInput(width=Window.size[0] * 0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Nosūtīt")
        self.send.bind(on_press=self.send_message)

        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)



        self.add_widget(bottom_line)

        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_once(self.focus_text_input, 1)
        socket_client.start_listening(self.incoming_message, show_error)
        self.bind(size=self.adjust_fields)

    def adjust_fields(self, *_):

        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.9
        self.history.height = new_height

        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width


        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:
            self.send_message(None)

    def send_message(self, _):
        message = self.new_message.text
        self.new_message.text = ""
        if message:
            self.history.update_chat_history(f"[color=dd2020]{chat_app.connect_page.username.text}[/color] > {message}")
            socket_client.send(message)
        Clock.schedule_once(self.focus_text_input, 0.1)

    def focus_text_input(self, _):
        self.new_message.focus = True
    #Ienakoša ziņojuma apstrāde
    def incoming_message(self, username, message):
        self.history.update_chat_history(f"[color=20dd20]{username}[/color] > {message}")


class StudyApp(App):
    #  Sākuma lapas ar pieslēguma informāciju izveidošana
    def build(self):
        self.screen_manager = ScreenManager()
        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)
        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)
        return self.screen_manager
    # Čata lapas izveidošana
    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name="Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)

#Informācijas par savienojuma pārtraukšanu vai savienojuma kļūdām izvade
def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = StudyApp()
    chat_app.run()
