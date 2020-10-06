import os

from zipfile import ZipFile

EXTRACT_CHUNK_SIZE = 1024 * 1024 * 100 # 100MB chunk size

class ZipExtractor(object):
    def __init__(self, path):
        self._path = path
        self._zip = ZipFile(path)
        
        # Get total number of files
        self._num_files = len(self._zip.infolist())
        self._uncompressed_size = sum([ info.file_size for info in self._zip.filelist ])
    
    @property
    def path(self):
        return self._path

    @property
    def zip(self):
        return self._zip
    
    @property
    def count(self):
        return self._num_files
        
    @property
    def uncompressed_size(self):
        return self._uncompressed_size
    
    def start(self, destination_path):
        for name in self._zip.namelist():
            file_info = self._zip.getinfo(name)
            if file_info.is_dir():
                continue
            target_path = os.path.join(destination_path, name)
            target_dir = os.path.dirname(target_path)
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)
            read_file = self._zip.open(name)
            if os.path.isfile(target_path) and file_info.file_size == os.path.getsize(target_path):
                yield file_info.file_size
                continue # Ignore completed files
            write_file = open(target_path, "wb")
            while True:
                data = read_file.read(EXTRACT_CHUNK_SIZE)
                if not data:
                    break
                write_file.write(data)
                yield len(data)