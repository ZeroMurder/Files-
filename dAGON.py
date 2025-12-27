import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import os
import sys
import threading
import queue
import json

from playsound import playsound


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def run_subprocess(cmd, cwd=None):
    try:
        p = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        out, err = p.communicate()
        return p.returncode, out, err
    except Exception as e:
        return -1, "", str(e)


# ---------- МИНИ AI-АССИСТЕНТ ----------

def simple_ai_suggestions(code: str, lang: str) -> list:
    tips = []
    if lang == "python":
        if "print " in code and "print(" not in code:
            tips.append("Python 3: используй print(...).")
        if "except:" in code and "Exception" not in code:
            tips.append("Голый except лучше заменить на except Exception as e:.")
    if lang in ("c", "cpp"):
        if "gets(" in code:
            tips.append("gets небезопасна, используй fgets.")
        if "main(" in code and "return 0;" not in code:
            tips.append("В конце main обычно пишут return 0;")
    if not tips:
        tips.append("Шаблонный анализ не нашёл явных проблем.")
    return tips


# ---------- ОСНОВНОЙ КЛАСС ----------

class MiniIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UniversalDev no-pygame + UI-Editor v1.0")
        self.geometry("1300x750")
        self.configure(bg="black")

        self.current_file = None
        self.current_lang = "python"

        # терминал
        self.terminal_process = None
        self.terminal_queue = queue.Queue()
        self.after(100, self._poll_terminal_output)

        # музыка
        self.playlist = []
        self.current_track_index = None
        self.music_thread = None
        self.music_stop_flag = False
        self.loop_enabled = False
        self.music_playing = False

        # UI-редактор
        self.ui_tabs_meta = {}
        self.ui_merge_source = None

        self.create_widgets()
        self.bind_shortcuts()

    # ---------- UI ----------

    def create_widgets(self):
        self.create_menu()

        main = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="black")
        main.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main, bg="black", width=260)
        self.create_file_tree(left_frame)
        main.add(left_frame)

        right = tk.PanedWindow(main, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="black")
        main.add(right)

        editor_frame = tk.Frame(right, bg="black")
        self.create_editor(editor_frame)
        right.add(editor_frame)

        bottom_frame = tk.Frame(right, bg="black", height=260)
        self.create_bottom_tabs(bottom_frame)
        right.add(bottom_frame)

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Новый файл", command=self.new_file)
        file_menu.add_command(label="Открыть файл...", command=self.open_file_dialog)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)

        project_menu = tk.Menu(menu, tearoff=0)
        project_menu.add_command(label="Собрать Python -> exe", command=self.build_python_exe)
        project_menu.add_command(label="Собрать C/C++ (gcc)", command=self.build_c)

        tools_menu = tk.Menu(menu, tearoff=0)
        tools_menu.add_command(label="Запуск файла", command=self.run_current)
        tools_menu.add_command(label="Анализ кода (мини ИИ)", command=self.run_ai_assistant)

        menu.add_cascade(label="Файл", menu=file_menu)
        menu.add_cascade(label="Проект", menu=project_menu)
        menu.add_cascade(label="Инструменты", menu=tools_menu)

    # ---------- ФАЙЛОВОЕ ДЕРЕВО ----------

    def create_file_tree(self, parent):
        toolbar = tk.Frame(parent, bg="black")
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Открыть папку", command=self.choose_root_dir).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Новая папка", command=self.create_directory).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Новый файл", command=self.create_new_file).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(parent)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.root_dir = None

    def choose_root_dir(self):
        d = filedialog.askdirectory()
        if not d:
            return
        self.root_dir = d
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        if not self.root_dir:
            return

        def insert_node(parent_id, path):
            for name in os.listdir(path):
                full = os.path.join(path, name)
                node_id = self.tree.insert(parent_id, "end", text=name, values=[full])
                if os.path.isdir(full):
                    insert_node(node_id, full)

        insert_node("", self.root_dir)

    def on_tree_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        path = self.tree.item(item, "values")[0]
        if os.path.isdir(path):
            return
        self.open_file(path)

    def create_directory(self):
        if not self.root_dir:
            messagebox.showinfo("Папка", "Сначала открой корневую папку проекта.")
            return
        name = "new_folder"
        path = os.path.join(self.root_dir, name)
        i = 1
        while os.path.exists(path):
            path = os.path.join(self.root_dir, f"{name}_{i}")
            i += 1
        os.makedirs(path)
        self.refresh_tree()

    def create_new_file(self):
        if not self.root_dir:
            messagebox.showinfo("Файл", "Сначала открой корневую папку проекта.")
            return
        name = "new_file.py"
        path = os.path.join(self.root_dir, name)
        i = 1
        while os.path.exists(path):
            path = os.path.join(self.root_dir, f"new_file_{i}.py")
            i += 1
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        self.refresh_tree()
        self.open_file(path)

    # ---------- РЕДАКТОР ----------

    def create_editor(self, parent):
        self.text = tk.Text(parent, wrap="none", undo=True,
                            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.text.pack(fill=tk.BOTH, expand=True)

        y_scroll = tk.Scrollbar(self.text, orient=tk.VERTICAL, command=self.text.yview)
        self.text.config(yscrollcommand=y_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.tag_configure("error_line", background="#552222")

    def highlight_error_line(self, lineno):
        self.text.tag_remove("error_line", "1.0", tk.END)
        if lineno is None:
            return
        self.text.tag_add("error_line", f"{lineno}.0", f"{lineno}.end")

    # ---------- ВКЛАДКИ ВНИЗУ ----------

    def create_bottom_tabs(self, parent):
        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(self.nb, bg="black", fg="lime")
        self.console_text.pack(fill=tk.BOTH, expand=True)
        self.nb.add(self.console_text, text="Консоль")

        self.terminal_text = tk.Text(self.nb, bg="#000010", fg="#00ffcc")
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        self.terminal_text.bind("<Return>", self._terminal_enter)
        self.nb.add(self.terminal_text, text="Терминал")

        self.debug_text = tk.Text(self.nb, bg="#101010", fg="#ffff66")
        self.debug_text.pack(fill=tk.BOTH, expand=True)
        self.nb.add(self.debug_text, text="Отладка")

        self.problems_list = tk.Listbox(self.nb, bg="#200000", fg="#ff8080")
        self.problems_list.pack(fill=tk.BOTH, expand=True)
        self.problems_list.bind("<Double-1>", self._problem_jump_to_line)
        self.nb.add(self.problems_list, text="Проблемы")

        self.ai_text = tk.Text(self.nb, bg="black", fg="cyan")
        self.ai_text.pack(fill=tk.BOTH, expand=True)
        self.nb.add(self.ai_text, text="AI")

        self.player_frame = tk.Frame(self.nb, bg="black")
        self.create_music_player(self.player_frame)
        self.nb.add(self.player_frame, text="Музыка")

        self.ui_editor_frame = tk.Frame(self.nb, bg="black")
        self.create_ui_editor(self.ui_editor_frame)
        self.nb.add(self.ui_editor_frame, text="UI-редактор")

    # ---------- ЛОГИ ----------

    def log(self, text):
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)

    def debug_log(self, text):
        self.debug_text.insert(tk.END, text + "\n")
        self.debug_text.see(tk.END)

    def ai_log(self, text):
        self.ai_text.insert(tk.END, text + "\n")
        self.ai_text.see(tk.END)

    def add_problem(self, text, lineno=None):
        display = text
        if lineno:
            display = f"Строка {lineno}: {text}"
        self.problems_list.insert(tk.END, display)

    # ---------- ФАЙЛЫ ----------

    def new_file(self):
        self.current_file = None
        self.text.delete("1.0", tk.END)
        self.update_title()

    def open_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("All", "*.*")])
        if path:
            self.open_file(path)

    def open_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding=sys.getdefaultencoding(), errors="ignore") as f:
                content = f.read()
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.current_file = path
        self.detect_language(path)
        self.update_title()

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", tk.END))
        self.log(f"Сохранено: {self.current_file}")

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".py")
        if not path:
            return
        self.current_file = path
        self.save_file()
        self.detect_language(path)
        self.refresh_tree()
        self.update_title()

    def detect_language(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".py":
            self.current_lang = "python"
        elif ext == ".c":
            self.current_lang = "c"
        elif ext in (".cpp", ".cc", ".cxx"):
            self.current_lang = "cpp"
        else:
            self.current_lang = "text"

    def update_title(self):
        name = self.current_file if self.current_file else "Новый файл"
        self.title(f"UniversalDev - {name}")

    # ---------- ЗАПУСК / СБОРКА ----------

    def run_current(self):
        self.save_file()
        if not self.current_file:
            return
        if self.current_lang == "python":
            cmd = [sys.executable, self.current_file]
        elif self.current_lang in ("c", "cpp"):
            exe = os.path.splitext(self.current_file)[0] + ".exe"
            if not os.path.exists(exe):
                messagebox.showinfo("Запуск", "Сначала собери C/C++ файл.")
                return
            cmd = [exe]
        else:
            messagebox.showinfo("Запуск", "Неизвестный тип файла.")
            return

        self.log(f"Запуск: {' '.join(cmd)}")

        def worker():
            code, out, err = run_subprocess(cmd, cwd=os.path.dirname(self.current_file))
            if out:
                self.log(out)
            if err:
                self.log(err)
                self.debug_log(err)

        threading.Thread(target=worker, daemon=True).start()

    def build_python_exe(self):
        self.save_file()
        if not self.current_file or self.current_lang != "python":
            messagebox.showinfo("Сборка", "Открой .py файл.")
            return
        cmd = f"pyinstaller --onefile \"{self.current_file}\""
        self.log(f"Сборка Python -> exe: {cmd}")
        # pyinstaller является стандартным способом упаковки Tkinter‑GUI в exe.[web:5]
        def worker():
            self.problems_list.delete(0, tk.END)
            self.highlight_error_line(None)
            code, out, err = run_subprocess(cmd, cwd=os.path.dirname(self.current_file))
            if out:
                self.log(out)
            if err:
                self.log(err)
                self.debug_log(err)
        threading.Thread(target=worker, daemon=True).start()

    def build_c(self):
        self.save_file()
        if not self.current_file or self.current_lang not in ("c", "cpp"):
            messagebox.showinfo("Сборка", "Открой .c или .cpp файл.")
            return
        exe = os.path.splitext(self.current_file)[0] + ".exe"
        if self.current_lang == "c":
            cmd = f"gcc \"{self.current_file}\" -o \"{exe}\""
        else:
            cmd = f"g++ \"{self.current_file}\" -o \"{exe}\""
        self.log(f"Сборка C/C++: {cmd}")
        # использование gcc/g++ через subprocess — распространённый способ сборки C‑кода из Python.[web:31]
        def worker():
            self.problems_list.delete(0, tk.END)
            self.highlight_error_line(None)
            code, out, err = run_subprocess(cmd, cwd=os.path.dirname(self.current_file))
            if out:
                self.log(out)
            if err:
                self.log(err)
                self.debug_log(err)
        threading.Thread(target=worker, daemon=True).start()

    # ---------- AI ----------

    def run_ai_assistant(self):
        code = self.text.get("1.0", tk.END)
        tips = simple_ai_suggestions(code, self.current_lang)
        self.ai_text.delete("1.0", tk.END)
        for t in tips:
            self.ai_log("- " + t)

    # ---------- ТЕРМИНАЛ ----------

    def _start_terminal(self):
        if self.terminal_process and self.terminal_process.poll() is None:
            return
        shell_cmd = os.environ.get("COMSPEC", "cmd.exe") if os.name == "nt" else "/bin/bash"
        self.terminal_process = subprocess.Popen(
            shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False
        )

        def reader():
            for line in self.terminal_process.stdout:
                self.terminal_queue.put(line)
            self.terminal_queue.put(None)

        threading.Thread(target=reader, daemon=True).start()
        self.terminal_text.insert(tk.END, f"[Терминал запущен: {shell_cmd}]\n")

    def _poll_terminal_output(self):
        try:
            while True:
                item = self.terminal_queue.get_nowait()
                if item is None:
                    break
                self.terminal_text.insert(tk.END, item)
                self.terminal_text.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self._poll_terminal_output)

    def _terminal_enter(self, event):
        line = self.terminal_text.get("end-2l linestart", "end-1c")
        cmd = line.strip()
        if not cmd:
            return "break"
        if not self.terminal_process or self.terminal_process.poll() is not None:
            self._start_terminal()
        self.terminal_process.stdin.write(cmd + "\n")
        self.terminal_process.stdin.flush()
        self.terminal_text.insert(tk.END, "\n")
        return "break"

    # ---------- ПРОБЛЕМЫ ----------

    def _problem_jump_to_line(self, event):
        selection = self.problems_list.curselection()
        if not selection:
            return
        text = self.problems_list.get(selection[0])
        import re
        m = re.search(r"(\d+)", text)
        if not m:
            return
        lineno = int(m.group(1))
        self.text.mark_set(tk.INSERT, f"{lineno}.0")
        self.text.see(f"{lineno}.0")
        self.highlight_error_line(lineno)

    # ---------- МУЗЫКАЛЬНЫЙ ПЛЕЕР (playsound) ----------

    def create_music_player(self, parent):
        parent.configure(bg="black")

        top = tk.Frame(parent, bg="black")
        top.pack(fill=tk.X, pady=5)

        style_btn = dict(bg="#222222", fg="white", activebackground="#444444",
                         activeforeground="white", bd=0, padx=10, pady=3)

        tk.Button(top, text="Добавить треки", command=self.add_tracks, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(top, text="Удалить", command=self.remove_track, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(top, text="Переименовать", command=self.rename_track, **style_btn).pack(side=tk.LEFT, padx=3)

        center = tk.Frame(parent, bg="black")
        center.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.music_list = tk.Listbox(center, bg="#101010", fg="white", selectbackground="#0066ff",
                                     bd=0, highlightthickness=0)
        self.music_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(center, orient=tk.VERTICAL, command=self.music_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.music_list.config(yscrollcommand=scroll.set)

        bottom = tk.Frame(parent, bg="black")
        bottom.pack(fill=tk.X, pady=5)

        self.track_label = tk.Label(bottom, text="Нет трека", bg="black", fg="white",
                                    anchor="w", font=("Segoe UI", 10, "bold"))
        self.track_label.pack(fill=tk.X, padx=10, pady=(0, 3))

        control = tk.Frame(bottom, bg="black")
        control.pack(fill=tk.X, pady=5)

        tk.Button(control, text="⏮", command=self.prev_track, width=4, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(control, text="▶", command=self.play_selected, width=4, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(control, text="⏹", command=self.stop_music, width=4, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(control, text="⏭", command=self.next_track, width=4, **style_btn).pack(side=tk.LEFT, padx=3)

        self.loop_btn = tk.Button(control, text="Loop: OFF", command=self.toggle_loop, **style_btn)
        self.loop_btn.pack(side=tk.RIGHT, padx=8)

    def add_tracks(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio", "*.mp3 *.wav"), ("All", "*.*")]
        )
        for f in files:
            name = os.path.basename(f)
            self.playlist.append({"path": f, "name": name})
            self.music_list.insert(tk.END, name)

    def remove_track(self):
        idx = self._get_selected_track_index()
        if idx is None:
            return
        self.music_list.delete(idx)
        del self.playlist[idx]
        if self.current_track_index == idx:
            self.stop_music()
            self.current_track_index = None
            self.track_label.config(text="Нет трека")

    def rename_track(self):
        idx = self._get_selected_track_index()
        if idx is None:
            return
        old_name = self.playlist[idx]["name"]
        new_name = simpledialog.askstring("Переименование", "Новое название:", initialvalue=old_name)
        if not new_name:
            return
        self.playlist[idx]["name"] = new_name
        self.music_list.delete(idx)
        self.music_list.insert(idx, new_name)
        if self.current_track_index == idx:
            self.track_label.config(text=new_name)

    def _get_selected_track_index(self):
        sel = self.music_list.curselection()
        if not sel:
            return None
        return sel[0]

    def _music_worker(self, path):
        while not self.music_stop_flag:
            try:
                playsound(path)  # playsound — простой блокирующий плеер без внешних зависимостей.[web:24]
            except Exception as e:
                self.debug_log(f"Ошибка воспроизведения: {e}")
                break
            if not self.loop_enabled:
                break
        self.music_playing = False

    def play_selected(self):
        idx = self._get_selected_track_index()
        if idx is None:
            if self.current_track_index is not None:
                idx = self.current_track_index
            else:
                return
        self.current_track_index = idx
        track = self.playlist[idx]
        path = track["path"]

        self.stop_music()
        self.track_label.config(text=track["name"])

        self.music_stop_flag = False
        self.music_playing = True
        self.music_thread = threading.Thread(target=self._music_worker, args=(path,), daemon=True)
        self.music_thread.start()

    def stop_music(self):
        self.music_stop_flag = True
        self.music_playing = False

    def next_track(self):
        if not self.playlist:
            return
        if self.current_track_index is None:
            self.current_track_index = 0
        else:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.music_list.select_clear(0, tk.END)
        self.music_list.select_set(self.current_track_index)
        self.play_selected()

    def prev_track(self):
        if not self.playlist:
            return
        if self.current_track_index is None:
            self.current_track_index = 0
        else:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
        self.music_list.select_clear(0, tk.END)
        self.music_list.select_set(self.current_track_index)
        self.play_selected()

    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        self.loop_btn.config(text=f"Loop: {'ON' if self.loop_enabled else 'OFF'}")

    # ---------- UI-РЕДАКТОР ----------

    def create_ui_editor(self, parent):
        parent.configure(bg="black")

        toolbar = tk.Frame(parent, bg="black")
        toolbar.pack(fill=tk.X, pady=3)

        style_btn = dict(bg="#222222", fg="white", activebackground="#444444",
                         activeforeground="white", bd=0, padx=8, pady=3)

        tk.Button(toolbar, text="Новая вкладка", command=self.ui_create_tab, **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Кнопка", command=lambda: self.ui_add_widget("button"), **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Окно", command=lambda: self.ui_add_widget("frame"), **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Канбан-колонка", command=lambda: self.ui_add_widget("kanban"), **style_btn).pack(side=tk.LEFT, padx=3)
        tk.Button(toolbar, text="Input", command=lambda: self.ui_add_widget("entry"), **style_btn).pack(side=tk.LEFT, padx=3)

        tk.Button(toolbar, text="Сохранить конфиг", command=self.ui_save_layout, **style_btn).pack(side=tk.RIGHT, padx=3)
        tk.Button(toolbar, text="Загрузить конфиг", command=self.ui_load_layout, **style_btn).pack(side=tk.RIGHT, padx=3)

        self.ui_notebook = ttk.Notebook(parent)
        self.ui_notebook.pack(fill=tk.BOTH, expand=True, pady=(3, 0))

        self.ui_create_tab()

    def ui_create_tab(self):
        tab = tk.Frame(self.ui_notebook, bg="#101010")
        name = f"Tab {len(self.ui_notebook.tabs()) + 1}"
        self.ui_notebook.add(tab, text=name)
        self.ui_notebook.select(tab)
        self.ui_tabs_meta[tab] = []

    def ui_get_current_tab(self):
        tid = self.ui_notebook.select()
        if not tid:
            return None
        return self.ui_notebook.nametowidget(tid)

    def ui_add_widget(self, kind):
        tab = self.ui_get_current_tab()
        if tab is None:
            return

        container = tk.Frame(tab, bg="#202020", bd=1, relief=tk.SOLID)
        container.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)

        meta = {
            "kind": kind,
            "container": container,
            "widget": None,
            "title": "",
            "code": "",
            "linked_with": []
        }

        if kind == "button":
            btn = tk.Button(container, text="Новая кнопка",
                            command=lambda m=meta: self.ui_run_widget_code(m))
            btn.pack(fill=tk.X, padx=4, pady=4)
            meta["widget"] = btn
            meta["title"] = "Новая кнопка"

        elif kind == "entry":
            lbl = tk.Label(container, text="Input:", bg="#202020", fg="white")
            lbl.pack(side=tk.LEFT, padx=4, pady=4)
            ent = tk.Entry(container)
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)
            meta["widget"] = ent
            meta["title"] = "Input"

        elif kind == "frame":
            lbl = tk.Label(container, text="Окно", bg="#202020", fg="white")
            lbl.pack(anchor="w", padx=4, pady=4)
            meta["widget"] = lbl
            meta["title"] = "Окно"

        elif kind == "kanban":
            lbl = tk.Label(container, text="Канбан-колонка", bg="#202020", fg="white")
            lbl.pack(anchor="w", padx=4, pady=(4, 0))
            listbox = tk.Listbox(container, bg="#151515", fg="white", height=4)
            listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            meta["widget"] = listbox
            meta["title"] = "Канбан-колонка"

        container.bind("<Button-3>", lambda e, m=meta: self.ui_show_context_menu(e, m))
        for child in container.winfo_children():
            child.bind("<Button-3>", lambda e, m=meta: self.ui_show_context_menu(e, m))

        self.ui_tabs_meta[tab].append(meta)

    def ui_show_context_menu(self, event, meta):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Переименовать", command=lambda m=meta: self.ui_rename_widget(m))
        menu.add_command(label="Настроить код...", command=lambda m=meta: self.ui_edit_code(m))
        menu.add_separator()
        menu.add_command(label="Выбрать как источник объединения", command=lambda m=meta: self.ui_set_merge_source(m))
        menu.add_command(label="Объединить в столбик с источником", command=lambda m=meta: self.ui_merge_with_source(m))
        menu.add_separator()
        menu.add_command(label="Удалить элемент", command=lambda m=meta: self.ui_delete_widget(m))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def ui_rename_widget(self, meta):
        new_name = simpledialog.askstring("Переименование", "Новое имя:", initialvalue=meta["title"])
        if not new_name:
            return
        meta["title"] = new_name
        w = meta["widget"]
        if isinstance(w, tk.Button):
            w.config(text=new_name)
        elif isinstance(w, tk.Label):
            w.config(text=new_name)

    def ui_edit_code(self, meta):
        win = tk.Toplevel(self)
        win.title("Код элемента")
        win.geometry("600x400")

        txt = tk.Text(win, bg="#101010", fg="#ffffff", insertbackground="white")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", meta["code"])

        def save_and_close():
            meta["code"] = txt.get("1.0", tk.END)
            win.destroy()

        tk.Button(win, text="Сохранить", command=save_and_close).pack(pady=4)

    def ui_run_widget_code(self, meta):
        if not meta["code"].strip():
            return
        local_ctx = {
            "meta": meta,
            "app": self,
            "root": self,
        }
        w = meta["widget"]
        if isinstance(w, tk.Entry):
            local_ctx["input_value"] = w.get()
        try:
            exec(meta["code"], {}, local_ctx)
        except Exception as e:
            messagebox.showerror("Ошибка кода", str(e))

    def ui_set_merge_source(self, meta):
        self.ui_merge_source = meta
        self.debug_log(f"Источник объединения: {meta['title']}")

    def ui_merge_with_source(self, target_meta):
        if self.ui_merge_source is None or self.ui_merge_source is target_meta:
            return
        src_container = self.ui_merge_source["container"]
        tgt_container = target_meta["container"]
        tgt_container.pack_forget()
        tgt_container.master = src_container
        tgt_container.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)
        self.ui_merge_source["linked_with"].append(target_meta)
        self.debug_log(f"{target_meta['title']} объединён со {self.ui_merge_source['title']}")

    def ui_delete_widget(self, meta):
        tab = self.ui_get_current_tab()
        if tab is None:
            return
        if messagebox.askyesno("Удаление", f"Удалить элемент '{meta['title']}'?"):
            meta["container"].destroy()
            if tab in self.ui_tabs_meta:
                self.ui_tabs_meta[tab] = [m for m in self.ui_tabs_meta[tab] if m is not meta]

    def ui_save_layout(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        data = []
        for tab in self.ui_tabs_meta:
            tab_title = self.ui_notebook.tab(tab, "text")
            items = []
            for meta in self.ui_tabs_meta[tab]:
                items.append({
                    "kind": meta["kind"],
                    "title": meta["title"],
                    "code": meta["code"],
                })
            data.append({"title": tab_title, "items": items})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.log(f"UI-конфиг сохранён: {path}")

    def ui_load_layout(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for tab_id in list(self.ui_notebook.tabs()):
            tab = self.ui_notebook.nametowidget(tab_id)
            tab.destroy()
        self.ui_tabs_meta.clear()

        for tab_info in data:
            tab = tk.Frame(self.ui_notebook, bg="#101010")
            self.ui_notebook.add(tab, text=tab_info.get("title", "Tab"))
            self.ui_tabs_meta[tab] = []
            for item in tab_info.get("items", []):
                self.ui_add_widget(item["kind"])
                meta = self.ui_tabs_meta[tab][-1]
                meta["title"] = item.get("title", meta["title"])
                meta["code"] = item.get("code", "")
                self.ui_rename_widget(meta)

    # ---------- ШОРТКАТЫ ----------

    def bind_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<F5>", lambda e: self.run_current())
        self.bind("<F9>", lambda e: self.build_python_exe())


if __name__ == "__main__":
    app = MiniIDE()
    app.mainloop()
