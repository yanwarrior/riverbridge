try:
  import socketio
  import PySimpleGUI as sg
  import psgtray
  print("package already checked", flush=True)
except Exception as e:
  import os
  os.system('pip install "python-socketio[client]"')
  os.system('pip install PySimpleGUI')
  os.system('pip install psgtray')