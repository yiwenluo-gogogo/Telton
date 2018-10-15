from pynput.keyboard import Key, Controller, Listener
import time
import os
import rumps
import os

def notify(title,subtitle, text):
	os.system("""
			  osascript -e 'display notification "{}" with title "{}" subtitle "{}"'
			  """.format(text, title,subtitle))

class AwesomeStatusBarApp(rumps.App):
	def __init__(self):
		super(AwesomeStatusBarApp, self).__init__("Telton")
		self.menu = ["Say hi","Stop","Start"]

	@rumps.clicked("Say hi")
	def sayhi(self, _):
		notify("Telton", "Heres an alert","Hello!")
	@rumps.clicked("Stop")
	def stop(self, _):
		self.listener.stop()
		notify("Telton", "Telton is turned off","sth")
	@rumps.clicked("Start")
	def start(self,_):
		self.listener = Listener(on_press=on_press,on_release=on_release)
		self.listener.start()
		# listener.join()
		notify("Telton", "Telton is turned on","sth")
# Listener.stop

keyboard = Controller()

last3keylist=[None,None,None]p
# with open(os.path.expanduser('~/Desktop/shortcutlist.txt')) as sc_file:
# 	for t,i in enumerate(sc_file):
# 		if len(i)<2:
# 			continue
# 		key,value = i.rstrip().split('@@')
# 		if len(key)==2:
# 			shortcut_dict2[key] = value
# 		elif len(key)==3:
# 			shortcut_dict3[key] =value
shortcut_dict2={"ps":"proc sort","da":"data"}
shortcut_dict3={"psd":"proc sort descending"}
print(shortcut_dict3)
print(shortcut_dict2)
def on_press(key):
	global last3keylist
	
	if key == Key.space:
		last3str = ''.join(str(elem) for elem in last3keylist)
		last2str = str(last3keylist[1])+str(last3keylist[2])

		if last3str in shortcut_dict3:
			keyboard.release(Key.space)
			typesth(Key.backspace)
			typesth(Key.backspace)
			typesth(Key.backspace)
			typesth(Key.backspace)

			keyboard.type(shortcut_dict3[last3str])

		if last2str in shortcut_dict2:
			keyboard.release(Key.space)
			typesth(Key.backspace)
			typesth(Key.backspace)
			typesth(Key.backspace)
			keyboard.type(shortcut_dict2[last2str])
			
	try:
		last3keylist=last3keylist[1:]+[key.char]
	except:
		last3keylist=last3keylist[1:]+[key]
	print(last3keylist)

			
def typesth(ttt):
	keyboard.press(ttt)
	keyboard.release(ttt)


def on_release(key):


	if key == Key.esc:
		# Stop listener
		return False

# Collect events until released

# thread = threading.Thread(target=Listener,args=(on_press=on_press,on_release=on_release))
if __name__ == "__main__":
	AwesomeStatusBarApp().run()
