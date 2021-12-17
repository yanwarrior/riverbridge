import socket
import _thread
from PySimpleGUI.PySimpleGUI import Tree
import socketio
import PySimpleGUI as sg
import subprocess
import sys
import webbrowser
import psgtray 
import os

sio = socketio.Client()
global_rbui = None


def safe_room_name(n=5):
  room = ''.join(filter(str.isalpha, socket.gethostname()))
  return room


def code_build(code, room, timeout=1):
  try:
    with open(f'{room}.py', 'wb') as f:
      f.write(code.encode(encoding='UTF-8'))
    
    p = subprocess.Popen(f"python {room}.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = '\n'
    for line in p.stdout:
      line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
      output += line
      
      sio.emit("stdout", {"room": room, "content": f"{line}\n"})
    retval = p.wait(timeout)
      # return (retval, output) 
  except Exception as e:
    sio.emit("stdout", {"room": room, "content": f"{e}"})


@sio.event
def connect():
  global global_rbui
  global_rbui.tray.show_icon()
  global_rbui.tray.show_message('River Bridge', "Connect to server successfully!")


@sio.event
def disconnect():
  global global_rbui
  global_rbui.tray.show_message('River Bridge', "Disconnected from server")


@sio.event
def connect_error(data):
  global global_rbui
  global_rbui.tray.show_icon()
  global_rbui.tray.show_message('River Bridge', "Error connection!")
  sys.exit()


@sio.event
def pair_success(data):
  global global_rbui
  global_rbui.tray.show_icon()
  global_rbui.tray.show_message('River Bridge', data['content'])


@sio.event
def run(data):
  global_rbui
  global_rbui.tray.show_icon()
  global_rbui.tray.show_message('River Bridge', "Building code...")
  _thread.start_new_thread( code_build, (data['content'], data['room']) )


def connecting(sio, values, window):
  sio.connect(values[RiverBridgeUI.KEY_HOST_SERVER])
  sio.emit("pair", {
    'room': values[RiverBridgeUI.KEY_ROOM],
    'content': ''
  })
  window.hide()

class RiverBridgeUI:

  KEY_HOST_SERVER = "host_server"
  KEY_ROOM = "room"
  KEY_NGROK = "ngrok"
  DEFAULT_HOST = "https://riverlabs.herokuapp.com"
  BUTTON_CONNECT = 'Connect'
  BUTTON_CLOSE_CONNECT = 'Close Connection'
  BUTTON_INSTALL_PYTHON = 'Install Python'
  ICON_NAME = "icon.ico"

  def __init__(self, sio, title="River Bridge") -> None:
    self.title = title
    self.window = None  
    self.layout = None
    self.room = safe_room_name()
    self.icon = os.path.abspath(RiverBridgeUI.ICON_NAME)
    self.sio = sio
    self.menu = [
      '', 
      [
        'Show', 
        'Open Web Editor',
        'Hide',
        'Exit',
      ]
    ]
    self.tray = None

  def get_sio(self):
    return self.sio

  def set_sio(self, sio):
    self.sio = sio

  def set_window(self):
    sg.theme("black")
    self.window = sg.Window(
      self.title, 
      self.layout, 
      keep_on_top=True,
      background_color='black'
    )

  def set_systemtray(self):
    self.tray = psgtray.SystemTray(
      self.menu, 
      single_click_events=False, 
      window=self.window, 
      tooltip="River Bridge", 
      icon=self.icon
    )

  def get_window(self):
    return self.window

  def set_layout(self):
    self.layout = [
      [
        sg.Image(os.path.abspath("cloud.png"), background_color="black", expand_x=True)
      ],
      [sg.Text("Host Server:", background_color='black', text_color='grey', font='Courier 10 bold')],
      [sg.InputText(
          RiverBridgeUI.DEFAULT_HOST, 
          background_color='black', 
          text_color="pink",
          key=RiverBridgeUI.KEY_HOST_SERVER, 
          # expand_x=True,
          border_width=0,
          font='Courier 10'
        )
      ],
      [sg.Text("Room Name:", background_color='black', text_color='grey', font='Courier 10')],
      [sg.InputText(self.room, key=RiverBridgeUI.KEY_ROOM, 
          background_color='black', 
          text_color="pink",
          border_width=0,
          font='Courier 10'
        )
      ],
      [
        sg.Button(RiverBridgeUI.BUTTON_CONNECT, pad=(5, 10), border_width=0, button_color='blue', expand_x=True),
        sg.Button(RiverBridgeUI.BUTTON_CLOSE_CONNECT, pad=(5, 10), border_width=0, button_color='yellow', expand_x=True),
      ]
    ]

  
  def run(self):
    while True:
      event, values = self.window.read()
      if event == self.tray.key:
        event = values[event]
      
      if event == RiverBridgeUI.BUTTON_CONNECT:
        try:
          _thread.start_new_thread(connecting, (self.sio, values, self.window))
          
        except socketio.exceptions.ConnectionError as e:
          print(e)
      
      if event in ('Show', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
        self.window.un_hide()
        self.window.bring_to_front()

      if event == 'Open Web Editor':
        webbrowser.open(values[RiverBridgeUI.KEY_HOST_SERVER])

      if event == RiverBridgeUI.BUTTON_CLOSE_CONNECT:
        self.sio.disconnect()
      
      if event == sg.WIN_CLOSED or event == 'Cancel':
        self.sio.disconnect()
        break

  def close(self):
    self.tray.close()
    self.window.close()
    sys.exit()


if __name__ == '__main__':
  rbui = RiverBridgeUI(sio)
  global_rbui = rbui
  rbui.set_layout()
  rbui.set_window()
  rbui.set_systemtray()
  rbui.run()
  rbui.close()