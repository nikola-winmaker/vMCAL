import sys
import ctypes
import threading

sys.path.insert(0, '../src_gen')
sys.path.insert(1, '../test_env/gui')
from vFLS import vFlash
from FlashLogger_DLL import VirtualFlashApp

class AutosarSIL:
    def __init__(self, dll_path):
        # Load the DLL and import the functions
        self.app_dll = ctypes.CDLL(dll_path)

        # instantiate vFlash
        self.vFLS = vFlash(self.app_dll)
        # initialize callbacks
        self.vFLS.set_callbacks()

        self.autosar_thread = None
        self.flash_gui_thread = None

    def init_dll_appl(self):
        # msg receiving
        self.autosar_thread = threading.Thread(target=self.run_dll_main)
        self.autosar_thread.daemon = True
        self.autosar_thread.start()

    def run_dll_main(self):
        dll_main_func = self.app_dll.main
        dll_main_func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
        dll_main_func.restype = ctypes.c_int

        while True:
            # Run the main function in a loop
            argc = 1
            argv = [None, None]
            argv_p = ctypes.c_char_p(argv[0])
            result = dll_main_func(argc, ctypes.pointer(argv_p))
            print("DLL main returned", result)

    def start_simulation(self):
        start_func = self.app_dll.start_application
        start_func.argtypes = [ctypes.CFUNCTYPE(None)]
        func = ctypes.CFUNCTYPE(None)(start_func)
        start_func(func)

    def start_flash_gui(self):
        self.flash_gui_thread = threading.Thread(target=self.run_flash_gui)
        self.flash_gui_thread.daemon = True
        self.flash_gui_thread.start()

    def run_flash_gui(self):
        app = VirtualFlashApp(self.vFLS.flash_data, self.vFLS.history_data)
        while True:
            app.update_time()
            app.root.grid_rowconfigure(2, weight=1)
            app.root.grid_columnconfigure(1, weight=1)
            # Run the main function in a loop
            app.root.mainloop()

dll_path = '../app_dll/c_app.dll'
as_sil = AutosarSIL(dll_path)
as_sil.init_dll_appl()
as_sil.start_flash_gui()

import time
time.sleep(1)
as_sil.start_simulation()
print("start sim")

while True:
    time.sleep(1)