import rumps
from pynput.keyboard import Key, Controller, Listener
import subprocess, sys
import pickle

# shortcut_dict={}
# shortcut_dict[2]={"py":"python"}
# shortcut_dict[3]={"tel":"telton"}
# shortcut_dict[4]={}
# shortcut_dict[5]={}
# shortcut_dict[6]={}
rumps.debug_mode(True)

applescript='''
display dialog "In order for Telton to work, add Telton in Security & Privacy > Accessibility" buttons {"Open System Preference","Deny"} with icon alias ((":")& "Telton.icns") with title "Telton"

if button returned of result = "Open System Preference" then
	display dialog "1. Click the lock icon to unlock your system preferences.\n2. Click the plus icon and select Telton from Application List\n3. Check the box beside the Dropbox icon to enable accessibility\n4. You are good to go!" with icon alias ((":")& "Telton.icns") with title "Telton"
	do shell script "open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'"
end if

'''

args = [item for x in [("-e",l.strip()) for l in applescript.split('\n') if l.strip() != ''] for item in x]
proc = subprocess.Popen(["osascript"] + args ,stdout=subprocess.PIPE )
progname = proc.stdout.read().strip()
sys.stdout.write(str(progname))

f = open('store.pckl', 'rb')
shortcut_dict = pickle.load(f)
f.close()

lower = '''`1234567890-=[]\;',./'''
upper = '''~!@#$%^&*()_+{}|:"<>?'''

telton_status=True


class TeltonBar(rumps.App):
	def __init__(self):
		super(TeltonBar, self).__init__("Telton",icon="Telton_bw.icns")
		self.menu = ["Stop", "Start","Add alias","Reset alias"]


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
		
	@rumps.clicked("Add alias")
	def add(self, _):
		global shortcut_dict
		theText = subprocess.check_output(['osascript', '-e', \
		   r'''set theText to text returned of (display dialog "Please enter alias pair as 'alias:fullstring', recommended length of alias is between 2 and 6" default answer "hi:hello world" with icon alias ((":")& "Telton.icns") with title "Telton")'''])

		print(theText.decode('UTF-8'))
		kv = str(theText.decode('UTF-8')).strip().split(":")
		shortcut_dict[len(kv[0])][kv[0]]=kv[1]

		f = open('store.pckl', 'wb')
		pickle.dump(shortcut_dict, f)
		f.close()
	@rumps.clicked("Reset alias")
	def reset(self, _):
		global shortcut_dict
		shortcut_dict={}
		f = open('store.pckl', 'wb')
		pickle.dump(shortcut_dict, f)
		f.close()	

last6keylist=[None,None,None,None,None,None]

keyboard = Controller()

def on_press(key):
	global last6keylist
	global telton_status

	if key == Key.space and telton_status:
		last_n_str={}
		for i in range(2,7):
			last_n_str[i] = ''.join(str(elem) for elem in last6keylist[6-i:])

		for i in range(2,7):
			if last_n_str[i] in shortcut_dict[i]:

				keyboard.release(Key.space)

				last6keylist=[None,None,None,None,None,None]

				for i in range(i+1): 
					typesth(Key.backspace)
				typestring(shortcut_dict[i][last_n_str[i]])

				return
	
	try:
		last6keylist=last6keylist[1:]+[key.char]
	except:
		last6keylist=last6keylist[1:]+[key]
	print(last6keylist)

def typesth(ttt):
	keyboard.press(ttt)
	keyboard.release(ttt)

def typestring(string):
	for char in string:
		if char in upper:
			print(char)
			char_u=lower[upper.index(char)]
			keyboard.press(Key.shift)
			keyboard.press(char_u)
			keyboard.release(char_u)
			keyboard.release(Key.shift)
		elif char in lower:
			keyboard.press(char)
			keyboard.release(char)
		elif char.isupper():
			keyboard.press(Key.shift)
			keyboard.press(char.lower())
			keyboard.release(char.lower())
			keyboard.release(Key.shift)
		else:
			keyboard.press(char.lower())
			keyboard.release(char.lower())


# Collect events until released
listener = Listener(on_press=on_press)
listener.start()

TeltonBar().run()