"""Cria atalho no Menu Iniciar > Apps Caio > Texto para Voz."""

import os
from win32com.client import Dispatch

base_path = os.path.dirname(os.path.abspath(__file__))

# Pasta destino no Menu Iniciar
programs_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Apps Caio")
os.makedirs(programs_folder, exist_ok=True)

# Criar atalho
shortcut_path = os.path.join(programs_folder, "Texto para Voz.lnk")
pythonw_path = os.path.join(base_path, "venv", "Scripts", "pythonw.exe")
script_path = os.path.join(base_path, "main.py")

shell = Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = pythonw_path
shortcut.Arguments = f'"{script_path}"'
shortcut.WorkingDirectory = base_path
shortcut.IconLocation = pythonw_path
shortcut.save()

print(f"Atalho criado em: {shortcut_path}")
