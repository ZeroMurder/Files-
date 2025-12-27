import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows check
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

# --- Функции для администраторов ---
def change_screen_color_admin(color):
    if color == "normal":
        command = ('powershell.exe -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\ColorFiltering '
                   '-Name Active -Value 0"')
    elif color == "inverted":
        command = ('powershell.exe -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\ColorFiltering '
                   '-Name Active -Value 1; Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\ColorFiltering '
                   '-Name FilterType -Value 2"')
    elif color == "grayscale":
        command = ('powershell.exe -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\ColorFiltering '
                   '-Name Active -Value 1; Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\ColorFiltering '
                   '-Name FilterType -Value 1"')
    else:
        return
    subprocess.run(command, shell=True)

def shutdown_pc_admin():
    subprocess.Popen("shutdown /s /t 5")

def restart_pc_admin():
    subprocess.Popen("shutdown /r /t 5")

# --- Функции для пользователей без админ прав ---
def change_screen_color_user(color):
    messagebox.showinfo("Нет прав", "Смена цветового фильтра требует администраторских прав.\n"
                                   "Откройте настройки 'Цветовые фильтры' вручную.")
    subprocess.Popen("start ms-settings:easeofaccess-colorfilter", shell=True)

def shutdown_pc_user():
    messagebox.showwarning("Нет прав", "Выключение ПК из программы без прав администратора невозможно.\n"
                                      "Вы можете выключить компьютер вручную.")

def restart_pc_user():
    messagebox.showwarning("Нет прав", "Перезагрузка ПК из программы без прав администратора невозможна.\n"
                                      "Вы можете перезагрузить компьютер вручную.")

# --- Общие функции ---
def launch_task_manager():
    subprocess.Popen("taskmgr")

def launch_device_manager():
    subprocess.Popen("devmgmt.msc")

def launch_sound_settings():
    subprocess.Popen("start ms-settings:sound", shell=True)

def open_folders():
    user_folder = os.path.expanduser("~")
    subprocess.Popen(f'explorer "{user_folder}"')

def toggle_night_mode():
    subprocess.Popen("start ms-settings:nightlight", shell=True)

def open_cmd():
    subprocess.Popen("start cmd", shell=True)

def open_powershell():
    subprocess.Popen("start powershell", shell=True)


# --- Интерфейс ---
root = tk.Tk()
root.title("Управление Windows")
root.geometry("600x800")

tk.Label(root, text="Быстрая смена цвета экрана").pack(pady=5)
if is_admin():
    tk.Button(root, text="Обычный", command=lambda: change_screen_color_admin("normal")).pack(fill='x', padx=20)
    tk.Button(root, text="Инвертировать цвета", command=lambda: change_screen_color_admin("inverted")).pack(fill='x', padx=20)
    tk.Button(root, text="Оттенки серого", command=lambda: change_screen_color_admin("grayscale")).pack(fill='x', padx=20)
else:
    tk.Button(root, text="Обычный", command=lambda: change_screen_color_user("normal")).pack(fill='x', padx=20)
    tk.Button(root, text="Инвертировать цвета", command=lambda: change_screen_color_user("inverted")).pack(fill='x', padx=20)
    tk.Button(root, text="Оттенки серого", command=lambda: change_screen_color_user("grayscale")).pack(fill='x', padx=20)

tk.Label(root, text="Диспетчер задач").pack(pady=10)
tk.Button(root, text="Запустить Диспетчер задач", command=launch_task_manager).pack(fill='x', padx=20)

tk.Label(root, text="Управление устройствами").pack(pady=10)
tk.Button(root, text="Открыть Диспетчер устройств", command=launch_device_manager).pack(fill='x', padx=20)

tk.Label(root, text="Управление звуком").pack(pady=10)
tk.Button(root, text="Настройки звука", command=launch_sound_settings).pack(fill='x', padx=20)

tk.Label(root, text="Управление папками").pack(pady=10)
tk.Button(root, text="Открыть папку пользователя", command=open_folders).pack(fill='x', padx=20)

tk.Label(root, text="Выключение/Перезагрузка ПК").pack(pady=10)
if is_admin():
    tk.Button(root, text="Выключить ПК", command=shutdown_pc_admin).pack(fill='x', padx=20)
    tk.Button(root, text="Перезагрузить ПК", command=restart_pc_admin).pack(fill='x', padx=20)
else:
    tk.Button(root, text="Выключить ПК", command=shutdown_pc_user).pack(fill='x', padx=20)
    tk.Button(root, text="Перезагрузить ПК", command=restart_pc_user).pack(fill='x', padx=20)

tk.Label(root, text="Ночной режим").pack(pady=10)
tk.Button(root, text="Настройки ночного режима", command=toggle_night_mode).pack(fill='x', padx=20)

tk.Label(root, text="Открыть консоли").pack(pady=10)
tk.Button(root, text="Открыть CMD", command=open_cmd).pack(fill='x', padx=20)
tk.Button(root, text="Открыть PowerShell", command=open_powershell).pack(fill='x', padx=20)

root.mainloop()
