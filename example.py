import time, threading
import LineBot

def ShowMsg():
    while True:    
        if len(LineBot.msg_queue) >0:
            msg = LineBot.msg_queue.pop(0)
            print(f'LineBot message = {msg}')
        time.sleep(5)

t = threading.Thread(target=ShowMsg)
t.daemon = True   
t.start()        

LineBot.pushLineMsg('This is an active push message.')
        
LineBot.init(port=32768)


