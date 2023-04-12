import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import defaultdict

class VirtualFlashApp:
    def __init__(self, flash_data, flash_cmd_history):
        self.root = tk.Tk()
        self.root.title("Virtual Flash")

        self.history_data = flash_cmd_history

        self.log_index = 0

        # create a label for current time
        self.time_label = ttk.Label(self.root, text="Current Time: ")
        self.time_label.grid(row=0, column=0, sticky="w")

        # create a label for showing logs
        self.logs_label = ttk.Label(self.root, text="Logs: ")
        self.logs_label.grid(row=1, column=0, sticky="w")

        # create a text box to display logs
        self.logs_text = scrolledtext.ScrolledText(self.root, height=10, width=50, state="disabled")
        self.logs_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        # disable manual changes to the logs text

        # create a label for address input filter
        self.address_filter_label = ttk.Label(self.root, text="Filter by address: ")
        self.address_filter_label.grid(row=3, column=0, sticky="w")
        # create an entry box for address input filter
        self.address_filter_entry = ttk.Entry(self.root)
        self.address_filter_entry.grid(row=3, column=1, sticky="w")

        # create a label for data input filter
        self.data_filter_label = ttk.Label(self.root, text="Filter by data: ")
        self.data_filter_label.grid(row=4, column=0, sticky="w")
        # create an entry box for data input filter
        self.data_filter_entry = ttk.Entry(self.root)
        self.data_filter_entry.grid(row=4, column=1, sticky="w", pady=2)

        # create a show button
        self.show_button = ttk.Button(self.root, text="Show", command=self.show_filtered_data)
        self.show_button.grid(row=4, column=2, padx=10)

        # create a label for current time
        self.user_label = ttk.Label(self.root, text="\n\nUser Manual control")
        self.user_label.grid(row=5, column=0, sticky="w")

        # create a label for address input
        self.address_label = ttk.Label(self.root, text="Address in hex without 0x: ")
        self.address_label.grid(row=6, column=0, sticky="w", pady=5)
        # create an entry box for address input
        self.address_entry = ttk.Entry(self.root)
        self.address_entry.grid(row=6, column=1, sticky="w", pady=5)

         # create a label for length input
        self.length_label = ttk.Label(self.root, text="Length in hex without 0x: ")
        self.length_label.grid(row=7, column=0, sticky="w", pady=5)
        # create an entry box for length input
        self.length_entry = ttk.Entry(self.root)
        self.length_entry.grid(row=7, column=1, sticky="w", pady=5)


        # create a label for data input
        self.data_label = ttk.Label(self.root, text="Data in hex without 0x: ")
        self.data_label.grid(row=8, column=0, sticky="w", pady=5)
        # create an entry box for data input
        self.data_entry = ttk.Entry(self.root)
        self.data_entry.grid(row=8, column=1, sticky="w", pady=5)

        # create a read button
        self.read_button = ttk.Button(self.root, text="Read", command=self.gui_read)
        self.read_button.grid(row=7, column=2)


        # create a write button
        self.write_button = ttk.Button(self.root, text="Write", command=self.gui_write)
        self.write_button.grid(row=8, column=2, pady=2)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Address')
        self.ax.set_ylabel('Write Count')
        self.ax.set_title('Write History by Address')

        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.plot_canvas.get_tk_widget().grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.plot_canvas, self.root, pack_toolbar=False)
        toolbar.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")


        self.plot_thread = threading.Thread(target=self.plot_data)
        self.plot_thread.daemon = True
        self.plot_thread.start()

        self.log_thread = threading.Thread(target=self.update_logs)
        self.log_thread.daemon = True
        self.log_thread.start()
        

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def gui_write(self):
        pass

    def gui_read(self):

        data = ""

        # create a new window
        window = tk.Toplevel()
        window.title("Read Result")

        # create a treeview widget
        tree = ttk.Treeview(window, columns=("Address", "Data", "TimeStamp"), show=["headings"])
        tree.heading("Address", text="Address")
        tree.heading("Data", text="Data")
        tree.heading("TimeStamp", text="TimeStamp")
        tree.pack(fill="both", expand=True)
        # insert the data into the treeview
        for address, (value, timestamp) in data.items():
            address_hex = hex(address)
            value_hex = hex(value)
            tree.insert("", tk.END, values=(address_hex, value_hex, timestamp))

    def get_current_time(self):
        # get current time and format it
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current_time

    def update_vscroll(self):
        # check if current scroll position is at the end of the text box
        _, y_end = self.logs_text.yview()
        if y_end > 0.9:
            # scroll to the bottom of the plot
            self.logs_text.yview(tk.END)

    def show_filtered_data(self):

        address = 0
        data = 0

        print(address)
        print(data)

        #TODO add it to a tree

    def update_history(self):
        # plot history data
        addresses = defaultdict(int)
        for data in self.history_data:
            if "Write" in data:
                address = data.split(',')[0].split(':')[-1].strip()
                addresses[address] += 1

        # check if zoom or pan mode is active
        nav_toolbar = self.plot_canvas.toolbar
        is_zoomed = nav_toolbar.mode == 'zoom rect'
        is_panned = nav_toolbar.mode == 'pan/zoom'

        if not is_zoomed and not is_panned:
            self.ax.clear()
            x = [int(addr, 16) for addr in addresses.keys()] # convert keys to integer
            y = list(addresses.values())
            for xi, yi in zip(x, y):
                self.ax.vlines(x=xi, ymin=0, ymax=yi, linewidth=2)
                self.ax.text(xi, yi+0.001, str(yi), ha='center')

            self.ax.set_xlabel('Address')
            self.ax.set_ylabel('Write Count')
            self.ax.set_title('Write History by Address')
            self.plot_canvas.draw()

    def plot_data(self):
        while True:
            time.sleep(2)
            self.update_history()

    def update_time(self):
        # update time label with current time
        current_time = self.get_current_time()
        self.time_label.config(text="Current Time: " + current_time)

        # schedule next update after 1 second
        self.root.after(1000, self.update_time)

    def update_logs(self):
        # clear index log, first time run we need to go trough the complete list
        self.log_index = 0
        logs_str = ""
        while True:
            if self.log_index == 0:
                # Convert the logs list to a string
                logs_str = "\n".join(self.history_data)
            else:
                logs_str = "\n".join(self.history_data[self.log_index:])

            self.log_index = len(self.history_data)


            # Insert the logs into the `logs_text` widget
            self.logs_text.config(state="normal")
            self.logs_text.insert(tk.END, logs_str + "\n")
            self.logs_text.config(state="disabled")
            self.update_vscroll()
            time.sleep(1)

    def close_app(self):
        """Stops the mainloop and any running threads before closing the GUI"""
        self.running = False  # set running flag to False to stop any running threads
        self.root.quit()     # stop the mainloop
