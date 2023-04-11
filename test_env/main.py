import sys
import ctypes
import threading

sys.path.insert(0, '../src_gen')
from vFLS import vFlash

class AutosarSIL:
    def __init__(self, dll_path):
        # Load the DLL and import the functions
        self.app_dll = ctypes.CDLL(dll_path)
        # instantiate vFlash
        self.vFLS = vFlash(self.app_dll)

    def init_dll_appl(self):
        # msg receiving
        self.autosar_thread = threading.Thread(target=self.run_dll_main)
        self.autosar_thread.daemon = True
        self.autosar_thread.start()

        # initialize callbacks
        self.vFLS.set_callbacks()

    def run_dll_main(self):
        print("entered DLL main")
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

dll_path = '../app_dll/c_app.dll'
as_sil = AutosarSIL(dll_path)
as_sil.init_dll_appl()

import time
time.sleep(1)
as_sil.start_simulation()
print("start sim")

while True:
    time.sleep(1)