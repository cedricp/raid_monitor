#!/usr/bin/python3

import wx.adv
import os, datetime

SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
TRAY_ICON = SCRIPT_ROOT+'/raid_icon.png'
TRAY_ICON_FAIL = SCRIPT_ROOT+'/raid_icon_fail.png'
TRAY_TOOLTIP = 'Raid monitor'

class Raid_device:
    def __init__(self, array):
        self.isok = True
        self.dev = array[0]
        self.status = array[1]
        self.type = array[2]
        self.disks = array[3:]
        for disk in self.disks:
            if "(F)" in disk.upper():
                self.isok =  False
            
    def show(self):
        print(self.disks)

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update(None)
        self.timer.Start(1000)

    def create_menu_item(self, menu, label, func):
        menuitem = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=menuitem.GetId())
        menu.Append(menuitem)
        return menuitem

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def get_tooltip(self):
        status = TRAY_TOOLTIP
        status += "\n" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        for dev in self.raid_devs:
            status += "\n" + dev.dev + " : " + dev.status + " (" + dev.type + ")  [" + " ".join(dev.disks) + "]"
        return status

    def set_icon_ok(self):
        icon = wx.Icon(wx.Bitmap(TRAY_ICON))
        self.SetIcon(icon, self.get_tooltip())

    def set_icon_fail(self):
        icon = wx.Icon(wx.Bitmap(TRAY_ICON_FAIL))
        self.SetIcon(icon, self.get_tooltip())

    def on_left_down(self, event):
        pass

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()
        
    def update(self, event):
        self.scan()
        self.timer.Start(10000)
        
    def scan(self):
        self.raid_devs = []
        mdstat = open("/proc/mdstat").read()
        for md in mdstat.split("\n"):
            if md.startswith("md"):
                raid_array = md.strip().replace(" :", "").split(" ")
                raid_dev = Raid_device(raid_array)
                self.raid_devs.append(raid_dev)
        isok = True
        for dev in self.raid_devs:
            if not dev.isok:
                isok = False
                break
                
        if not isok:
            self.set_icon_fail()
        else:
            self.set_icon_ok()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()

if __name__ == '__main__':
    main()
