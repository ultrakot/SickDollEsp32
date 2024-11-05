#test reading and writing to NFC cards
from time import sleep_ms
import read
from machine import Pin


#read.do_read()
#leds
red_led = Pin(15, Pin.OUT)
green_led = Pin(14, Pin.OUT)

#2282008374 ear check
#2282010422 oinment
#2282012470 antibiotics 

#2 functions
def skin_illnes_init():
    print("skin rash")
    red_led.on()
    green_led.off()
    
def ear_illness_init():
    red_led.off()
    green_led.off()

def skin_illness(uid):
    
    if uid == 2282008374:
        green_led.on()
        print("earchecked, yes")
        sleep_ms(1000)
        green_led.off()
        
    if uid == 2282010422:
        red_led.off()
        print("oinment was recognised")
    
    
def ear_illness(uid):
    
    if uid == 2282008374:
        green_led.on()
        print("earchecked, yes")   
     
    if uid == 2282012470:
         green_led.off()
         print("medicine was recognised")
    
def main():
    sleep_ms(100)
    skin_illnes_init()
    #ear_illness_init()
    try:
        while True:
            uid = read.do_read()
            if uid is not None:
                print(uid)
                skin_illness(uid)
                #ear_illness(uid)
                
    except KeyboardInterrupt:
        print("Bye")
        
main()        