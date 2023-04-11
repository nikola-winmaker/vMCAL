import ctypes
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import defaultdict
import threading
import queue
import sqlite3

class VirtualFlashApp:
    def __init__(self, num_sectors=4, num_pages=5, page_size=1024):
        self.root = tk.Tk()
        self.root.title("Virtual Flash")

        self.num_sectors = num_sectors
        self.num_pages = num_pages
        self.page_size = page_size
        self.sector_size = num_pages * page_size
        self.flash_size = self.sector_size * self.num_sectors
        # use picle
        #self.flash = [0XFF] * self.sector_size * self.num_sectors
        #self.write_count_per_addr = defaultdict(int)

        # create a queue to store the incoming messages
        self.message_queue = queue.Queue()

        # define database
        self.db_connection = sqlite3.connect('vFlash.db', uri=True)
        # Create a row factory that returns rows as dictionaries
        self.db_connection.row_factory = sqlite3.Row
        self.db_cursor = self.db_connection.cursor()

        # Create the flash_data table if it doesn't already exist
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS flash_data (
            id INTEGER PRIMARY KEY,
            command TEXT,
            address INTEGER,
            data INTEGER,
            timestamp INTEGER
        )''')

        self.db_connection.commit()
        # write 0xff if db empty
        self.init_db()

        # msg receiving
        self.restAPI_thread = threading.Thread(target=self.C_App_Main) #_restAPI)
        self.restAPI_thread.daemon = True
        self.restAPI_thread.start()

        # Msg parsing
        self.message_thread = threading.Thread(target=self.process_messages)
        self.message_thread.daemon = True
        self.message_thread.start()

        # plot data
        self.plot_thread = threading.Thread(target=self.plot_data) #_restAPI)
        self.plot_thread.daemon = True
        self.plot_thread.start()

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
        self.write_button = ttk.Button(self.root, text="Write", command=self.write_data)
        self.write_button.grid(row=8, column=2, pady=2)

        # create a list to store history data
        self.history_data = []

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Address')
        self.ax.set_ylabel('Write Count')
        self.ax.set_title('Write History by Address')

        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.plot_canvas.get_tk_widget().grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.plot_canvas, self.root, pack_toolbar=False)
        toolbar.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def init_db(self):
        # check if table is empty
        query = "SELECT COUNT(*) FROM flash_data"
        self.db_cursor.execute(query)
        count = self.db_cursor.fetchone()[0]
        if count == 0:
            print("Empty DB, init.")
            # Create a list of addresses in the flash
            addresses = list(range(self.flash_size))
            # Begin a transaction
            for address in addresses:
                # Initialize the database with 0xff values for each address in the flash
                self.insert_element_db(self.db_connection, 'write', address, 0xFF, 0x0)

        query = "SELECT COUNT(*) FROM flash_data"
        self.db_cursor.execute(query)
        count = self.db_cursor.fetchone()[0]
        print(f"The table has {count} rows")

    def _get_db_connection(self):
            # If the current thread doesn't have a database connection, create one
            if not hasattr(self.db_connection, 'connection'):
                self.db_connection = sqlite3.connect('vFlash.db', uri=True)

            # Return the database connection for the current thread
            return self.db_connection

    def process_messages(self):
        while True:
            # get a message from the queue
            message = self.message_queue.get()

            print(f"Received message: {message.decode()}")
            topic, msg = message.decode().strip().split(":")
            print(topic, msg)
            address, data, length = msg.split(",")
            print(hex(int(address)), data, length)

            self.fls_write(hex(int(address)), data, 0)

    #TODO:
    def _restAPI(self):
        import socket, time
        # Set up the connection to the server
        host = "127.0.0.1"
        port = 8888

        while True:
            # Set up the connection to the server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    # Try to connect to the server
                    client_socket.connect((host, port))
                    break # Connection successful, break out of the loop
                except ConnectionRefusedError:
                    # Connection failed, wait one second and try again
                    print("Connection failed, trying again in 1 second...")
                    time.sleep(1)

            # Send a subscribe request for the Fls_Write topic
            subscribe_message = "SUBSCRIBE:Fls_Write"
            client_socket.send(subscribe_message.encode())


            # create a buffer to store incomplete messages
            message_buffer = ""
            # Wait for incoming messages
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # add the received data to the message buffer
                    message_buffer = data.decode()

                    
                    # split the buffer into separate messages based on the delimiter
                    messages = message_buffer.split(";")
                    print(messages)

                    # process each complete message
                    for message in messages:
                        # ignore empty messages
                        if not message:
                            continue
                        
                        print(message.encode())
                        # put the message in the queue
                        self.message_queue.put(message.encode())
                    
                    # keep any incomplete message in the buffer for the next iteration
                    message_buffer = messages[-1]
                except KeyboardInterrupt:
                    # allow the user to exit the program cleanly
                    break

                # try:
                #     message = client_socket.recv(1024)
                #     if not message:
                #         break

                #     self.message_queue.put(message)

                #     # print(f"Received message: {message.decode()}")
                #     # topic, msg = message.decode().strip().split(":")
                #     # print(topic, msg)
                #     # address, data, length = msg.split(",")
                #     # print(hex(int(address)), data, length)

                #     # self.fls_write(hex(int(address)), data, 0)

                # except ConnectionResetError:
                #     # The connection was lost, so we need to reconnect
                #     print("Connection lost, reconnecting...")
                #     break

            # Close the client socket
            client_socket.close()
        # while True:
        #     import time
        #     time.sleep(1)
        #     #print(1)
        #     self.write_data()


    def C_App_Main(self):
        # Load the DLL and import the functions you need
        dll = ctypes.CDLL('d:\\DSUsers\\uic74928\\Trainings\\Autosar_training\\tresos_Wincore\\workspace\\demoRte\\util\\\c_app.dll')
        main_func = dll.main
        main_func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
        main_func.restype = ctypes.c_int

        while True:
            fls_wr_init_redirect = dll.set_vFls_Write_callback
            fls_wr_init_redirect.argtypes = [ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)]
            fls_wr_init_redirect.restype = ctypes.c_int

            # Define the callback function in Python
            def callback(address, data):
                log = f" callback Write: Address: {hex(address)}, Data: {data}"
                print(log)
                self.fls_write(str(hex(address)), str(hex(data)), 0)

            def c_callback():
                print("C function job finished")
                import time
                time.sleep(5)

            # Define a function to be called from C application on Fls_Write
            callback_func = ctypes.CFUNCTYPE(None, ctypes.c_int,  ctypes.c_int)(callback)
            result = fls_wr_init_redirect(callback_func)
            print("other_func returned", result)

            # Run the main function in a loop
            argc = 1
            argv = [b"c_app.dll", None]
            argv_p = ctypes.c_char_p(argv[0])
            result = main_func(argc, ctypes.pointer(argv_p))
            print("DLL main returned", result)

    def get_write_count(self, db_connection, address):
        query = "SELECT COUNT(*) FROM flash_data WHERE command='write' AND address=?"
        result = db_connection.cursor().execute(query, (address,)).fetchone()

        write_count = result[0]

        print(write_count)

    def get_read_count(self, db_connection, address):
        query = "SELECT COUNT(*) FROM flash_data WHERE command='read' AND address=?"
        result = db_connection.cursor().execute(query, (address,)).fetchone()

        read_count = result[0]

        print(read_count)

    def read_all_from_querry_db(self, db_connection, element_type, value):
        # Retrieve all data from the table
        #rows = self.db_connection.execute('SELECT * FROM flash_data').fetchall()
        # Create a row factory that returns rows as dictionaries
        db_connection.row_factory = sqlite3.Row
        # Execute the query and retrieve the matching rows
        query = f"SELECT * FROM flash_data WHERE {element_type} = ?"
        rows = db_connection.execute(query, (value,)).fetchall()

        # Loop through the rows and print the sector_id and page_id values for each row
        for row in rows:
            cmd = row['command']
            ts = row['timestamp']
            data = row['data']
            addr = row['address']
            print(f"cmd {cmd}, address: {hex(addr)}, data: {hex(data)}, ts: {ts}")

    def get_last_wr_value_from_db(self, db_connection, element_type, value):

        db_connection.row_factory = sqlite3.Row
        query = f"SELECT * FROM flash_data WHERE command='write' AND {element_type}={value} ORDER BY timestamp DESC LIMIT 1"
        rows = db_connection.execute(query).fetchall()

        # print(len(rows))
        # # Loop through the rows and print the sector_id and page_id values for each row
        # for row in rows:
        #     cmd = row['command']
        #     ts = row['timestamp']
        #     data = row['data']
        #     addr = row['address']
        #     print(f"cmd {cmd}, address: {hex(addr)}, data: {hex(data)}, ts: {ts}")

        return rows[0]
    
    
    def read_range_latest_from_db(self, db_connection, address, length):
        # Use a prepared statement with placeholders
        query = "SELECT address, MAX(timestamp), data FROM flash_data WHERE command='write' AND address BETWEEN ? AND ? GROUP BY address"
        values = (address, address+length-1)
        # Execute the query
        result = db_connection.cursor().execute(query, values).fetchall()
        return result

    def get_data_for_read(db_result):
         # Print the result
        for row in db_result:
            address = row[0]
            timestamp = row[1]
            value = row[2]
            print(f"Address: {address}, Timestamp: {timestamp}, Value: {value}")

    def insert_element_db(self, db_connection, command, address, data, timestamp):
        # Insert some sample data into the table
        db_connection.cursor().execute('''INSERT INTO flash_data (
            command, address, data, timestamp
        ) VALUES (?, ?, ?, ?)''', (command, address, data, timestamp))

        # Commit the changes to the database
        db_connection.commit()

    def gui_read(self):
        # Get the database connection for the current thread
        db_connection = self._get_db_connection()

        data = self.read_data(db_connection)
        if data == "":
            data = "No adress and length requested!"
            messagebox.showinfo("Read Result", data)
            return

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

        self.get_write_count(db_connection, 0)
        self.get_read_count(db_connection, 0)

    def read_data(self, db_connection):

        # get address and length from entry boxes
        try:
            address = int(self.address_entry.get(), 16)
            length = int(self.length_entry.get(), 16)
        except:
            return ""

        # add data to logs text box
        current_time = self.get_current_time()

        if address + length > self.flash_size:
            messagebox.showinfo("Warning", "Read operation truncated!")
            length = self.flash_size - 1

        db_data_dict = {}
        db_result = self.read_range_latest_from_db(db_connection, address, length)
        for row in db_result:
            address_db = row[0]
            ts_db = row[1]
            data_db = row[2]

            #write to DB
            self.insert_element_db(db_connection, 'read', address_db, data_db, current_time)
            db_data_dict[address_db] = (data_db, ts_db)

        log = f"{current_time} - Read: Address: {hex(address)}, Length: {hex(length)}"
        self.logs_text.config(state="normal")
        self.logs_text.insert(tk.END, log + "\n")
        self.logs_text.config(state="disabled")

        # check if current scroll position is at the end of the text box
        self.update_vscroll()

        return db_data_dict

    def get_current_time(self):
        # get current time and format it
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current_time

    def write_data(self, address, data, length):
        # get address and data from entry boxes
        address = self.address_entry.get()
        data = self.data_entry.get()

        if address == "" or data == "":
            return

        self.fls_write(address, data, 0)

    def fls_write(self, address, data, length): 

        #self.flash[int(address, 16)] = int(data, 16)
        #self.write_count_per_addr[int(address, 16)] += 1
        # Get the database connection for the current thread
        #db_connection = self._get_db_connection()

        # add data to logs text box
        current_time = self.get_current_time()
        log = f"{current_time} - Write: Address: {hex(int(address, 16))}, Data: {hex(int(data, 16))}"
        self.logs_text.config(state="normal")
        self.logs_text.insert(tk.END, log + "\n")
        self.logs_text.config(state="disabled")

        # add data to history list
        self.history_data.append(log)
        #write to DB
        #self.insert_element_db(db_connection, 'write', int(address, 16), int(data, 16), current_time)

        # check if current scroll position is at the end of the text box
        self.update_vscroll()

    def update_vscroll(self):
        # check if current scroll position is at the end of the text box
        _, y_end = self.logs_text.yview()
        if y_end > 0.9:
            # scroll to the bottom of the plot
            self.logs_text.yview(tk.END)

    def show_filtered_data(self):
        # Get the database connection for the current thread
        db_connection = self._get_db_connection()

        address = 0
        data = 0

        l_addr = self.address_filter_entry.get()
        if l_addr != "":
            try:
                address = int(l_addr, 16)
            except:
                return

        l_data = self.data_filter_entry.get()
        if l_data != "":
            try:
                data = int(l_data, 16)
            except:
                return

        if l_data == "" and l_addr == "":
            return

        print(address)
        print(data)

        # for log in self.history_data:
        #     if "Address: " + str(hex(address)) in log and l_data == "" and l_addr != "":
        #          print(log)
        #          data_db = self.read_all_from_querry_db(db_connection, 'address', address)
        #     elif "Data: "+str(hex(data)) in log and l_addr == "" and l_data != "":
        #         print(log)
        #         data_db = self.read_all_from_querry_db(db_connection, 'data', data)
        #     elif "Address: "+str(hex(address)) in log and "Data: "+str(hex(data)) in log and l_data != "" and l_addr != "":
        #          print(log)

        if l_data == "" and l_addr != "":
                data_db = self.read_all_from_querry_db(db_connection, 'address', address)
        elif l_addr == "" and l_data != "":
            data_db = self.read_all_from_querry_db(db_connection, 'data', data)
        elif l_data != "" and l_addr != "":
                print("TODO")



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
            time.sleep(5)
            self.update_history()

    def update_time(self):
        # update time label with current time
        current_time = self.get_current_time()
        self.time_label.config(text="Current Time: " + current_time)

        # schedule next update after 1 second
        self.root.after(1000, self.update_time)

    def close_app(self):
        """Stops the mainloop and any running threads before closing the GUI"""
        self.running = False  # set running flag to False to stop any running threads
        self.root.quit()     # stop the mainloop

if __name__ == '__main__':
    app = VirtualFlashApp()
    app.update_time()
    app.root.grid_rowconfigure(2, weight=1)
    app.root.grid_columnconfigure(1, weight=1)
    app.root.mainloop()