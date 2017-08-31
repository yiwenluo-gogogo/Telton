#!/usr/bin/env python
import ttk
from Tkinter import * 
import pythoncom, pyHook
from ctypes import windll, Structure, c_ulong, byref
import win32api
import time
import ctypes
from ctypes import wintypes       
import os
import sys
import win32con
import win32gui_struct
import winxpgui as win32gui
import HTML
import webbrowser

shortcut_dict2={}
shortcut_dict3={}

with open('shortcutlist.txt') as sc_file:
	for t,i in enumerate(sc_file):
		if len(i)<2:
			continue
		key,value = i.rstrip().split('@@')
		if len(key)==2:
			shortcut_dict2[key] = value
		elif len(key)==3:
			shortcut_dict3[key] =value



class SysTrayIcon(object):
	'''TODO'''
	QUIT = 'QUIT'
	SPECIAL_ACTIONS = [QUIT]
	
	FIRST_ID = 1023
	
	def __init__(self,
				 icon,
				 hover_text,
				 menu_options,
				 on_quit=None,
				 default_menu_index=None,
				 window_class_name=None,):
		
		self.icon = icon
		self.hover_text = hover_text
		self.on_quit = on_quit
		
		menu_options = menu_options + (('Quit', None, self.QUIT),)
		self._next_action_id = self.FIRST_ID
		self.menu_actions_by_id = set()
		self.menu_options = self._add_ids_to_menu_options(list(menu_options))
		self.menu_actions_by_id = dict(self.menu_actions_by_id)
		del self._next_action_id
		
		
		self.default_menu_index = (default_menu_index or 0)
		self.window_class_name = window_class_name or "SysTrayIconPy"
		
		message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
					   win32con.WM_DESTROY: self.destroy,
					   win32con.WM_COMMAND: self.command,
					   win32con.WM_USER+20 : self.notify,}
		# Register the Window class.
		window_class = win32gui.WNDCLASS()
		hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
		window_class.lpszClassName = self.window_class_name
		window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
		window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
		window_class.hbrBackground = win32con.COLOR_WINDOW
		window_class.lpfnWndProc = message_map # could also specify a wndproc.
		classAtom = win32gui.RegisterClass(window_class)
		# Create the Window.
		style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
		self.hwnd = win32gui.CreateWindow(classAtom,
										  self.window_class_name,
										  style,
										  0,
										  0,
										  win32con.CW_USEDEFAULT,
										  win32con.CW_USEDEFAULT,
										  0,
										  0,
										  hinst,
										  None)
		win32gui.UpdateWindow(self.hwnd)
		self.notify_id = None
		self.refresh_icon()
		self.turnon()
		
		win32gui.PumpMessages()

	def _add_ids_to_menu_options(self, menu_options):
		result = []
		for menu_option in menu_options:
			option_text, option_icon, option_action = menu_option
			if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
				self.menu_actions_by_id.add((self._next_action_id, option_action))
				result.append(menu_option + (self._next_action_id,))
			elif non_string_iterable(option_action):
				result.append((option_text,
							   option_icon,
							   self._add_ids_to_menu_options(option_action),
							   self._next_action_id))
			else:
				print 'Unknown item', option_text, option_icon, option_action
			self._next_action_id += 1
		return result
		
	def refresh_icon(self):
		# Try and find a custom icon
		hinst = win32gui.GetModuleHandle(None)
		if os.path.isfile(self.icon):
			icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
			hicon = win32gui.LoadImage(hinst,
									   self.icon,
									   win32con.IMAGE_ICON,
									   0,
									   0,
									   icon_flags)
		else:
			print "Can't find icon file - using default."
			hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

		if self.notify_id: message = win32gui.NIM_MODIFY
		else: message = win32gui.NIM_ADD
		self.notify_id = (self.hwnd,
						  0,
						  win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
						  win32con.WM_USER+20,
						  hicon,
						  self.hover_text)
		win32gui.Shell_NotifyIcon(message, self.notify_id)

	def restart(self, hwnd, msg, wparam, lparam):
		self.refresh_icon()

	def destroy(self, hwnd, msg, wparam, lparam):
		if self.on_quit: self.on_quit(self)
		try:
			hm.UnhookKeyboard()
		except:
			pass
		nid = (self.hwnd, 0)
		win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
		win32gui.PostQuitMessage(0) # Terminate the app.
		sys.exit(0)

	def notify(self, hwnd, msg, wparam, lparam):
		if lparam==win32con.WM_LBUTTONDBLCLK:
			self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
		elif lparam==win32con.WM_RBUTTONUP:
			self.show_menu()
		elif lparam==win32con.WM_LBUTTONUP:
			pass
		return True
		
	def show_menu(self):
		menu = win32gui.CreatePopupMenu()
		self.create_menu(menu, self.menu_options)
		#win32gui.SetMenuDefaultItem(menu, 1000, 0)
		
		pos = win32gui.GetCursorPos()
		# See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
		win32gui.SetForegroundWindow(self.hwnd)
		win32gui.TrackPopupMenu(menu,
								win32con.TPM_LEFTALIGN,
								pos[0],
								pos[1],
								0,
								self.hwnd,
								None)
		win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
	
	def create_menu(self, menu, menu_options):
		for option_text, option_icon, option_action, option_id in menu_options[::-1]:
			if option_icon:
				option_icon = self.prep_menu_icon(option_icon)
			
			if option_id in self.menu_actions_by_id:                
				item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
																hbmpItem=option_icon,
																wID=option_id)
				win32gui.InsertMenuItem(menu, 0, 1, item)
			else:
				submenu = win32gui.CreatePopupMenu()
				self.create_menu(submenu, option_action)
				item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
																hbmpItem=option_icon,
																hSubMenu=submenu)
				win32gui.InsertMenuItem(menu, 0, 1, item)

	def prep_menu_icon(self, icon):
		# First load the icon.
		ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
		ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
		hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

		hdcBitmap = win32gui.CreateCompatibleDC(0)
		hdcScreen = win32gui.GetDC(0)
		hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
		hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
		# Fill the background.
		brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
		win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
		# unclear if brush needs to be feed.  Best clue I can find is:
		# "GetSysColorBrush returns a cached brush instead of allocating a new
		# one." - implies no DeleteObject
		# draw the icon
		win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
		win32gui.SelectObject(hdcBitmap, hbmOld)
		win32gui.DeleteDC(hdcBitmap)
		
		return hbm

	def command(self, hwnd, msg, wparam, lparam):
		id = win32gui.LOWORD(wparam)
		self.execute_menu_option(id)
		
	def execute_menu_option(self, id):
		menu_action = self.menu_actions_by_id[id]      
		if menu_action == self.QUIT:
			win32gui.DestroyWindow(self.hwnd)
			try:
				hm.UnhookKeyboard()
			except:
				pass
		else:
			menu_action(self)
	def turnon(self):
		global hm
		hm = pyHook.HookManager()
		# watch for all mouse events
		hm.KeyDown = OnKeyboardEvent
		# set the hook
		hm.HookKeyboard()
		# wait forever
		pythoncom.PumpMessages()		
			
