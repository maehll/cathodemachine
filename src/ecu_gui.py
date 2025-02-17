import tkinter as tk
from tkinter import ttk
import asyncio
from datetime import datetime
import threading
from queue import Queue

class KathodenmaschinenGUI:
    def __init__(self, ecu_client, root=None):
        self.root = root if root else tk.Tk()
        self.root.title("Kathodenmaschinen Monitor")
        self.ecu_client = ecu_client
        self.data_queue = Queue()
        
        # GUI in Bereiche aufteilen
        self.create_threshold_frame()
        self.create_data_frame()
        self.create_warning_frame()
        
        # Periodische GUI-Aktualisierung
        self.root.after(100, self.update_gui)
    
    def create_threshold_frame(self):
        threshold_frame = ttk.LabelFrame(self.root, text="Schwellwerte", padding="5")
        threshold_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Schwellwert-Einstellungen
        row = 0
        self.threshold_vars = {}
        for key, value in self.ecu_client.schwellwerte.items():
            ttk.Label(threshold_frame, text=value["beschreibung"]).grid(row=row, column=0, sticky="w")
            
            min_var = tk.StringVar(value=str(value["min"]))
            max_var = tk.StringVar(value=str(value["max"]))
            
            ttk.Label(threshold_frame, text="Min:").grid(row=row, column=1)
            min_entry = ttk.Entry(threshold_frame, textvariable=min_var, width=8)
            min_entry.grid(row=row, column=2)
            
            ttk.Label(threshold_frame, text="Max:").grid(row=row, column=3)
            max_entry = ttk.Entry(threshold_frame, textvariable=max_var, width=8)
            max_entry.grid(row=row, column=4)
            
            self.threshold_vars[key] = {"min": min_var, "max": max_var}
            
            # Update-Funktion für Schwellwerte
            def update_threshold(key=key):
                try:
                    min_val = int(self.threshold_vars[key]["min"].get())
                    max_val = int(self.threshold_vars[key]["max"].get())
                    self.ecu_client.schwellwerte[key]["min"] = min_val
                    self.ecu_client.schwellwerte[key]["max"] = max_val
                except ValueError:
                    pass
            
            ttk.Button(threshold_frame, text="Aktualisieren", 
                      command=update_threshold).grid(row=row, column=5)
            row += 1

    def create_data_frame(self):
        data_frame = ttk.LabelFrame(self.root, text="Aktuelle Daten", padding="5")
        data_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Scrollbare Textbox für Daten
        self.data_text = tk.Text(data_frame, height=20, width=40)
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", 
                                command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=scrollbar.set)
        
        self.data_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_warning_frame(self):
        warning_frame = ttk.LabelFrame(self.root, text="Warnungen", padding="5")
        warning_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Scrollbare Textbox für Warnungen
        self.warning_text = tk.Text(warning_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(warning_frame, orient="vertical", 
                                command=self.warning_text.yview)
        self.warning_text.configure(yscrollcommand=scrollbar.set)
        
        self.warning_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Warntext rot einfärben
        self.warning_text.tag_configure("warning", foreground="red")

    def update_gui(self):
        # Daten aus der Queue verarbeiten
        while not self.data_queue.empty():
            data_type, content = self.data_queue.get()
            
            if data_type == "data":
                self.data_text.delete(1.0, tk.END)
                for key, value in content.items():
                    self.data_text.insert(tk.END, f"{key}: {value}\n")
            
            elif data_type == "warnings":
                self.warning_text.delete(1.0, tk.END)
                for warning in content:
                    self.warning_text.insert(tk.END, f"{warning}\n", "warning")
        
        self.root.after(100, self.update_gui)

    def add_data(self, data_type, content):
        self.data_queue.put((data_type, content))

    def run(self):
        self.root.mainloop() 