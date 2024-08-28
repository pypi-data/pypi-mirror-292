from abc import ABC, abstractmethod
import os, sys, json, shutil

"""
https://github.com/python/cpython/blob/main/Lib/json/__init__.py
"""


class jsonc(object):
    @staticmethod
    def load(fp):
        backup = "."+str(fp)
        shutil.copy(fp, backup)
        from fileinput import FileInput as finput
        with finput(backup, inplace=True, backup=None) as foil:
            for line in foil:
                if not line.strip().startswith("//"):
                    print(line,end='')

        with open(backup, "r") as reader:
            content = json.load(reader)

        try:os.remove(backup)
        except Exception as e:
            print(e)

        return content

class jsonl(object):
    @staticmethod
    def load(fp):
        output = []
        with open(fp, 'r') as reader:
            for content_line in reader.readlines():
                if not content_line.strip().startswith("//"):
                    try:
                        output += [
                            json.loads(content_line)
                        ]
                    except Exception as e:
                        print(e)
        return output

def load(file:str):
    if not os.path.exists(file):
        return None
    if file.endswith(".jsonc"):
        return jsonc.load(file)
    elif file.endswith(".jsonl"):
        return jsonl.load(file)
    if file.endswith(".json"):
        with open(file, "r") as reader:
            return json.load(reader)
    return None