def non_string_iterable(obj):
	try:
		iter(obj)
	except TypeError:
		return False
	else:
		return not isinstance(obj, basestring)


last3keylist=[None,None,None]


user32 = ctypes.WinDLL('user32', use_last_error=True)
INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008
MAPVK_VK_TO_VSC = 0
wintypes.ULONG_PTR = wintypes.WPARAM
class MOUSEINPUT(ctypes.Structure):
	_fields_ = (("dx",          wintypes.LONG),
				("dy",          wintypes.LONG),
				("mouseData",   wintypes.DWORD),
				("dwFlags",     wintypes.DWORD),
				("time",        wintypes.DWORD),
				("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
	_fields_ = (("wVk",         wintypes.WORD),
				("wScan",       wintypes.WORD),
				("dwFlags",     wintypes.DWORD),
				("time",        wintypes.DWORD),
				("dwExtraInfo", wintypes.ULONG_PTR))

	def __init__(self, *args, **kwds):
		super(KEYBDINPUT, self).__init__(*args, **kwds)
		# some programs use the scan code even if KEYEVENTF_SCANCODE
		# isn't set in dwFflags, so attempt to map the correct code.
		if not self.dwFlags & KEYEVENTF_UNICODE:
			self.wScan = user32.MapVirtualKeyExW(self.wVk,
												 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
	_fields_ = (("uMsg",    wintypes.DWORD),
				("wParamL", wintypes.WORD),
				("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
	class _INPUT(ctypes.Union):
		_fields_ = (("ki", KEYBDINPUT),
					("mi", MOUSEINPUT),
					("hi", HARDWAREINPUT))
	_anonymous_ = ("_input",)
	_fields_ = (("type",   wintypes.DWORD),
				("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
	if result == 0:
		raise ctypes.WinError(ctypes.get_last_error())
	return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
							 LPINPUT,       # pInputs
							 ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
	x = INPUT(type=INPUT_KEYBOARD,
			  ki=KEYBDINPUT(wVk=hexKeyCode))
	user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
	x = INPUT(type=INPUT_KEYBOARD,
			  ki=KEYBDINPUT(wVk=hexKeyCode,
							dwFlags=KEYEVENTF_KEYUP))
	user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))




def OnKeyboardEvent(event):
	global last3keylist
	# print 'MessageName:',event.MessageName
	# print 'Message:',event.Message
	# print 'Time:',event.Time
	# print 'Window:',event.Window
	# print 'WindowName:',event.WindowName
	# print 'Ascii:', event.Ascii, chr(event.Ascii)
	# print 'Key:', event.Key
	# print 'KeyID:', event.KeyID
	# print 'ScanCode:', event.ScanCode
	# print 'Extended:', event.Extended
	# print 'Injected:', event.Injected
	# print 'Alt', event.Alt
	# print 'Transition', event.Transition
	# print '---'

	if event.KeyID==32:		# SPACE key is pressed
		if 'SAS' in event.WindowName or 'hpwbls027' in event.WindowName:
			if last3keylist[1:]==['P','S']:
				ReleaseKey(key_dict['S'])
				type('VK_BACK')
				type('VK_BACK')

				for c in 'proc sort;by;run;':
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())
				if 'hpwbls027' in event.WindowName:
					for i in range(5):
						type('nleft')
				else:
					for i in range(5):
						type('left')					

			if last3keylist[1:]==['P','F']:
				ReleaseKey(key_dict['F'])
				type('VK_BACK')
				type('VK_BACK')
				for c in 'proc freq;table;run;':
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())
				if 'hpwbls027' in event.WindowName:
					for i in range(5):
						type('nleft')
				else:
					for i in range(5):
						type('left')

			# type('VK_BACK')
			if last3keylist==['P','S','D']:
				ReleaseKey(key_dict['D'])
				type('VK_BACK')
				type('VK_BACK')
				type('VK_BACK')
				for c in 'proc sort nodupkey;by;run;':
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())
					print c
				if 'hpwbls027' in event.WindowName:
					for i in range(5):
						type('nleft')
				else:
					for i in range(5):
						type('left')


			if last3keylist[1:]==['D','O']:
				ReleaseKey(key_dict['O'])
				type('VK_BACK')
				type('VK_BACK')
				for c in 'do;':
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())
				type('enter')
				
				for c in 'end;':
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())

				if 'hpwbls027' in event.WindowName:
					PressKey(0x12)
					type('nup')
					type('nend')
					ReleaseKey(0x12)
				else:
					type('up')
					type('end')
				type('enter')
				type('tab')
			last3str = ''.join(str(elem) for elem in last3keylist)
			last2str = str(last3keylist[1])+str(last3keylist[2])
			if last2str in shortcut_dict2:
				type('VK_BACK')
				type('VK_BACK')
				ReleaseKey(key_dict[last2str[1]])
				for c in shortcut_dict2[last2str]:
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())
			if last3str in shortcut_dict3:
				ReleaseKey(key_dict[last3str[2]])
				type('VK_BACK')
				type('VK_BACK')
				type('VK_BACK')
				for c in shortcut_dict3[last3str]:
					if c.isupper():
						PressKey(0x10)
						type(c.upper())
						ReleaseKey(0x10)
					else:
						type(c.upper())			





	last3keylist=last3keylist[1:]+[event.Key]
	print last3keylist
