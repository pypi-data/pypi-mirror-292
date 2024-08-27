import win32api,win32con,time
for i in range(800):
    win32api.keybd_event(77,0,0,0)
    win32api.keybd_event(77,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(90,0,0,0)
    win32api.keybd_event(90,0,win32con.KEYEVENTF_KEYUP,0)
    i = i + 1
    time.sleep(0.05)
