import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

class CPUScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.configure(bg="#2c3e50")

        tk.Label(root, text="CPU Scheduling Simulator", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=10)

        tk.Label(root, text="Enter Number of Processes:", fg="white", bg="#2c3e50").pack()
        self.process_count_entry = tk.Entry(root, width=10)
        self.process_count_entry.pack()
        tk.Button(root, text="Set Processes", command=self.create_process_entries, bg="#3498db", fg="white").pack(pady=5)

        self.process_frame = tk.Frame(root, bg="#2c3e50")
        self.process_frame.pack()

        tk.Label(root, text="Choose Scheduling Algorithm:", fg="white", bg="#2c3e50").pack()
        self.algorithm = tk.StringVar()
        self.algorithm.set("FCFS")

        algorithms = ["FCFS", "SJF", "Priority", "Round Robin"]
        for algo in algorithms:
            tk.Radiobutton(root, text=algo, variable=self.algorithm, value=algo, bg="#2c3e50", fg="white", command=self.toggle_fields).pack()

        self.quantum_label = tk.Label(root, text="Enter Time Quantum (Only for Round Robin):", fg="white", bg="#2c3e50")
        self.quantum_entry = tk.Entry(root, width=10)

        tk.Button(root, text="Run Simulation", command=self.run_simulation, bg="#27ae60", fg="white", font=("Arial", 12)).pack(pady=5)

        self.result_frame = tk.Frame(root, bg="#2c3e50")
        self.result_frame.pack()

    def create_process_entries(self):
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        try:
            self.num_processes = int(self.process_count_entry.get())
            if self.num_processes <= 0:
                raise ValueError("Number of processes must be positive.")

            headers = ["Process", "Arrival Time", "Burst Time", "Priority"]
            for i, header in enumerate(headers):
                tk.Label(self.process_frame, text=header, fg="white", bg="#2c3e50").grid(row=0, column=i, padx=10)

            self.process_names = []
            self.arrival_entries = []
            self.burst_entries = []
            self.priority_entries = []

            for i in range(self.num_processes):
                process_name = f"P{i+1}"
                self.process_names.append(process_name)

                tk.Label(self.process_frame, text=process_name, fg="white", bg="#2c3e50").grid(row=i+1, column=0)
                at_entry = tk.Entry(self.process_frame, width=10)
                bt_entry = tk.Entry(self.process_frame, width=10)
                pr_entry = tk.Entry(self.process_frame, width=10)

                at_entry.grid(row=i+1, column=1, padx=10)
                bt_entry.grid(row=i+1, column=2, padx=10)
                pr_entry.grid(row=i+1, column=3, padx=10)

                self.arrival_entries.append(at_entry)
                self.burst_entries.append(bt_entry)
                self.priority_entries.append(pr_entry)

            self.toggle_fields()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def toggle_fields(self):
        if self.algorithm.get() == "Priority":
            for entry in self.priority_entries:
                entry.config(state="normal")
        else:
            for entry in self.priority_entries:
                entry.config(state="disabled")

        if self.algorithm.get() == "Round Robin":
            self.quantum_label.pack()
            self.quantum_entry.pack()
        else:
            self.quantum_label.pack_forget()
            self.quantum_entry.pack_forget()

    def run_simulation(self):
        try:
            burst_times = [int(bt.get()) for bt in self.burst_entries]
            arrival_times = [int(at.get()) for at in self.arrival_entries]
            priorities = [int(pr.get()) if self.algorithm.get() == "Priority" else 0 for pr in self.priority_entries]

            process_data = list(zip(self.process_names, arrival_times, burst_times, priorities))

            if self.algorithm.get() == "Round Robin":
                quantum = int(self.quantum_entry.get())
                if quantum <= 0:
                    raise ValueError("Time quantum must be positive.")

            if self.algorithm.get() == "FCFS":
                self.fcfs(process_data)
            elif self.algorithm.get() == "SJF":
                self.sjf(process_data)
            elif self.algorithm.get() == "Priority":
                self.priority_scheduling(process_data)
            elif self.algorithm.get() == "Round Robin":
                self.round_robin(process_data, quantum)

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def fcfs(self, process_data):
        sorted_processes = sorted(process_data, key=lambda x: x[1])
        self.calculate_and_display(sorted_processes)

    def sjf(self, process_data):
        process_data.sort(key=lambda x: (x[1], x[2]))  # Sort by arrival time and burst time
        n = len(process_data)
        remaining_time = [p[2] for p in process_data]
        completion_time = [0] * n
        waiting_time = [0] * n
        turnaround_time = [0] * n
        ready_queue = []
        time = 0
        completed = 0

        while completed < n:
            # Add processes to ready queue based on their arrival time
            for i in range(n):
                if process_data[i][1] <= time and remaining_time[i] > 0 and i not in ready_queue:
                    ready_queue.append(i)

            if not ready_queue:
                time += 1
                continue

            # Sort the ready queue by remaining time (SJF)
            ready_queue.sort(key=lambda i: remaining_time[i])
            index = ready_queue.pop(0)

            # Execute the selected process
            time += remaining_time[index]
            remaining_time[index] = 0
            completion_time[index] = time
            turnaround_time[index] = completion_time[index] - process_data[index][1]
            waiting_time[index] = turnaround_time[index] - process_data[index][2]
            completed += 1

        # Calculate averages
        avg_wt = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        
        # Sorting processes back by their original order
        sorted_by_process = sorted(zip(process_data, completion_time, turnaround_time, waiting_time), key=lambda x: int(x[0][0][1:]))
        sorted_processes, completion_time, turnaround_time, waiting_time = zip(*sorted_by_process)
        
        self.display_table(sorted_processes, completion_time, waiting_time, turnaround_time)
        self.plot_gantt_chart([ct - bt for ct, bt in zip(completion_time, [p[2] for p in sorted_processes])], 
                            completion_time, n, sorted_processes)
        
        messagebox.showinfo("Results", f"Avg Waiting Time: {avg_wt:.2f}\nAvg Turnaround Time: {avg_tat:.2f}")

    def priority_scheduling(self, process_data):
        # Sort by priority (lower number = higher priority), then by arrival time
        process_data.sort(key=lambda x: (x[3], x[1]))
        
        n = len(process_data)
        remaining_time = [p[2] for p in process_data]
        arrival_time = [p[1] for p in process_data]
        completion_time = [0] * n
        waiting_time = [0] * n
        turnaround_time = [0] * n
        time = 0
        
        while True:
            # Find the highest priority process that has arrived and has remaining time
            selected = None
            for i in range(n):
                if arrival_time[i] <= time and remaining_time[i] > 0:
                    if selected is None or process_data[i][3] < process_data[selected][3]:
                        selected = i
            
            if selected is None:
                # No process available, advance time
                time += 1
                continue
            
            # Execute the selected process to completion (non-preemptive)
            time += remaining_time[selected]
            completion_time[selected] = time
            remaining_time[selected] = 0
            turnaround_time[selected] = completion_time[selected] - arrival_time[selected]
            waiting_time[selected] = turnaround_time[selected] - process_data[selected][2]
            
            # Check if all processes are completed
            if all(rt == 0 for rt in remaining_time):
                break
        
        # Calculate averages
        avg_wt = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        
        # Sorting processes back by their original order
        sorted_by_process = sorted(zip(process_data, completion_time, turnaround_time, waiting_time), 
                                 key=lambda x: int(x[0][0][1:]))
        sorted_processes, completion_time, turnaround_time, waiting_time = zip(*sorted_by_process)
        
        self.display_table(sorted_processes, completion_time, waiting_time, turnaround_time)
        self.plot_gantt_chart([ct - bt for ct, bt in zip(completion_time, [p[2] for p in sorted_processes])], 
                             completion_time, n, sorted_processes)
        
        messagebox.showinfo("Results", f"Avg Waiting Time: {avg_wt:.2f}\nAvg Turnaround Time: {avg_tat:.2f}")

    def round_robin(self, process_data, quantum):
        n = len(process_data)
        remaining_time = [p[2] for p in process_data]
        arrival_time = [p[1] for p in process_data]
        completion_time = [0] * n
        waiting_time = [0] * n
        turnaround_time = [0] * n
        ready_queue = deque()
        time = 0
        completed = 0
        
        # Initialize ready queue with processes that have arrived at time 0
        for i in range(n):
            if arrival_time[i] == 0:
                ready_queue.append(i)
        
        # To track when each process was last added to the queue
        last_added = [-1] * n
        
        while completed < n:
            if not ready_queue:
                time += 1
                # Check for new arrivals
                for i in range(n):
                    if arrival_time[i] == time and remaining_time[i] > 0 and i not in ready_queue and last_added[i] != time:
                        ready_queue.append(i)
                        last_added[i] = time
                continue
            
            current_process = ready_queue.popleft()
            
            # Execute the process for quantum or remaining time, whichever is smaller
            exec_time = min(quantum, remaining_time[current_process])
            time += exec_time
            remaining_time[current_process] -= exec_time
            
            # Check for new arrivals during this execution
            for i in range(n):
                if arrival_time[i] <= time and remaining_time[i] > 0 and i not in ready_queue and i != current_process and last_added[i] != time:
                    ready_queue.append(i)
                    last_added[i] = time
            
            if remaining_time[current_process] == 0:
                completion_time[current_process] = time
                turnaround_time[current_process] = completion_time[current_process] - arrival_time[current_process]
                waiting_time[current_process] = turnaround_time[current_process] - process_data[current_process][2]
                completed += 1
            else:
                ready_queue.append(current_process)
        
        # Calculate averages
        avg_wt = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        
        # Sorting processes back by their original order
        sorted_by_process = sorted(zip(process_data, completion_time, turnaround_time, waiting_time), key=lambda x: int(x[0][0][1:]))
        sorted_processes, completion_time, turnaround_time, waiting_time = zip(*sorted_by_process)
        
        self.display_table(sorted_processes, completion_time, waiting_time, turnaround_time)
        
        # For RR, we'll show a simplified Gantt chart (more complex to show all context switches)
        self.plot_gantt_chart([ct - bt for ct, bt in zip(completion_time, [p[2] for p in sorted_processes])], 
                            completion_time, n, sorted_processes)
        
        messagebox.showinfo("Results", f"Avg Waiting Time: {avg_wt:.2f}\nAvg Turnaround Time: {avg_tat:.2f}")

    def calculate_and_display(self, sorted_processes):
        n = len(sorted_processes)
        waiting_time = [0] * n
        turnaround_time = [0] * n
        completion_time = [0] * n
        start_time = [0] * n
        end_time = [0] * n

        completion_time[0] = sorted_processes[0][1] + sorted_processes[0][2]
        for i in range(1, n):
            completion_time[i] = max(completion_time[i-1], sorted_processes[i][1]) + sorted_processes[i][2]

        for i in range(n):
            turnaround_time[i] = completion_time[i] - sorted_processes[i][1]
            waiting_time[i] = turnaround_time[i] - sorted_processes[i][2]
            start_time[i] = waiting_time[i] + sorted_processes[i][1]
            end_time[i] = completion_time[i]

        avg_wt = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n

        self.plot_gantt_chart(start_time, end_time, n, sorted_processes)
        self.display_table(sorted_processes, completion_time, waiting_time, turnaround_time)

        messagebox.showinfo("Results", f"Avg Waiting Time: {avg_wt:.2f}\nAvg Turnaround Time: {avg_tat:.2f}")

    def display_table(self, sorted_processes, completion_time, waiting_time, turnaround_time):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        headers = ["Process", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time"]
        table = ttk.Treeview(self.result_frame, columns=headers, show="headings", height=8)

        for header in headers:
            table.heading(header, text=header)
            table.column(header, width=100, anchor="center")

        for i, process in enumerate(sorted_processes):
            table.insert("", "end", values=(process[0], process[1], process[2], completion_time[i], turnaround_time[i], waiting_time[i]))

        table.pack()

    def plot_gantt_chart(self, start, end, n, sorted_processes):
        colors = plt.cm.tab10(np.linspace(0, 1, n))
        fig, ax = plt.subplots(figsize=(10, 2))

        for i in range(n):
            ax.barh(0, end[i] - start[i], left=start[i], color=colors[i], edgecolor="black", height=0.8)
            ax.text(start[i] + (end[i] - start[i]) / 2, 0, sorted_processes[i][0], ha='center', va='center', color='white', fontsize=12, fontweight='bold')

        ax.set_yticks([0])
        ax.set_xlabel("Time")
        ax.set_title("Gantt Chart")
        plt.tight_layout()
        plt.show()

root = tk.Tk()
scheduler = CPUScheduler(root)
root.mainloop()
