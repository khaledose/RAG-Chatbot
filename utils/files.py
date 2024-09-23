import os
import tempfile
import mimetypes
from fastapi import UploadFile

def create_temp_dir(file: UploadFile):
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def detect_file_type(file):
    if file is None:
        return None
    
    file_type = mimetypes.guess_type(file.name)[0]
    if file_type:
        if 'json' in file_type:
            return 'json'
        elif 'pdf' in file_type:
            return 'pdf'
        elif 'csv' in file_type:
            return 'csv'
    
    file_extension = file.name.split('.')[-1].lower()
    if file_extension in ['json', 'pdf', 'csv']:
        return file_extension
    
    return None