import rumps
from pynput.keyboard import Key, Controller, Listener


telton_status=True
class TeltonBar(rumps.App):
    def __init__(self):
        super(TeltonBar, self).__init__("Telton")
        self.menu = ["Stop", "Start"]


    @rumps.clicked("Stop")
    def stop(self, _):
        global telton_status
        rumps.notification("Telton", "Telton is turned off","sth")
        telton_status=False

    @rumps.clicked("Start")
    def start(self,_):
        global telton_status
        rumps.notification("Telton", "Telton is turned on","sth")
        telton_status=True

last3keylist=[None,None,None]

shortcut_dict2={"ps":"proc sort","da":"data"}
shortcut_dict3={"psd":"proc sort descending"}
keyboard = Controller()

def on_press(key):
    global last3keylist
    global telton_status
    if key == Key.space and telton_status:
        last3str = ''.join(str(elem) for elem in last3keylist)
        last2str = str(last3keylist[1])+str(last3keylist[2])

        if last3str in shortcut_dict3:
            keyboard.release(Key.space)
            for i in range(4): typesth(Key.backspace)
            keyboard.type(shortcut_dict3[last3str])

        if last2str in shortcut_dict2:
            keyboard.release(Key.space)
            for i in range(3): typesth(Key.backspace)
            keyboard.type(shortcut_dict2[last2str])
            
    try:
        last3keylist=last3keylist[1:]+[key.char]
    except:
        last3keylist=last3keylist[1:]+[key]
    print(last3keylist)

def typesth(ttt):
    keyboard.press(ttt)
    keyboard.release(ttt)


# Collect events until released
listener = Listener(on_press=on_press)
listener.start()

TeltonBar().run()