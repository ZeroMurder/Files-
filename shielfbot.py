import sqlite3
import hashlib
import socket
import threading
import time
import os
import psutil
from typing import List, Dict, Set
import tkinter as tk
from tkinter import ttk, scrolledtext
import requests

class ShieldBotAntivirus:
    def __init__(self, db_path: str = "shieldbot.db"):
        self.name = "🛡️ ShieldBot Antivirus"
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
        self.threats_db: Set[str] = set()
        self._setup_database()
        self.monitoring_active = False
        
    def _setup_database(self):
        """База известных угроз"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY, hash TEXT UNIQUE, threat_type TEXT, action TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, file_path TEXT, status TEXT)''')
        self.db.commit()
        self._load_threat_signatures()
    
    def _load_threat_signatures(self):
        """Загружаем сигнатуры угроз (DDoS инструменты, ботнеты)"""
        threat_hashes = {
            # Хеши известных вредоносных инструментов
            "d41d8cd98f00b204e9800998ecf8427e": "ddos_tool",  # Пустой файл тест
            "5d41402abc4b2a76b9719d911017c592": "botnet_cnc",
            "your_ddos_script_hash": "ddos_flooder"
        }
        for hash_val, threat_type in threat_hashes.items():
            self.cursor.execute("INSERT OR IGNORE INTO threats (hash, threat_type, action) VALUES (?, ?, ?)",
                              (hash_val, threat_type, "QUARANTINE"))
        self.threats_db.update(threat_hashes.keys())
        self.db.commit()
    
    def chat_interface(self):
        """Чат-интерфейс для управления антивирусом"""
        print(f"{self.name} активирован!")
        while True:
            cmd = input("ShieldBot> ").lower().strip()
            if cmd == "scan":
                self.full_system_scan()
            elif cmd == "network":
                self.network_monitor()
            elif cmd == "realtime":
                self.start_realtime_monitoring()
            elif cmd == "threats":
                self.show_threats()
            elif cmd == "gui":
                self.launch_gui()
            elif cmd in ['exit', 'quit']:
                break
            else:
                print("Команды: scan, network, realtime, threats, gui")
    
    def file_hash(self, file_path: str) -> str:
        """Вычисляем MD5 хеш файла"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def full_system_scan(self):
        """Полное сканирование системы"""
        print("🔍 Запуск полного сканирования...")
        threats_found = 0
        for root, _, files in os.walk("C:/"):  # Windows путь
            for file in files[:50]:  # Лимит для демо
                file_path = os.path.join(root, file)
                file_hash = self.file_hash(file_path)
                if file_hash in self.threats_db:
                    print(f"🛑 УГРОЗА: {file_path} ({file_hash})")
                    self.quarantine_file(file_path)
                    threats_found += 1
        print(f"✅ Сканирование завершено. Найдено угроз: {threats_found}")
    
    def quarantine_file(self, file_path: str):
        """Карантин угрозы"""
        try:
            os.rename(file_path, f"QUARANTINE_{file_path}")
            self.cursor.execute("INSERT INTO scan_history VALUES (NULL, ?, ?, ?)",
                              (time.strftime("%Y-%m-%d %H:%M"), file_path, "QUARANTINED"))
            self.db.commit()
        except Exception as e:
            print(f"Ошибка карантина: {e}")
    
    def network_monitor(self):
        """Мониторинг сети на DDoS паттерны"""
        print("🌐 Сетевой мониторинг...")
        def monitor_connections():
            for conn in psutil.net_connections(kind='inet'):
                if conn.raddr:  # Много исходящих соединений = подозрительно
                    print(f"Подозрительное соединение: {conn.laddr} -> {conn.raddr}")
        
        monitor_connections()
    
    def start_realtime_monitoring(self):
        """Мониторинг в реальном времени"""
        self.monitoring_active = True
        def monitor_loop():
            while self.monitoring_active:
                self.network_monitor()
                time.sleep(5)
        threading.Thread(target=monitor_loop, daemon=True).start()
        print("👀 Реал-тайм мониторинг запущен (Ctrl+C для остановки)")
    
    def show_threats(self):
        """Показать базу угроз"""
        self.cursor.execute("SELECT * FROM threats")
        for threat in self.cursor.fetchall():
            print(f"Угроза: {threat[1]} - {threat[2]} ({threat[3]})")
    
    def launch_gui(self):
        """GUI интерфейс антивируса"""
        root = tk.Tk()
        root.title(self.name)
        root.geometry("800x600")
        
        # Лог панель
        log_text = scrolledtext.ScrolledText(root, height=20)
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Полное сканирование", 
                  command=lambda: self.full_system_scan()).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сетевой мониторинг", 
                  command=self.network_monitor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Реал-тайм", 
                  command=self.start_realtime_monitoring).pack(side=tk.LEFT, padx=5)
        
        root.mainloop()

# Запуск антивируса
if __name__ == "__main__":
    antivirus = ShieldBotAntivirus()
    antivirus.chat_interface()
