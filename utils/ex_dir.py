import os



def file_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False



def make_csv_file(path):
    with open(path, 'w'): pass
    return path