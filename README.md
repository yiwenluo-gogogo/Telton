# Telton
Input tool to help improve typing(writing code, document, article) efficiency by allow user to add self-defined shortcut for any string.

Click here to download executable file.

Please refer to guide below on how to use




# Telton User Guide


By Yiwen Luo

# Telton functions

When telton is open, you can find telton in Windows Taskbar with miniature icon of green infinite loop. 

![](./guideimg/img3.png?raw=true "Optional Title")

Right click on the icon, you will see four menu options:

![](./guideimg/img4.png?raw=true "Optional Title")

1.Turn on: This enables shortcut function, which allow you to write certain string into editor with two or three letter combination plus space. It will only works in PC-SAS or UNIX-SAS window, so it won't affect other work like email.
2.Turn off: This disables shortcut function.
3.Help: Open help file with latest shortcutlist.
4.Add: You can add new shortcut by typing into the window poped up. Keep in mind the abbreviation can only be two or three letter.

![](./guideimg/img5.png?raw=true "Optional Title")

5.Quit: Close telton program.


# How to set telton as a start up program
On Windows 7 and earlier versions of Windows, the Start menu contained a 'Startup' folder to make this easy. On these versions of Windows, you can simply open your Start menu, locate a shortcut to an application you want to start automatically, right-click it, and select Copy. Next, locate the Startup folder under All Apps in the Start menu, right-click it, and select Paste to paste a copy of that shortcut.
This folder is no longer as easily accessible on Windows 8, 8.1, and 10, but it's still accessible. To access it, press Windows Key + R, type 'shell:startup' into the Run dialog, and press Enter.
![](./guideimg/img1.png?raw=true "Optional Title")
Shortcuts you add to the 'shell:startup' folder will only launch when you log in with your user account. If you'd like a shortcut to launch itself whenever any user logs in, type 'shell:common startup' into the Run dialog instead.
Paste shortcuts into this folder and Windows will automatically load them when you sign into your computer. On Windows 10, you can just drag-and-drop shortcuts from the 'All Apps' list in the Start menu directly into this folder.

![](./guideimg/img2.png?raw=true "Optional Title")

# Telton Shortcut List(default):

| Shortcut | Text         |
|----------|--------------|
| wm       | watermelon   |
| dec      | descending   |
| tes      | randomstring |
| bms      | Bristol      |


# How to modify or delete existing shortcut
Inside telton software folder you can find a text file called 'shortcutlist'. Open it and you will see all the customizable shortcuts. Delete or modify the shortcut you want, then save and close text file. Telton will apply these changes upon restart of the program.
