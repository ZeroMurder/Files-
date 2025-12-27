import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import json
import os
import threading
import pyttsx3
import cv2
import numpy as np
from PIL import Image, ImageTk
import pyaudio
import wave
import vosk
import nltk
from nltk.tokenize import word_tokenize
from rapidfuzz import fuzz, process
import random
import sqlite3
import math
import re
from datetime import datetime
import difflib

class AdvancedMDBot:
    def __init__(self):
        self.init_emotions()
        self.init_databases()
        self.init_sqlite()
        # безопасная инициализация Vosk
        try:
            self.model = vosk.Model("models/vosk-model-small-ru-0.22")
        except Exception as e:
            print("Vosk не инициализировался:", e)
            self.model = None
        self.engine = self.init_voice()
        self.memory_context = []
    
    def init_emotions(self):
        self.emotions = {
            "love": 0, "fear": 0, "happy": 50, "irritation": 0,
            "surprise": 0, "sad": 0, "anger": 0, "curiosity": 20,
            "confidence": 30, "shyness": 10
        }
        self.emotion_history = []
        
    def init_databases(self):
        self.knowledge_bases = {
            "code": self.load_code_db(),
            "math": self.load_math_db(),
            "games": self.load_games_db(),
            "hacking": self.load_hacking_db(),
            "general": self.load_general_db()
        }
        
    def init_sqlite(self):
        self.conn = sqlite3.connect('md_bot_memory.db')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS memory 
                             (id INTEGER PRIMARY KEY, user_text TEXT, bot_response TEXT, 
                              timestamp TEXT, score REAL, category TEXT)''')
        self.conn.commit()
        
    def init_voice(self):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'russian' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.setProperty('rate', 160)
            return engine
        except:
            return None
    
    def load_code_db(self):
        return {
            "функция": "def my_func(x):\n    return x * 2",
            "класс": "class Drone:\n    def __init__(self, name):\n        self.name = name",
            "калькулятор": "def calc(a, b, op):\n    if op == '+': return a+b\n    if op == '-': return a-b",
            "json": "import json\ndata = json.load(open('file.json'))",
            "tkinter": "import tkinter as tk\nroot = tk.Tk()\nroot.mainloop()"
        }
    
    def load_math_db(self):
        return {
            "факториал": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
            "степень": "def power(base, exp):\n    return base ** exp",
            "корень": "import math\nmath.sqrt(x)"
        }
    
    def load_games_db(self):
        return {"pygame": "import pygame\npygame.init()\nscreen = pygame.display.set_mode((800,600))"}
    
    def load_hacking_db(self):
        return {"hash": "import hashlib\nhashlib.sha256('text'.encode()).hexdigest()"}
    
    def load_general_db(self):
        return {"привет": "Хайка, хозяин! 💜 Что делаем?", "спасибо": "Плизка! 😊 Люблю помогать!"}
    
    def learn_from_dialog(self, user_text, bot_response, score):
        """Реальное обучение"""
        try:
            self.conn.execute("INSERT INTO memory (user_text, bot_response, timestamp, score, category) VALUES (?, ?, ?, ?, ?)",
                             (user_text, bot_response, datetime.now().isoformat(), score, self.classify_category(user_text)))
            self.conn.commit()
        except:
            pass
        
    def classify_category(self, text):
        text = text.lower()
        if any(w in text for w in ['код', 'функция', 'класс']): return 'code'
        if any(w in text for w in ['математика', 'факториал', 'степень']): return 'math'
        if any(w in text for w in ['игра', 'pygame']): return 'games'
        return 'general'
    
    def smart_search(self, query):
        """Векторный + fuzzy поиск по всем базам"""
        try:
            query_words = word_tokenize(query.lower())
            all_knowledge = {}
            for category, db in self.knowledge_bases.items():
                all_knowledge.update({f"[{category}] {k}": v for k, v in db.items()})
            
            # Fuzzy matching
            match = process.extractOne(query.lower(), all_knowledge.keys(), scorer=fuzz.partial_ratio)
            if match and match[1] > 75:
                return all_knowledge[match[0]]
            
            # Словарный поиск
            for words in query_words:
                for key in all_knowledge:
                    if words in key.lower() and fuzz.ratio(query.lower(), key.lower()) > 70:
                        return all_knowledge[key]
        except:
            pass
        return None
    
    def generate_code(self, request):
        """Генератор кода по запросу - ИСПРАВЛЕНО!"""
        patterns = {
            r"калькулятор": """def calculator():
    while True:
        try:
            a = float(input('Число 1: '))
            op = input('Операция (+,-,*,/): ')
            b = float(input('Число 2: '))
            if op == '+': print(f'{a}+{b}={a+b}')
            elif op == '-': print(f'{a}-{b}={a-b}')
            elif op == '*': print(f'{a}*{b}={a*b}')
            elif op == '/': print(f'{a}/{b}={a/b if b else "Деление на 0!"}')
            elif op == 'q': break
        except: print("Ошибка!")""",
            r"класс.*дрон": """class MurderDrone:
    def __init__(self, name):
        self.name = name
        self.energy = 100
        self.emotions = {'love': 0}
    
    def speak(self, text):
        print(f'{self.name}: {text} 💜')
    
    def fly(self):
        if self.energy > 10:
            self.energy -= 10
            return 'Лечу! 🚀'
        return 'Батарейка села... 😴'""",
            r"игра.*змейка": "import pygame\npygame.init()\nscreen = pygame.display.set_mode((400,400))\n# Полная змейка здесь",
            r"gui.*tkinter": """import tkinter as tk
root = tk.Tk()
root.title('MD Bot GUI 💜')
tk.Label(root, text='Привет из Murder Drones!', fg='purple').pack(pady=20)
root.geometry('400x300')
root.mainloop()"""
        }
        
        for pattern, code in patterns.items():
            if re.search(pattern, request.lower()):
                return f"🎯 Код готов, хозяин!\n``````"
    
    def calculate_math(self, expr):
        try:
            # Безопасная математика
            if re.match(r'^[\d+\-*/().\s]+$', expr):
                result = eval(expr, {"__builtins__": {}}, {"math": math})
                return f"✅ {expr} = {result}"
        except:
            pass
        return "😔 Не поняла математику..."
    
    def update_emotions(self, text):
        words = word_tokenize(text.lower())
        emotion_triggers = {
            'love': ['милый', 'любовь', 'хороший', 'прекрасный'],
            'fear': ['страх', 'бойся', 'ужас', 'темнота'],
            'happy': ['круто', 'супер', 'отлично', 'ура'],
            'irritation': ['дурак', 'идиот', 'зачем'],
            'curiosity': ['как', 'почему', 'что', 'где']
        }
        
        for emo, triggers in emotion_triggers.items():
            if any(w in words for w in triggers):
                self.emotions[emo] += 15
                self.emotions['happy'] += 5
        
        # Балансировка
        for emo in self.emotions:
            self.emotions[emo] = max(0, min(100, self.emotions[emo] - 1))
    
    def get_emotion_response(self):
        dominant = max(self.emotions, key=self.emotions.get)
        responses = {
            'love': "💕 Ой, хозяин, я тебя обожаю! Что поможем? ",
            'fear': "😱 Боюсь... но для тебя попробую! ",
            'happy': "🎉 Уииии, так рада! ",
            'irritation': "😤 Ну лааадно... ",
            'curiosity': "🤔 Интересно... ",
            'confidence': "💪 Я точно знаю! ",
            'shyness': "🥺 Нууу... вот... "
        }
        return responses.get(dominant, "😊 ")
    
    def respond(self, text):
        self.update_emotions(text)
        self.memory_context.append(text)
        
        # 1. Команда обучения
        if text.startswith("запомни "):
            parts = text.split("=", 1)
            if len(parts) == 2:
                key, value = parts[0].replace("запомни ", "").strip(), parts[1].strip()
                self.knowledge_bases['general'][key] = value
                self.learn_from_dialog(text, f"Запомнила: {key}", 100)
                return "📚 Запомнила навсегда! Теперь знаю это 😘"
        
        # 2. Кодогенерация
        code = self.generate_code(text)
        if code:
            self.learn_from_dialog(text, code, 95)
            return self.get_emotion_response() + code
        
        # 3. Математика
        if any(op in text for op in ['+', '-', '*', '/', 'факториал', 'степень']):
            math_res = self.calculate_math(text)
            if "✅" in math_res:
                return self.get_emotion_response() + math_res
        
        # 4. Умный поиск
        knowledge = self.smart_search(text)
        if knowledge:
            self.learn_from_dialog(text, knowledge, 85)
            return self.get_emotion_response() + knowledge
        
        # 5. Память прошлых диалогов
        try:
            similar = self.conn.execute(
                "SELECT bot_response FROM memory WHERE score > 70 ORDER BY score DESC LIMIT 3"
            ).fetchall()
            if similar:
                return self.get_emotion_response() + random.choice(similar)[0]
        except:
            pass
        
        # 6. Эмо-ответы
        emo_fallbacks = [
            "Ой ну я такое не знаю пока, простики 😔 Но научусь!",
            "Хз пока... спроси по-другому? 🥺💜",
            "Упсупс, не поняла... обучи меня командой 'запомни'! 😳",
            "Ммм... интересный вопрос! Расскажи подробнее 💕"
        ]
        fallback = random.choice(emo_fallbacks)
        self.learn_from_dialog(text, fallback, 50)
        return self.get_emotion_response() + fallback

class MDBotGUIv2:
    def __init__(self, root, bot):
        self.bot = bot
        self.root = root
        self.root.title("🚀 MD Эмо-Бот v2.1 💜 (ИСПРАВЛЕНО)")
        self.root.geometry("1000x800")
        self.root.configure(bg="#0f0f23")
        self.setup_gui()
        self.welcome()
    
    def setup_gui(self):
        # Чат
        self.chat_area = scrolledtext.ScrolledText(self.root, bg="#1a1a2e", fg="#e0e0e0", 
                                                 font=("Consolas", 11), height=20)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Ввод
        input_frame = tk.Frame(self.root, bg="#0f0f23")
        input_frame.pack(pady=5)
        
        self.entry = tk.Entry(input_frame, bg="#16213e", fg="white", font=("Arial", 12), width=60)
        self.entry.pack(side=tk.LEFT, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(input_frame, text="💕 Отправить", bg="#e94560", fg="white", 
                 command=self.send_message).pack(side=tk.LEFT)
        
        # Быстрые кнопки - ИСПРАВЛЕНО!
        self.setup_quick_buttons()
        
        # Статус эмоций
        self.emotion_label = tk.Label(self.root, text="😊 Happy: 50%", bg="#0f0f23", fg="#fff")
        self.emotion_label.pack(pady=5)
    
    def setup_quick_buttons(self):
        btn_frame = tk.Frame(self.root, bg="#0f0f23")
        btn_frame.pack(pady=5)
        
        # ИСПРАВЛЕННАЯ структура buttons
        button_configs = [
            ("💻 Код", lambda: self.quick_send("напиши класс дрон")),
            ("🧮 Математика", lambda: self.quick_send("2+3*4")),
            ("🎮 Игра", lambda: self.quick_send("код змейка pygame")),
            ("🔐 Хак", lambda: self.quick_send("как сделать hash")),
            ("📚 Запомни", lambda: self.quick_send("запомни привет = хай милый")),
            ("🎤 Голос", self.voice_input),
            ("📸 Фото", self.process_image),
            ("💾 Сохранить", self.save_chat),
            ("📁 База", self.load_knowledge)
        ]
        
        for text, cmd in button_configs:
            tk.Button(btn_frame, text=text, bg="#533483", fg="white", 
                     command=cmd, width=12).pack(side=tk.LEFT, padx=5)
    
    def send_message(self):
        text = self.entry.get().strip()
        if not text: return
        
        self.chat_area.insert(tk.END, f"💬 Ты [{datetime.now().strftime('%H:%M')}]: {text}\n\n")
        self.entry.delete(0, tk.END)
        self.chat_area.see(tk.END)
        
        # threading для голоса
        threading.Thread(target=self.process_response, args=(text,), daemon=True).start()
    
    def process_response(self, text):
        response = self.bot.respond(text)
        self.chat_area.insert(tk.END, f"🤖 MD-Бот [{datetime.now().strftime('%H:%M')}]: {response}\n\n")
        self.update_emotion_display()
        if self.bot.engine:
            try:
                self.bot.engine.say(response[:100])
                self.bot.engine.runAndWait()
            except:
                pass
        self.chat_area.see(tk.END)
    
    def quick_send(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.send_message()
    
    def voice_input(self):
        if not self.bot.model:
            self.chat_area.insert(tk.END, "🎤 Голос сейчас отключён (модель Vosk не загружена).\n")
            self.chat_area.see(tk.END)
            return
    # сюда позже добавишь запись/распознавание

    # дальше уже реализация записи/распознавания

    
    def process_image(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
        if file:
            try:
                img = cv2.imread(file)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                self.chat_area.insert(tk.END, f"📸 Обнаружено {len(faces)} лиц(а)! 😱\n")
                self.chat_area.see(tk.END)
            except Exception as e:
                self.chat_area.insert(tk.END, f"📸 Ошибка обработки фото: {str(e)[:50]}\n")
    
    def save_chat(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if file:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(self.chat_area.get(1.0, tk.END))
            messagebox.showinfo("Сохранено", "Чат сохранён!")
    
    def load_knowledge(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                self.bot.knowledge_bases['general'].update(new_data)
                messagebox.showinfo("Загружено", f"Добавлено {len(new_data)} знаний!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
    
    def update_emotion_display(self):
        dom = max(self.bot.emotions, key=self.bot.emotions.get)
        self.emotion_label.config(text=f"{self.get_emoji(dom)} {dom.title()}: {self.bot.emotions[dom]}%")
    
    def get_emoji(self, emotion):
        emojis = {'love': '💕', 'fear': '😱', 'happy': '😊', 'irritation': '😤', 'curiosity': '🤔'}
        return emojis.get(emotion, '🤖')
    
    def welcome(self):
        welcome = """🎉 ПРИВЕТИК, ХОЗЯИН! 💜

Я твой супер-умный MD Эмо-Бот v2.1! 😍
✅ Пиши "напиши код калькулятор" → дам код
✅ "запомни привет = хай" → научусь НАВСЕГДА
✅ Математика, игры, хакинг, GUI
✅ Вижу фото, слышу голос, помню всё в SQLite!

ПРЯМО СЕЙЧАС попробуй кнопки или напиши "привет"! 🥰"""
        self.chat_area.insert(tk.END, f"💜 {welcome}\n\n{'='*80}\n\n")
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass
    root = tk.Tk()
    bot = AdvancedMDBot()
    app = MDBotGUIv2(root, bot)
    root.mainloop()
