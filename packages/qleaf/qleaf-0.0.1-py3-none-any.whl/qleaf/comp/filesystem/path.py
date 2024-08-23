# QUTAT - Multiphysics Simulation Platform
# Copyright (C) 2023 Jaehak Lee
# SPDX-License-Identifier: GPL-3.0-only

from core.extern_libs import *

from core.ui.abstract_comp import AbstractComp
from core.ui.prop import Prop

from lib.comp.basic import TextComp, PushButtonComp



class PathComp(AbstractComp):
    def layoutClass(self):
        return QHBoxLayout()
        
    def initUI(self):
        PushButtonComp(self,
            onClick=self.openPath,
            props={"label":"..."})
        TextComp(self,
            props={"text":self.props["path"]})
        if self.props["path"].get() == None:
            self.props["path"].set(os.getcwd())

    def openPath(self):
        dialog = QFileDialog()
        if "directory" in self.props.keys():
            if self.props["directory"].get() == True:
                if self.props["path"].get():
                    dialog.setDirectory(self.props["path"].get())              
                directory = dialog.getExistingDirectory(None, 'Select Directory')
                if directory:
                    self.props["path"].set(directory)
                return directory

        if self.props["path"].get():
            dialog.setDirectory(os.path.dirname(self.props["path"].get()))
        if "extension" in self.props.keys():
            dialog.setDefaultSuffix(self.props["extension"].get())
        if "filter" in self.props.keys():
            filter = self.props["filter"].get()
        else:
            filter = "all(*.*);;text (*.txt);;image (*.jpg *.jpeg *.gif *.png *.bmp)"
        filename = dialog.getOpenFileUrl(None, 'Open File', self.props["path"].get(), filter)
        if filename[0].toString() != "":
            self.props["path"].set(filename[0].toString())

        return filename[0].toString()
