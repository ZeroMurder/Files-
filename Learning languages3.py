import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog





def open_code_editor(language_name, file_extension):
    """Общее окно редактора кода для всех языков с возможностью сохранить файл."""

    editor_window = tk.Toplevel(root)
    editor_window.title(f"Редактор кода: {language_name}")
    editor_window.geometry("600x500")

    text_area = tk.Text(editor_window, font=("Consolas", 12), wrap=tk.NONE, undo=True)
    text_area.pack(expand=True, fill='both')

    starter_texts = {
        "C": "int main() {\n    return 0;\n}\n",
        "C++": "int main() {\n    return 0;\n}\n",
        "Python": "def main():\n    pass\n\nif __name__ == '__main__':\n    main()\n",
        "C#": "class Program {\n    static void Main() {\n    }\n}\n",
        "ASM": "; Ассемблерный код тут\n",
        "Kernel": "// Знания о ядре ОС\n"
    }
    text_area.insert(tk.END, starter_texts.get(language_name, ""))

    def save_code():
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_extension,
            filetypes=[(f"{language_name} files", f"*{file_extension}"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get(1.0, tk.END))
            messagebox.showinfo("Сохранено", f"Код успешно сохранен в {file_path}")

    save_button = tk.Button(editor_window, text="Сохранить код", command=save_code,
                            bg="#7B2FF7", fg="white", font=("Arial", 12, "bold"))
    save_button.pack(side=tk.BOTTOM, pady=10)


def open_c_window():
    c_window = tk.Toplevel(root)
    c_window.geometry("500x500")
    c_window.title("Знания о C")
    text = ("Функции в языке C — это блоки кода с именами, которые выполняют определённые действия и могут принимать параметры (входные данные). "
            "Параметры функции — это локальные переменные, доступные только внутри этой функции. Функция может возвращать значение с помощью оператора return.\n\n"
            "Переменные в C — это именованные области памяти для хранения данных определённого типа (например, int — целое число, float — число с плавающей точкой, char — символ). "
            "Переменные бывают локальными (объявляются внутри функции и существуют только во время её выполнения) и глобальными (объявляются вне функций и доступны в программе в целом).\n\n"
            "При вызове функции аргументы передаются в параметры по значению, то есть копируются. Изменения параметров внутри функции не влияют на переданные переменные, "
            "если не используется передача по адресу через указатели.\n\n"
            "Пример функции в C:\nint sum(int a, int b) {\n  return a + b;\n}\nint result = sum(5, 6); // result будет равен 11\n\n"
            "Переменные объявляются с указанием типа и имени, например:\nint x = 10;\nfloat y = 3.14;\nchar c = 'A';\n\n"
            "Таким образом, переменные хранят данные, а функции — это программные блоки для обработки этих данных с локальными параметрами и возможным возвращаемым значением.")
    text_widget = scrolledtext.ScrolledText(c_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


def open_cpp_window():
    cpp_window = tk.Toplevel(root)
    cpp_window.geometry("500x500")
    cpp_window.title("О C++")
    text = ("Функции в C++ — это именованные блоки кода, которые выполняют определённые действия и могут принимать параметры (аргументы). "
            "Аргументы по умолчанию передаются по значению, то есть функция работает с копиями этих значений. Функция может возвращать результат с помощью оператора return. "
            "Если функция не возвращает значение, используется тип void.\n\n"
            "Переменные в C++ — это именованные области памяти с определённым типом данных (int, char, float, bool и др.). Тип переменной объявляется при её создании, так как C++ — язык со статической типизацией. "
            "Переменные бывают локальными (видны только внутри функции или блока) и глобальными (доступны во всей программе). "
            "При объявлении переменной ей можно сразу присвоить значение.\n\n"
            "Пример функции и переменной в C++:\nint sum(int a, int b) {\n  return a + b;\n}\nint result = sum(5, 6);  // result будет 11\nint x = 10;              // переменная типа int с значением 10\n\n"
            "Таким образом, функции позволяют переиспользовать код с параметрами, а переменные хранят данные строго заданного типа в памяти.")
    text_widget = scrolledtext.ScrolledText(cpp_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


def open_python_window():
    python_window = tk.Toplevel(root)
    python_window.geometry("500x500")
    python_window.title("Знания о Python")
    text = ("Кратко про функции и переменные в Python:\n\n"
            "Функции — это именованные блоки кода, которые выполняют определённые действия. "
            "Они могут принимать входные параметры (аргументы) и возвращать результат через ключевое слово return. "
            "Вызов функции запускает выполнение её кода.\n\n"
            "Переменные в Python — это имена, которые ссылаются на объекты в памяти. "
            "Переменная создаётся при первом присваивании значения и хранит ссылку на объект (число, строку, список и т.д.). "
            "Python использует динамическую типизацию — переменная может ссылаться на объекты разных типов в разное время.\n\n"
            "Переменные бывают локальными (видны только внутри функции) и глобальными (видны во всей программе). "
            "В Python переменная создаётся просто присваиванием оператора = без необходимости объявлять тип.\n\n"
            "Пример функции и переменной:\ndef sum(a, b):\n    return a + b\n\nresult = sum(5, 6)  # result равно 11\nx = 10              # переменная x с значением 10\n\n"
            "Таким образом, функции обрабатывают данные, которые передают через параметры, а переменные хранят объекты и управляют ссылками на них в памяти.")
    text_widget = scrolledtext.ScrolledText(python_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


def open_csharp_window():
    cs_window = tk.Toplevel(root)
    cs_window.geometry("500x500")
    cs_window.title("Знания о C#")
    text = ("Функции в C# — это небольшие подпрограммы, которые позволяют вынести повторяющийся код отдельно и вызывать его по необходимости. "
            "В C# функции при объявлении указывают возвращаемый тип, имя и параметры. Если функция ничего не возвращает, указывается тип void. "
            "Внутри классов функции называются методами. Для доступа к функциям без создания объекта используют модификатор static. "
            "Например, функция без параметров, ничего не возвращающая, может выглядеть так:\n\n"
            "public static void Test() {\n    Console.WriteLine(\"Пример функции\");\n}\n\n"
            "Переменные в C# — это места хранения данных определённого типа. В языке существует несколько категорий переменных, включая статические переменные, переменные экземпляра, параметры функций и локальные переменные. Внутри классов переменные называются полями, вне классов — переменными. Переменные должны быть инициализированы перед использованием, чтобы избежать ошибок времени исполнения.\n\n"
            "Таким образом, в C# функции (методы) структурируют код, а переменные обеспечивают хранение и управление данными в программах.")
    text_widget = scrolledtext.ScrolledText(cs_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


def open_asm_window():
    asm_window = tk.Toplevel(root)
    asm_window.geometry("500x500")
    asm_window.title("Знания об Ассемблере (ASM)")
    text = ("Ассемблер — это низкоуровневый язык программирования, служащий промежуточным уровнем между машинным кодом процессора и языками высокого уровня. "
            "Программы на ассемблере пишутся с помощью мнемонических инструкций, каждая из которых соответствует одной операции процессора, например, MOV, ADD, SUB. "
            "Ассемблер позволяет напрямую работать с регистрами процессора и памятью, что даёт точный контроль над аппаратным обеспечением.\n\n"
            "Переменные в ассемблере хранятся двумя основными способами: в регистрах и в памяти. Регистры — это маленькие и быстрые области внутри процессора для временного хранения данных. "
            "Если регистров недостаточно, данные размещаются в памяти, обозначая области с помощью символических имён. Важно размещать переменные так, чтобы они не пересекались с кодом программы, "
            "иначе процессор может выполнить данные как команды, что приведёт к ошибкам.\n\n"
            "Функции в ассемблере реализуются как подпрограммы с помощью команд перехода и возврата (CALL и RET). В них используют стек для передачи параметров и локального хранения данных. "
            "Функции помогают структурировать код и переиспользовать блоки команд.\n\n"
            "Таким образом, ассемблер обеспечивает максимально близкое к железу управление компьютером, требует детального понимания архитектуры процессора и памяти и применяется там, "
            "где важна скорость и эффективность работы программы.")
    text_widget = scrolledtext.ScrolledText(asm_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


def open_kernel_window():
    kernel_window = tk.Toplevel(root)
    kernel_window.geometry("500x500")
    kernel_window.title("Знания о Ядре ОС (Kernel)")
    text = ("Ядро операционной системы (кернел) — это центральная часть ОС, которая управляет аппаратными ресурсами, "
            "обеспечивает выполнение программ и взаимодействие между устройствами, пользователями и программами. "
            "Оно работает в привилегированном режиме и выполняет задачи, недоступные обычным приложениям.\n\n"
            "Функции ядра включают: управление процессами (создание, планирование, прерывание), управление памятью, "
            "управление вводом-выводом, работу с файловой системой, обеспечение безопасности и изоляции процессов, "
            "а также межпроцессное взаимодействие и системные вызовы.\n\n"
            "Переменные ядра — данные, необходимые для функционирования ОС на низком уровне. Они могут быть глобальными, per-CPU и локальными, "
            "разделяясь по назначению и области видимости. Управление переменными ядра ограничено для безопасности и происходит через системные вызовы и специальные API.\n\n"
            "Ядро — сложный набор функций и данных, направленных на эффективное и надежное управление аппаратными и программными ресурсами системы.")
    text_widget = scrolledtext.ScrolledText(kernel_window, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
    text_widget.pack(expand=True, fill='both')
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)


purple_bg = "#7B2FF7"
purple_fg = "white"

root = tk.Tk()
root.geometry("700x1000")
root.title("Окно с кнопками")

# Кнопки для знаний по языкам
btn_c = tk.Button(root, text="Знания о C", command=open_c_window,
                  bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_c.pack(pady=5, fill="x", padx=50)

btn_c_editor = tk.Button(root, text="Редактор кода C",
                         command=lambda: open_code_editor("C", ".c"),
                         bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_c_editor.pack(pady=5, fill="x", padx=50)


btn_cpp = tk.Button(root, text="О C++", command=open_cpp_window,
                    bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_cpp.pack(pady=5, fill="x", padx=50)

btn_cpp_editor = tk.Button(root, text="Редактор кода C++",
                           command=lambda: open_code_editor("C++", ".cpp"),
                           bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_cpp_editor.pack(pady=5, fill="x", padx=50)


btn_python = tk.Button(root, text="Знания о Python", command=open_python_window,
                       bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_python.pack(pady=5, fill="x", padx=50)

btn_python_editor = tk.Button(root, text="Редактор кода Python",
                              command=lambda: open_code_editor("Python", ".py"),
                              bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_python_editor.pack(pady=5, fill="x", padx=50)


btn_csharp = tk.Button(root, text="Знания о C#", command=open_csharp_window,
                       bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_csharp.pack(pady=5, fill="x", padx=50)

btn_csharp_editor = tk.Button(root, text="Редактор кода C#",
                              command=lambda: open_code_editor("C#", ".cs"),
                              bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_csharp_editor.pack(pady=5, fill="x", padx=50)


btn_asm = tk.Button(root, text="Знания об ASM (Ассемблер)", command=open_asm_window,
                    bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_asm.pack(pady=5, fill="x", padx=50)

btn_asm_editor = tk.Button(root, text="Редактор кода Ассемблера",
                           command=lambda: open_code_editor("ASM", ".asm"),
                           bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_asm_editor.pack(pady=5, fill="x", padx=50)


btn_kernel = tk.Button(root, text="Знания о Kernel (Ядро ОС)", command=open_kernel_window,
                       bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_kernel.pack(pady=5, fill="x", padx=50)

btn_kernel_editor = tk.Button(root, text="Редактор кода Ядра ОС",
                              command=lambda: open_code_editor("Kernel", ".txt"),
                              bg=purple_bg, fg=purple_fg, font=("Arial", 12, "bold"))
btn_kernel_editor.pack(pady=5, fill="x", padx=50)

root.mainloop()
