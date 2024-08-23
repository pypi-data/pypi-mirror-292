# Copyright (C) 2023 Jaehak Lee

from . import main_window
from . import abstract_comp
from . import image
from . import prop

from .main_window import show_status
import os, shutil

CURRENT_SOURCE_CODE_FILE_PATH = os.path.relpath(__file__)

def cout(*args):
    show_status(" ".join([str(arg) for arg in args]))

def setStyle(widget, style_name):    
    sshFile=CURRENT_SOURCE_CODE_FILE_PATH+"/../style/"+style_name+"/"+style_name+".qss"
    print("sshFile Path:",sshFile)
    with open(sshFile,"r") as fh:
        widget.setStyleSheet(fh.read())