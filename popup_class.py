

import tkinter
from tkinter import messagebox, Button, Tk, mainloop, Label, \
    StringVar, simpledialog, ttk as TKK
import socket


class PopUp:
    def __init__(self):
        self.port = 5555
        self.ip = socket.gethostbyname(socket.gethostname())
        self.host = False
        self.root = Tk()
        self.width = 700
        self.height = 600

        self.root.title('Multiplayer')
        self.root.geometry('250x160')

        self.ip_var = StringVar()
        self.ip_var.set(f"IP: {socket.gethostbyname(socket.gethostname())}")

        self.port_var = StringVar()
        self.port_var.set(f'port: {self.port}')

        self.lbl2 = Label(master=self.root, textvariable=self.ip_var)
        self.lbl2.grid(row=1, column=0)
        self.lbl3 = Label(master=self.root, textvariable=self.port_var)
        self.lbl3.grid(row=0, column=0)

        self.port_button = Button(text='Change Port',
                                  command=lambda:
                                  self.change_port(self.port_var),
                                  width=15,
                                  height=1)
        self.port_button.grid(row=0, column=1)

        self.ip_button = Button(text='Change IP',
                                command=lambda:
                                self.change_ip(self.ip_var),
                                width=15,
                                height=1)
        self.ip_button.grid(row=1, column=1)

        self.launch_button = Button(text='Host Game',
                                    command=lambda: self.host_fn(),
                                    width=15,
                                    height=1)
        self.launch_button.grid(row=2, column=1)

        self.launch_button = Button(text='Connect',
                                    command=lambda:
                                    self.root.destroy(),
                                    width=15,
                                    height=1)
        self.launch_button.grid(row=4, column=1)

        # self.gamemode_dropdown = TKK.Combobox(state='readonly',
        #                                       values=['single player', 'multiplayer'],
        #                                       width=15)
        # self.gamemode_dropdown.set('single player')
        # self.gamemode_dropdown.grid(row=5, column=1)

    def change_port(self, port_var: tkinter.StringVar) -> None:
        """
        update port variable and port number
        :param port_var: port string variable
        :return:
        """
        port = simpledialog.askinteger("Input", "Enter Port Number",
                                       parent=self.root,
                                       minvalue=0,
                                       maxvalue=10000,
                                       initialvalue=self.port)
        if port:
            self.port = port
            port_var.set(f'port: {self.port}')

    def change_ip(self, ip_var: tkinter.StringVar) -> None:
        """
        update IP variable and ip number
        :param ip_var: port string variable
        :return:
        """
        ip = simpledialog.askstring("Input", "Enter IP Address", parent=self.root,
                                    initialvalue=self.ip)
        if ip:
            self.ip = ip
            ip_var.set(f'IP: {self.ip}')

    def host_fn(self) -> None:
        """
        update IP variable and ip number
        :param name_var: player name
        :return:
        """
        self.host = True
        self.root.destroy()

    def main(self) -> tuple[bool, str, int]:
        """
        app main loop
        :return:
        """

        mainloop()
        return self.host, self.ip, self.port