# return True to pass the event to other handlers
	return True


key_dict={' ':0x20,
'A':0x41,'B':0x42,'C':0x43,'D':0x44,'E':0x45,
'F':0x46,'G':0x47,'H':0x48,'I':0x49,'J':0x4A,
'K':0x4B,'L':0x4C,'M':0x4D,'N':0x4E,'O':0x4F,
'P':0x50,'Q':0x51,'R':0x52,'S':0x53,'T':0x54,
'U':0x55,'V':0x56,'W':0x57,'X':0x58,'Y':0x59,
'Z':0x5A,'-':0xBD,'0':0x30,'1':0x31,'2':0x32,
'3':0x33,'4':0x34,'5':0x35,'6':0x36,'7':0x37,
'8':0x38,'9':0x39,'shift':0x10,'enter':0x0D,'/':0xBF,
'end':0x23,'tab':0x09,
'VK_BACK':0x08,';':0xBA,'left':0x25,'up':0x26,
'right':0x27,'down':0x28,'nleft':0xEA,'nup':0xEE,
'nright':0xF5,'nend':0x5F}


def type(key):
	cur=key_dict[key]
	PressKey(cur)
	ReleaseKey(cur)


class ThemeDemo(ttk.Frame):
	def __init__(self, name='themesdemo'):
		ttk.Frame.__init__(self, name=name)
		self.pack(expand=Y, fill=BOTH)
		self.master.title('Add new shortcut')

		demoPanel = ttk.Frame(self)

		demoPanel.pack(side=TOP, fill=BOTH, expand=Y)

		Dev_text = Label(demoPanel,text='''The abbreviation must be two or three letters.''')
		Dev_text.grid(row=0, column=1, sticky=W + E + N + S,columnspan=2, padx=10,pady=5)

		b = ttk.Button(demoPanel, text='Add', command=self.addsc)
		b.grid(row=4, column=1,columnspan=2, padx=10, pady=5)

		self.e = ttk.Entry(demoPanel)
		self.e.grid(row=2, column=2)

		Label(demoPanel, text='Abbreviation',borderwidth=1).grid(row=2, column=1, sticky=W + E + N + S, padx=10, pady=5)


		self.f = ttk.Entry(demoPanel)
		self.f.grid(row=3, column=2)

		Label(demoPanel, text='Full text',borderwidth=1).grid(row=3, column=1, sticky=W + E + N + S, padx=10, pady=5)

	def addsc(self):
		file = open("shortcutlist.txt",'a')
		writetext='\n'+self.e.get().upper()+'@@'+self.f.get()
		file.write(writetext)
		file.close()
		if len(self.e.get())==2:
			shortcut_dict2[self.e.get().upper()]=self.f.get()
		if len(self.e.get())==3:
			shortcut_dict3[self.e.get().upper()]=self.f.get()


