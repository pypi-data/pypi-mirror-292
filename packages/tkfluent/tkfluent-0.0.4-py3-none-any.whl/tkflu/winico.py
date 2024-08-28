from tkdeft.object import DObject

try:
    from tkwinico import *
except:
    class FluWinico(DObject):
        pass
else:
    class FluWinico(Winico, DObject):
        def __init__(self, *args, icon_name=None, icon_file=None, **kwargs):
            super().__init__(*args, **kwargs)

            self.tray_add(self.icon(icon_name=icon_name, icon_file=icon_file), callback=self.callback, callback_args=[MESSAGE, X, Y])

            from .popupmenu import FluPopupMenu

            self.menu = FluPopupMenu()
            self.menu.window.geometry("100x40")

        def callback(self, message, x, y):
            if message == "WM_RBUTTONDOWNessage":
                self.menu.window.attributes("-topmost", True)
                self.menu.window.deiconify()
                self.menu.popup(x, y)
                self.menu.focus_set()
