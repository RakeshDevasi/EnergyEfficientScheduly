import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class EnergyEfficientScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy Efficient CPU Scheduling")
        
        self.processes = []
        
        tk.Label(root, text="Number of Processes:").grid(row=0, column=0)
        self.num_processes_entry = tk.Entry(root)
        self.num_processes_entry.grid(row=0, column=1)
        
        tk.Button(root, text="Enter", command=self.get_process_details).grid(row=0, column=2)
        
    def get_process_details(self):
        try:
            self.num_processes = int(self.num_processes_entry.get())
            if self.num_processes <= 0:
                raise ValueError
            
            self.process_entries = []
            self.labels = ["Process ID", "Arrival Time", "Burst Time"]
            
            for j, label in enumerate(self.labels):
                tk.Label(self.root, text=label).grid(row=1, column=j)
            
            for i in range(self.num_processes):
                entry_row = []
                tk.Label(self.root, text=f"P{i+1}").grid(row=i+2, column=0)
                
                for j in range(1, 3):
                    entry = tk.Entry(self.root)
                    entry.grid(row=i+2, column=j)
                    entry_row.append(entry)
                
                self.process_entries.append(entry_row)
            
            tk.Button(self.root, text="Schedule", command=self.schedule_processes).grid(row=self.num_processes+2, column=1)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of processes.")
    
    def schedule_processes(self):
        self.processes = []
        
        for i, entries in enumerate(self.process_entries):
            try:
                arrival_time = int(entries[0].get())
                burst_time = int(entries[1].get())
                self.processes.append((i+1, arrival_time, burst_time))
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numerical values.")
                return
        
        self.processes.sort(key=lambda x: (x[1], x[2]))
        self.calculate_scheduling()
        self.display_results()
    
    def calculate_scheduling(self):
        self.waiting_times = {}
        self.turnaround_times = {}
        self.completion_times = {}
        self.energy_consumption = 0
        
        time = 0
        base_energy_unit = 1.5  # Base energy per cycle
        
        for pid, arrival, burst in self.processes:
            start_time = max(time, arrival)
            waiting_time = start_time - arrival
            turnaround_time = waiting_time + burst
            completion_time = start_time + burst
            
            self.waiting_times[pid] = waiting_time
            self.turnaround_times[pid] = turnaround_time
            self.completion_times[pid] = completion_time
            
            dynamic_energy = base_energy_unit * (0.8 if burst > 5 else 1.2)  # DVFS-based energy scaling
            self.energy_consumption += burst * dynamic_energy
            
            time = completion_time
        
        self.avg_waiting_time = sum(self.waiting_times.values()) / len(self.processes)
        self.avg_turnaround_time = sum(self.turnaround_times.values()) / len(self.processes)
    
    def display_results(self):
        # Frame for results
        results_frame = tk.Frame(self.root)
        results_frame.grid(row=self.num_processes+3, column=0, columnspan=3, pady=10)

        # Show average times
        avg_label = tk.Label(results_frame, text=f"Average Waiting Time: {self.avg_waiting_time:.2f} | Average Turnaround Time: {self.avg_turnaround_time:.2f}")
        avg_label.grid(row=0, column=0, padx=10)

        # Show total energy consumption
        energy_label = tk.Label(results_frame, text=f"Total Energy Consumption: {self.energy_consumption:.2f} units")
        energy_label.grid(row=0, column=1, padx=10)

        # Display the Gantt Chart
        self.display_gantt_chart(results_frame)

        # Display results table
        self.display_results_table(results_frame)
    
    def display_gantt_chart(self, frame):
        fig, ax = plt.subplots(figsize=(8, 2))
        start_time = 0
        
        colors = plt.cm.get_cmap("tab10", len(self.processes))
        
        for i, (pid, arrival, burst) in enumerate(self.processes):
            start_time = max(start_time, arrival)
            ax.barh("Process", burst, left=start_time, color=colors(i), label=f"P{pid}")
            start_time += burst
        
        ax.set_xlabel("Time")
        ax.set_title("Gantt Chart - Energy Efficient Scheduling")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=10)
        canvas.draw()
    
    def display_results_table(self, frame):
        columns = ("Process", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time")
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for pid, arrival, burst in self.processes:
            tree.insert("", tk.END, values=(pid, arrival, burst, self.completion_times[pid], self.turnaround_times[pid], self.waiting_times[pid]))
        
        tree.grid(row=2, column=0, columnspan=3, pady=10, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyEfficientScheduler(root)
    root.mainloop()
