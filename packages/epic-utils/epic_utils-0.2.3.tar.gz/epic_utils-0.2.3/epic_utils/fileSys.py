import os

class File:
    def __init__(self, path : str, create : bool = False):
        if (File.isAbsPath(path)):
            self.path = path
        else:
            self.path = File.toAbsPath(path)
        self.directory = File.directoryName(self.path)
        temp = File.baseName(self.path).split(".")
        self.name = temp[0]
        self.extension = temp[1]  
            
    @staticmethod
    def baseName(path : str):
        return os.path.basename(path)
    @staticmethod
    def directoryName(path : str):
        return os.path.dirname(path) 
    @staticmethod
    def toAbsPath(path : str):
        return os.path.abspath(path)
    @staticmethod
    def isAbsPath(path : str):
        return os.path.isabs(path)