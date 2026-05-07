import customtkinter as ctk
from tkinter import filedialog, messagebox
import PyPDF2
import os

class BatchPDFMerger(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Конвейер объединения PDF")
        self.geometry("600x500")
        
        self.batches = []  # Список списков путей к файлам
        self.current_batch_index = 0
        self.total_batches_needed = 0
        self.current_files = []

        # --- Слой 1: Настройка количества циклов ---
        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.setup_frame, text="Сколько итоговых PDF файлов нужно создать?", font=("Arial", 16)).pack(pady=10)
        self.cycles_entry = ctk.CTkEntry(self.setup_frame, width=100)
        self.cycles_entry.insert(0, "3")
        self.cycles_entry.pack(pady=5)

        self.btn_start_config = ctk.CTkButton(self.setup_frame, text="Настроить файлы для каждого цикла", command=self.prepare_configuration)
        self.btn_start_config.pack(pady=20)

        # --- Слой 2: Выбор файлов для конкретного цикла ---
        self.config_frame = ctk.CTkFrame(self)
        
        self.config_label = ctk.CTkLabel(self.config_frame, text="", font=("Arial", 14, "bold"))
        self.config_label.pack(pady=10)

        self.btn_select_for_batch = ctk.CTkButton(self.config_frame, text="Выбрать PDF для этого цикла", command=self.select_files_for_current_batch)
        self.btn_select_for_batch.pack(pady=10)

        self.batch_files_list = ctk.CTkTextbox(self.config_frame, width=500, height=150)
        self.batch_files_list.pack(pady=10)

        self.btn_next_batch = ctk.CTkButton(self.config_frame, text="Следующий цикл", command=self.next_batch, state="disabled")
        self.btn_next_batch.pack(pady=10)

    def prepare_configuration(self):
        """Переход к настройке каждого цикла"""
        try:
            self.total_batches_needed = int(self.cycles_entry.get())
            if self.total_batches_needed < 1: 
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число больше 0")
            return

        self.batches = []
        self.current_batch_index = 0
        self.setup_frame.pack_forget()
        self.config_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.update_config_ui()

    def update_config_ui(self):
        """Обновление текста и состояния кнопок"""
        self.config_label.configure(text=f"Настройка итогового файла №{self.current_batch_index + 1} из {self.total_batches_needed}")
        self.batch_files_list.delete("0.0", "end")
        self.btn_next_batch.configure(state="disabled")
        
        if self.current_batch_index == self.total_batches_needed - 1:
            self.btn_next_batch.configure(text="Завершить настройку и начать", fg_color="green")
        else:
            self.btn_next_batch.configure(text="Следующий цикл", fg_color=["#3B8ED0", "#1F6AA5"])

    def select_files_for_current_batch(self):
        """Выбор файлов для текущего пакета"""
        files = filedialog.askopenfilenames(title=f"Выберите PDF для файла №{self.current_batch_index + 1}", filetypes=[("PDF", "*.pdf")])
        if files:
            self.current_files = list(files)
            self.batch_files_list.delete("0.0", "end")
            self.batch_files_list.insert("0.0", "\n".join([os.path.basename(f) for f in self.current_files]))
            self.btn_next_batch.configure(state="normal")

    def next_batch(self):
        """Сохранение текущего набора и переход дальше"""
        self.batches.append(self.current_files)
        
        if self.current_batch_index < self.total_batches_needed - 1:
            self.current_batch_index += 1
            self.update_config_ui()
        else:
            self.confirm_and_run()

    def confirm_and_run(self):
        """Финальное подтверждение и выполнение объединения"""
        summary = "\n".join([f"Файл {i+1}: {len(files)} шт." for i, files in enumerate(self.batches)])
        confirm = messagebox.askyesno("Подтверждение", f"Настроено циклов: {len(self.batches)}\n\n{summary}\n\nНачать объединение?")
        
        if confirm:
            output_dir = filedialog.askdirectory(title="Куда сохранить результат?")
            if not output_dir: 
                return

            try:
                for i, files_to_merge in enumerate(self.batches):
                    merger = PyPDF2.PdfMerger()
                    for path in files_to_merge:
                        merger.append(path)
                    
                    out_path = os.path.join(output_dir, f"result_batch_{i+1}.pdf")
                    with open(out_path, 'wb') as f:
                        merger.write(f)
                    merger.close()

                messagebox.showinfo("Готово", f"Успешно создано {len(self.batches)} файлов в папке:\n{output_dir}")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка при сохранении", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    app = BatchPDFMerger()
    app.mainloop()