#Author: NSA Cloud
import bpy

from .gen_functions import textColors

def showMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text = message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
def showErrorMessageBox(message):
    print(textColors.FAIL + "ERROR: " + message + textColors.ENDC)
    showMessageBox(message,title = "Error", icon = "ERROR")
    