import sys
import os
import zipfile

class AudioBookPackage:
    def __init__(self, file_name, enable_diagnostic_output = True):
        self._zip_file = file_name

        self._end_func = None
        self._start_func = None
        if enable_diagnostic_output:
            self._start_func = AudioBookPackage.print_begin
            self._end_func = AudioBookPackage.print_end
    
    @property
    def start_func(self):
        return self._start_func
    
    @start_func.setter
    def start_func(self, value):
        self._start_func = value
    
    @property
    def end_func(self):
        return self._end_func
    
    @end_func.setter
    def end_func(self, value):
        self._end_func = value

    def install(self, target_dir):
        result = {}

        try:
            os.mkdir(target_dir)
        except FileExistsError:
            pass
    
        if self.start_func != None:
            self.start_func()

        with zipfile.ZipFile(self._zip_file, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        if self.end_func != None:
            self.end_func()

        name_path = os.path.join(target_dir, "info", "name.txt")
        with open(name_path, "r", encoding="utf-8") as f:
            result['audio_book_name'] = f.read().strip()

        return result

    @staticmethod
    def print_begin():
        sys.stdout.write("Unzipping data ... ")
        sys.stdout.flush()
    
    @staticmethod
    def print_end():
        print("done")