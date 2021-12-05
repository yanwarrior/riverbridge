import sys
from cx_Freeze import setup, Executable
directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|RiverBridge"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "Bridging IoT for RiverSide", "IconId", None),
    ],
    "Icon": [
        ("IconId", "icon.ico"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    "all_users": True,
    "data": msi_data,
    "environment_variables": [
        ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
    ],
    "upgrade_code": "{1513d203-0b76-401a-bb6f-f3f43391924c}",
}

build_exe_options = {
    "packages": [
        "socket", "_thread", "socketio", 
        "PySimpleGUI", "subprocess", "sys",
        "webbrowser", "psgtray", "os", "pystray",
        "tkinter"],
    'include_files': ['icon.ico', 'cloud.png', 'python-3.9.0-amd64.exe',],
    'include_msvcr': True,
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "riverbridge.py",
        copyright="Copyright (C) 2021 RiverSide Technology",
        base=base,
        icon="icon.ico",
        shortcut_name="RiverBridge",
        shortcut_dir="DesktopFolder",
    ),
]

setup(
    name = "RiverBridge",
    version = "0.1",
    description = "Bridging IoT for RiverSide!",
    # options = {"build_exe": build_exe_options},
    executables =executables,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
        
    },
)