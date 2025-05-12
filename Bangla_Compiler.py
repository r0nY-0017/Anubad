import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
from io import StringIO
import sys
import ast
import threading

class BanglaCompiler:
    def __init__(self, root):
        self.root = root
        self.root.title("অনুবাদ : বাংলা মিনি কম্পাইলার")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f2f5")

        #Font Setup
        self.font = ("Kalpurush", 16)
        self.code_font = ("Kalpurush", 16, "normal")

        #Theme Setup
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=self.font, padding=10, background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[("active", "#45a049")])
        self.style.configure("TLabel", font=self.font, background="#f0f2f5")
        self.style.configure("TFrame", background="#f0f2f5")

        #Menu Bar
        self.menu_bar = tk.Menu(root, font=self.font, bg="#ffffff", fg="#333333")
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font)
        self.file_menu.add_command(label="নতুন ফাইল", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="ফাইল খুলুন", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="সেভ করুন", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="প্রস্থান", command=root.quit)
        self.menu_bar.add_cascade(label="ফাইল", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font)
        self.edit_menu.add_command(label="কাট", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="কপি", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="পেস্ট", command=self.paste_text, accelerator="Ctrl+V")
        self.menu_bar.add_cascade(label="সম্পাদন", menu=self.edit_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.font)
        self.help_menu.add_command(label="কীওয়ার্ড সাহায্য", command=self.show_keywords_help)
        self.help_menu.add_command(label="সম্পর্কে", command=self.show_about)
        self.menu_bar.add_cascade(label="সাহায্য", menu=self.help_menu)

        self.root.config(menu=self.menu_bar)

        #Main Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #Code Editor
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        #Code Editor Frame
        self.code_frame = ttk.Frame(self.left_frame)
        self.code_frame.pack(fill=tk.BOTH, expand=True)

        self.code_label = ttk.Label(self.code_frame, text="বাংলা কোড লিখুন:")
        self.code_label.pack(anchor=tk.W, pady=(0, 5))

        #Line Number
        self.editor_container = ttk.Frame(self.code_frame)
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            self.editor_container,
            width=4,
            font=self.code_font,
            bg="#e0e0e0",
            fg="#333333",
            state='disabled',
            wrap=tk.NONE,
            borderwidth=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = scrolledtext.ScrolledText(
            self.editor_container,
            width=50,
            height=25,
            font=self.code_font,
            wrap=tk.NONE,
            undo=True,
            bg="#ffffff",
            fg="#333333",
            insertbackground="black",
            relief="flat",
            borderwidth=1
        )
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ডান ফ্রেম (আউটপুট এবং বাটনের জন্য)
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # বাটন ফ্রেম (আউটপুটের উপরে)
        self.button_frame = ttk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        # রান বাটন
        self.run_button = ttk.Button(
            self.button_frame,
            text="রান করুন (F5)",
            command=self.run_code,
            style="TButton"
        )
        self.run_button.pack(side=tk.LEFT, padx=10)

        # ক্লিয়ার বাটন
        self.clear_button = ttk.Button(
            self.button_frame,
            text="আউটপুট পরিষ্কার করুন",
            command=self.clear_output,
            style="TButton"
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # আউটপুট ফ্রেম
        self.output_frame = ttk.Frame(self.right_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_label = ttk.Label(self.output_frame, text="আউটপুট:")
        self.output_label.pack(anchor=tk.W, pady=(0, 5))

        self.output_display = scrolledtext.ScrolledText(
            self.output_frame,
            width=50,
            height=25,
            font=self.code_font,
            state='disabled',
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
            borderwidth=1
        )
        self.output_display.pack(fill=tk.BOTH, expand=True)

        # কী-বাইন্ডিং
        self.root.bind('<F5>', lambda event: self.run_code())
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())

        # স্ট্যাটাস বার
        self.status_bar = ttk.Label(
            root,
            text="প্রস্তুত",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # উদাহরণ কোড লোড
        self.load_example()
        self.update_line_numbers()

        # লাইন নাম্বার আপডেট
        self.code_editor.bind('<KeyRelease>', lambda event: self.update_line_numbers())
        self.code_editor.bind('<MouseWheel>', lambda event: self.sync_scroll(event))
        self.line_numbers.bind('<MouseWheel>', lambda event: self.sync_scroll(event))

    def sync_scroll(self, event):
        self.code_editor.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def update_line_numbers(self):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        line_count = int(self.code_editor.index('end-1c').split('.')[0])
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, line_numbers_text)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])

    def new_file(self):
        self.code_editor.delete(1.0, tk.END)
        self.clear_output()
        self.status_bar.config(text="নতুন ফাইল তৈরি হয়েছে")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Bangla Code Files", "*.bn"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.code_editor.delete(1.0, tk.END)
                    self.code_editor.insert(1.0, file.read())
                self.status_bar.config(text=f"ফাইল খোলা হয়েছে: {file_path}")
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("ত্রুটি", f"ফাইল খুলতে সমস্যা:\n{str(e)}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".bn",
            filetypes=[("Bangla Code Files", "*.bn"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.code_editor.get(1.0, tk.END))
                self.status_bar.config(text=f"ফাইল সেভ করা হয়েছে: {file_path}")
            except Exception as e:
                messagebox.showerror("ত্রুটি", f"ফাইল সেভ করতে সমস্যা:\n{str(e)}")

    def cut_text(self):
        self.code_editor.event_generate("<<Cut>>")

    def copy_text(self):
        self.code_editor.event_generate("<<Copy>>")

    def paste_text(self):
        self.code_editor.event_generate("<<Paste>>")

    def clear_output(self):
        self.output_display.config(state='normal')
        self.output_display.delete(1.0, tk.END)
        self.output_display.config(state='disabled')
        self.status_bar.config(text="আউটপুট পরিষ্কার করা হয়েছে")

    def show_keywords_help(self):
        help_text = """বাংলা কীওয়ার্ড সাহায়িকা:
        
ধরি ক = ৫        # ভেরিয়েবল ডিক্লেয়ারেশন
দেখাও(ক)         # ভেরিয়েবল প্রিন্ট করা
দেখাও("হ্যালো")  # টেক্সট প্রিন্ট করা
যদি ক > ১০ হয়:   # শর্তসাপেক্ষ
    দেখাও("বড়")
নাহলে:
    দেখাও("ছোট")

যতক্ষণ ক < ১০:   # লুপ
    দেখাও(ক)
    ক = ক + ১
"""
        messagebox.showinfo("কীওয়ার্ড সাহায্য", help_text)

    def show_about(self):
        about_text = """বাংলা মিনি কম্পাইলার
ভার্সন 2.2

এটি একটি বাংলা সিনট্যাক্স ভিত্তিক প্রোগ্রামিং পরিবেশ।
পাইথনে তৈরি করা হয়েছে Tkinter GUI ব্যবহার করে।

ডেভেলপার: Md Mehedi Hasan Rony
"""
        messagebox.showinfo("সম্পর্কে", about_text)

    def load_example(self):
        example_code = """# এখানে কোড লিখুন...

"""
        self.code_editor.delete(1.0, tk.END)
        self.code_editor.insert(1.0, example_code)

    def run_code(self):
        def execute():
            try:
                bangla_code = self.code_editor.get('1.0', tk.END)
                if not bangla_code.strip():
                    self.show_error("কোড ফাঁকা, কিছু লিখুন!")
                    return

                # বাংলা কোডকে Python কোডে রূপান্তর
                python_code = self.translate_to_python(bangla_code)
                print("Translated Python Code:\n", python_code)  # ডিবাগিংয়ের জন্য
                self.validate_syntax(python_code)

                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()

                # নিরাপদ এক্সিকিউশন এনভায়রনমেন্ট
                safe_env = {
                    '__builtins__': {
                        'print': print,
                        'str': str,
                        'int': int,
                        'float': float,
                        'bool': bool,
                        'range': range
                    },
                    'True': True,
                    'False': False
                }

                exec(python_code, safe_env)
                sys.stdout = old_stdout
                output = mystdout.getvalue()

                # শুধু আউটপুট দেখাও, ভেরিয়েবল তালিকা নয়
                self.show_output(output)
                self.status_bar.config(text="কোড সফলভাবে রান হয়েছে")
            except Exception as e:
                self.show_error(f"কোড এক্সিকিউশন ত্রুটি:\n{str(e)}")

        def timeout():
            self.show_error("কোড নির্বাহ খুব দীর্ঘ সময় নিচ্ছে\nসম্ভবত ইনফিনিটি লুপ")

        # Timer এবং Thread চালু করো
        t = threading.Thread(target=execute)
        t.daemon = True
        t.start()

    def timeout_handler(self, signum, frame):
        raise TimeoutError("কোড নির্বাহ খুব দীর্ঘ সময় নিচ্ছে")

    def validate_syntax(self, code):
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            error_msg = f"সিনট্যাক্স ত্রুটি:\n{e.msg}\nলাইন {e.lineno}"
            if e.text:
                error_msg += f"\n{e.text.strip()}"
            raise SyntaxError(error_msg) from e

    def translate_to_python(self, bangla_code):
        # বাংলা সংখ্যা ইংরেজিতে রূপান্তর
        bangla_to_eng_numbers = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
        bangla_code = bangla_code.translate(bangla_to_eng_numbers)

        # বাংলা কীওয়ার্ড ট্রান্সলেশন টেবিল
        translations = {
            'ধরি': '',
            'দেখাও': 'print',
            'যদি': 'if',
            'হয়': '',
            'নাহলে': 'else',
            'যতক্ষণ': 'while',
            'এবং': 'and',
            'বা': 'or',
            'না': 'not',
            'সত্য': 'True',
            'মিথ্যা': 'False'
        }

        python_lines = []
        in_block = False

        for line in bangla_code.split('\n'):
            original_line = line
            stripped_line = line.strip()

            if not stripped_line:
                python_lines.append('')
                continue

            if stripped_line.startswith('#'):
                python_lines.append(original_line)
                continue

            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 4

            # ধরি বাদ দেওয়া
            if stripped_line.startswith("ধরি "):
                translated_line = stripped_line.replace("ধরি ", "", 1)
            else:
                translated_line = stripped_line

            # কীওয়ার্ড ট্রান্সলেট করা
            for bangla, python in translations.items():
                translated_line = translated_line.replace(bangla, python)

            # যদি ... হয়: এর জন্য নিয়ম
            translated_line = re.sub(r'যদি (.*) হয়:', r'if \1:', translated_line)

            # দেখাও এর জন্য সাধারণ নিয়ম (ইন্টিজার এবং স্ট্রিং হ্যান্ডল করতে)
            translated_line = re.sub(r'দেখাও\((.*?)\)', r'print(\1)', translated_line)

            if translated_line in ('else:', 'elif:', 'except:', 'finally:'):
                indent_level = max(0, indent_level - 1)

            python_lines.append('    ' * indent_level + translated_line)

            if translated_line.endswith(':'):
                in_block = True
            elif not stripped_line:
                in_block = False

        return '\n'.join(python_lines)

    def convert_to_bangla_digits(self, text):
        eng_to_bangla_numbers = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
        return text.translate(eng_to_bangla_numbers)

    def show_output(self, text):
        # বাংলা সংখ্যায় রূপান্তর
        text = self.convert_to_bangla_digits(text)
        # রান সম্পন্ন বার্তা যোগ
        text = text.rstrip() + "\n\n============বাংলা কম্পাইলার দিয়ে রান সম্পন্ন হয়েছে============="
        self.output_display.config(state='normal')
        self.output_display.delete('1.0', tk.END)
        self.output_display.insert('1.0', text)
        self.output_display.config(state='disabled')

    def show_error(self, error_msg):
        error_msg = self.convert_to_bangla_digits(error_msg)
        self.output_display.config(state='normal')
        self.output_display.delete('1.0', tk.END)
        self.output_display.insert('1.0', error_msg)
        self.output_display.config(state='disabled')
        self.status_bar.config(text="কোডে ত্রুটি পাওয়া গেছে")

if __name__ == "__main__":
    root = tk.Tk()
    compiler = BanglaCompiler(root)
    root.mainloop()