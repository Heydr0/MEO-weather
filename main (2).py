import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.filename = "weather_data.json"
        self.records = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Температура:").grid(row=1, column=0, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=2, pady=5)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(filter_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Температура выше:").grid(row=1, column=0, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.filter_records).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(filter_frame, text="Показать все", command=self.show_all).grid(row=2, column=1, padx=5, pady=5)

        table_frame = ttk.Frame(self.root)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=200)
        self.tree.column("precipitation", width=80)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def validate_input(self, date_str, temp_str, desc):
        if not desc.strip():
            return "Описание не должно быть пустым."
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            return "Неверный формат даты. Используйте ДД.ММ.ГГГГ."
        try:
            float(temp_str)
        except ValueError:
            return "Температура должна быть числом."
        return None

    def add_record(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        error = self.validate_input(date_str, temp_str, desc)
        if error:
            messagebox.showerror("Ошибка ввода", error)
            return

        temperature = float(temp_str)
        record = {
            "date": date_str,
            "temperature": temperature,
            "description": desc,
            "precipitation": precip
        }
        self.records.append(record)
        self.update_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def update_table(self, records=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = records if records is not None else self.records
        for rec in data:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(rec["date"], rec["temperature"], rec["description"], precip_text))

    def filter_records(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if date_filter:
            try:
                datetime.strptime(date_filter, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре.")
                return
            filtered = [r for r in filtered if r["date"] == date_filter]

        if temp_filter:
            try:
                threshold = float(temp_filter)
            except ValueError:
                messagebox.showerror("Ошибка", "Температурный порог должен быть числом.")
                return
            filtered = [r for r in filtered if r["temperature"] > threshold]

        self.update_table(filtered)

    def show_all(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def save_data(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_data(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Некорректный формат данных.")
            for item in data:
                if not all(k in item for k in ("date", "temperature", "description", "precipitation")):
                    raise ValueError("Запись не содержит всех ключей.")
                try:
                    datetime.strptime(item["date"], "%d.%m.%Y")
                    float(item["temperature"])
                except (ValueError, TypeError):
                    raise ValueError("Некорректные данные в файле.")
            self.records = data
            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()