ttk.Style().theme_use('vista')



# Minimal self test. You'll need a bunch of ICO files in the current working
# directory in order for this to work...
if __name__ == '__main__':
	import itertools, glob
	
	icons = itertools.cycle(glob.glob('*.ico'))
	hover_text = "Telton"
	def turnon(sysTrayIcon):
		global hm
		hm = pyHook.HookManager()
		# watch for all mouse events
		hm.KeyDown = OnKeyboardEvent
		# set the hook
		hm.HookKeyboard()
		# wait forever
		pythoncom.PumpMessages()
	def turnoff(sysTrayIcon):
		hm.UnhookKeyboard()
	def addshortcut(sysTrayIcon):
		ThemeDemo().mainloop()

	def helpdoc(sysTrayIcon):

		Html_help= open("help.html","w")
		tablelist=[['PF','proc freq;table;run;'],
			['PS','proc sort;by;run;'],
			['PSD','proc sort nodupkey;by;run;'],
			['DO','do;\n \nend;']
			]+[[key,shortcut_dict2[key]] for key in shortcut_dict2]+[[key,shortcut_dict3[key]] for key in shortcut_dict3]

		htmlcode=HTML.table(tablelist,header_row=['Shortcut','Text'])
		Html_help.write("<p><a><font size='10'><center>Telton User Guide</center></font></a></p>")
		Html_help.write("<p><a><center>By Yiwen Luo</center></a></p>")


		Html_help.write("<p><a><font size='6'>Telton functions</font></a></p>")
		Html_help.write("<p><a><font size='4'>When telton is open, you can find telton in Windows Taskbar with miniature icon of green infinite loop. </font></a></p>")
		Html_help.write("<img src='img/img3.png' alt='some_text' >")
		Html_help.write("<p><a><font size='4'>Right click on the icon, you will see four menu options:</font></a></p>")
		Html_help.write("<img src='img/img4.png' alt='some_text' >")
		Html_help.write("<p><a><font size='4'>1.Turn on: This enables shortcut function, which allow you to write certain string into editor with two or three letter combination plus space. It will only works in PC-SAS or UNIX-SAS window, so it won't affect other work like email.</font></a></p>")
		Html_help.write("<p><a><font size='4'>2.Turn off: This disables shortcut function.</font></a></p>")
		Html_help.write("<p><a><font size='4'>3.Help: Open help file with latest shortcutlist.</font></a></p>")
		Html_help.write("<p><a><font size='4'>4.Add: You can add new shortcut by typing into the window poped up. Keep in mind the abbreviation can only be two or three letter.</font></a></p>")
		Html_help.write("<img src='img/img5.png' alt='some_text' >")
		Html_help.write("<p><a><font size='4'>5.Quit: Close telton program.</font></a></p>")
		Html_help.write("<p><a><font size='6'>How to set telton as a start up program</font></a></p>")
		Html_help.write("<p><a><font size='4'>On Windows 7 and earlier versions of Windows, the Start menu contained a 'Startup' folder to make this easy. On these versions of Windows, you can simply open your Start menu, locate a shortcut to an application you want to start automatically, right-click it, and select Copy. Next, locate the Startup folder under All Apps in the Start menu, right-click it, and select Paste to paste a copy of that shortcut.</font></a></p>")
		Html_help.write("<p><a><font size='4'>This folder is no longer as easily accessible on Windows 8, 8.1, and 10, but it's still accessible. To access it, press Windows Key + R, type 'shell:startup' into the Run dialog, and press Enter.</font></a></p>")
		Html_help.write("<img src='img/img1.png' alt='some_text' >")
		Html_help.write("<p><a><font size='4'>Shortcuts you add to the 'shell:startup' folder will only launch when you log in with your user account. If you'd like a shortcut to launch itself whenever any user logs in, type 'shell:common startup' into the Run dialog instead.</font></a></p>")
		Html_help.write("<p><a><font size='4'>Paste shortcuts into this folder and Windows will automatically load them when you sign into your computer. On Windows 10, you can just drag-and-drop shortcuts from the 'All Apps' list in the Start menu directly into this folder.</font></a></p>")
		Html_help.write("<img src='img/img2.png' alt='some_text' >")
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'>Telton Shortcut List:</font></a></p>")
		Html_help.write(htmlcode)
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'> </font></a></p>")
		Html_help.write("<p><a><font size='6'>How to modify or delete existing shortcut</font></a></p>")
		Html_help.write("<p><a><font size='6'>Inside telton software folder you can find a text file called 'shortcutlist'. Open it and you will see all the customizable shortcuts. Delete or modify the shortcut you want, then save and close text file. Telton will apply these changes upon restart of the program.</font></a></p>")

		Html_help.close()
		webbrowser.open("help.html")


	menu_options = (('Turn on', None, turnon),
					('Turn off', None, turnoff),
					('Help', None, helpdoc),
					('Add', None, addshortcut)
				   )
	def bye(sysTrayIcon): print 'Bye.'


	SysTrayIcon('icon/icon.ico', hover_text, menu_options, on_quit=bye, default_menu_index=1)
