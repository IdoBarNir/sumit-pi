# Contol two products: Binary Beer and HPU-22
# This progem runs on a Raspberry Pi computer attached to a 16-relay array

# HPU: - RasPi GPIO - Relay pins assignments
#  Switch  GPIO   Relay     Cable
#   A1 in  17       2       Black  W
#   B1 in  27       4       White  W
#   A2 in  22       6       Gray   W
#   B2 in   5       8       Purple W
#   C  in   6      10       Blue   W  - Carry
#   A1 out 23       1       Gray   N
#   B1 out 24       3       Purple N
#   A2 out 25       5       Blue   N
#   B2 out 16       7       Green  N
#   C  out 26      12       Green  W  - Carry

# BB: - RasPi GPIO - Relay pins assignments
#  Switch  GPIO   Relay     Cable
#   A in  22       6       Gray   W
#   B in   5       8       Purple W
#   C in   6      10       Blue   W  - Carry
#   A out 25       5       Blue   N
#   B out 16       7       Green  N
#   C out 26      12       Green  W  - Carry

#   SPK    21      14       Red    W
#   Pump   20      16       Brown  W

import sys
import os
from tkinter import *
import tkinter.font as myFont
import gpio
import pyautogui
from pygame import mixer

os.environ['DISPLAY'] = ':0'

if len(sys.argv) > 1:
    answer = sys.argv[1]
    print(f"Received answer: {answer}")
else:
    print("No answer provided.")
    sys.exit(1)

print("Successfully processed the answer.")

root = Tk()
root.title("SumIt")
root.config(cursor="none")
root.attributes('-fullscreen', True)
root.geometry('1366x768')
smallFont = myFont.Font(family='Arial', size=12, weight="bold")
btnFont = myFont.Font(family='Arial', size=32, weight="bold")
labelFont = myFont.Font(family='Arial', size=32, weight="bold")
inpFont = myFont.Font(family='Tahoma', size=36, weight="bold")
numBitsBB = 3   # user inputs
numBitsHPU = 4  # user inputs
bitsBB = [0]*numBitsBB   # BB-ABC
bitsHPU = [0]*numBitsHPU # HPU-A1B1A2B2
bitA1 = 0
bitB1 = 1
bitA2 = 2
bitB2 = 3
isBitCarry = 0
spkON = False
lightON = False
pumpON = False
canStart = False
canStop = False
canNext = False
bgColorOFF = "#cccccc"
bgColorLightON = "#cccc00"
bgColorSpkON = "#00bb33"
bgColorPumpON = "#ff7700"
btnTextA = StringVar(value="0")
btnTextB = StringVar(value="0")
btnTextC = StringVar(value="0")
btnTextA1 = StringVar(value="0")
btnTextB1 = StringVar(value="0")
btnTextA2 = StringVar(value="0")
btnTextB2 = StringVar(value="0")
xCenter = 683
yCenter = 394
mixer.init()
beep = mixer.Sound("error.wav")
startMusic = mixer.Sound("start.mp3")
stopMusic = mixer.Sound("stop.mp3")
GPIOpins = [23,17,24,27,25,22,16,5,6,26,21,20]
gpio.Init(GPIOpins)

#GPIO pins assignments
       #GPIO #Relay
A1InPin = 17  # 2
B1InPin = 27  # 4
A2InPin = 22  # 6
B2InPin =  5  # 8
CrInPin =  6  # 10 - Carry
A1OutPin = 23 # 1
B1OutPin = 24 # 3
A2OutPin = 25 # 5
B2OutPin = 16 # 7
CrOutPin = 26 # 12 - Carry

SpkPin = 21   # 14
PumpPin = 20  # 16

numValves = 5
ALLValvesIn = [A1InPin,B1InPin,A2InPin,B2InPin,CrInPin]
ALLValvesInNames = ["A1In","B1In","A2In","B2In","CarryIn"]
ALLValvesOut = [A1OutPin,B1OutPin,A2OutPin,B2OutPin,CrOutPin]
ALLValvesOutNames = ["A1Out","B1Out","A2Out","B2Out","CarryOut"]
valvesInState = [0]*numValves
valvesOutState = [0]*numValves
valveA1 = 0
valveB1 = 1
valveA2 = 2
valveB2 = 3
valveCr = 4


def Beep():
    beep.play()
    
def DispBB(): # display BB window
    frame.destroy()
    WinBB()
def DispHPU(): # display HPU window
    frame.destroy()
    WinHPU()

def PumpOn(updateIcon):
    global btnPUMP
    print("Pump on"," GPIO-",PumpPin)
    gpio.On(PumpPin)
    pumpON = True
    if (updateIcon): btnPUMP.config(bg=bgColorPumpON, activebackground=bgColorOFF)
    return

def PumpOff(updateIcon):
    global btnPUMP
    print("Pump off"," GPIO-",PumpPin)
    gpio.Off(PumpPin)
    pumpON = False
    if (updateIcon): btnPUMP.config(bg=bgColorOFF, activebackground=bgColorPumpON)
    return

def SpkOn():
    print("Speaker on"," GPIO-",PumpPin)
    gpio.On(SpkPin)
    return

def SpkOff():
    print("Speakers off"," GPIO-",PumpPin)
    gpio.Off(SpkPin)
    return

# BB Valves
# open input valves according to bits after closing matching output valves 
def OpenBBValvesIn(sum):
    if sum == 1:    
        # close output A2 valve (01) 
        print("BB-Out-01"," GPIO-",A2OutPin," Off")
        gpio.Off(A2OutPin)
        # open input A2 valve (01) 
        print("BB-In-01"," GPIO-",A2InPin," On")
        gpio.On(A2InPin)
    elif sum == 2:  # A2 & B2 valves (10)
        print("BB-Out-10"," GPIO-",A2OutPin," & ",B2OutPin," Off")       
        gpio.Off(A2OutPin)
        gpio.Off(B2OutPin)
        print("BB-In-10"," GPIO-",A2InPin," & ",B2InPin," On")       
        gpio.On(A2InPin)
        gpio.On(B2InPin)
    elif sum == 3:  # open A2 & B2 & Carry valves (11)
        print("BB-Out-11"," GPIO-",CrOutPin," & ",A1OutPin," & ",B1OutPin," & ",A2OutPin," & ",B2OutPin," Off")        
        gpio.Off(CrOutPin)
        gpio.Off(A1OutPin)
        gpio.Off(B1OutPin)
        gpio.Off(A2OutPin)
        gpio.Off(B2OutPin)
        print("BB-In-11"," GPIO-",CrInPin," & ",A1InPin," & ",B1InPin," & ",A2InPin," & ",B2InPin," On")        
        gpio.On(CrInPin)
        gpio.On(A1InPin)
        gpio.On(B1InPin)
        gpio.On(A2InPin)
        gpio.On(B2InPin)
    return

# HPU Valves
# open input valves according to bits after closing matching output valves 
def OpenHPUValvesIn():
    global valvesInState
    valvesInState = [0]*numValves # reset
    if (bitsHPU[bitA1]):
        # close output valve
        print("bit-Out A1"," GPIO-",A1OutPin," Off")
        gpio.Off(A1OutPin)
        # open input valve
        print("bit-In A1"," GPIO-",A1InPin," On")
        gpio.On(A1InPin)
    if (bitsHPU[bitB1]):
        # close output valve
        print("bit-Out B1"," GPIO-",B1OutPin," Off")
        gpio.Off(B1OutPin)
        # open input valve
        print("bit-In B1"," GPIO-",B1InPin," On")
        gpio.On(B1InPin)
    if (bitsHPU[bitA2]):
        # close output valve
        print("bit-Out A2"," GPIO-",A2OutPin," Off")
        gpio.Off(A2OutPin)
        # open input valve
        print("bit-In A2"," GPIO-",A2InPin," On")
        gpio.On(A2InPin)
    if (bitsHPU[bitB2]):
        # close output valve
        print("bit-Out B2"," GPIO-",B2OutPin," Off")
        gpio.Off(B2OutPin)
        # open input valve
        print("bit-In B2"," GPIO-",B2InPin," On")
        gpio.On(B2InPin)
    if (bitsHPU[bitA1] and bitsHPU[bitB1]):
        # close output valve
        print("bit-Out Carry"," GPIO-",CrOutPin," Off")
        gpio.Off(CrOutPin)
        # open input valve
        print("bit-In Carry"," GPIO-",CrInPin," On")
        gpio.On(CrInPin)
    return

# open all valves out
def OpenValvesOut():
    for valve,name in zip(ALLValvesOut,ALLValvesOutNames):
        print("bitOut-",name," GPIO-",valve," On")       
        gpio.On(valve)
    return

def CloseValvesIn():
    for valve,name in zip(ALLValvesIn,ALLValvesInNames):
        print("bitIn-",name," GPIO-",valve," Off")       
        gpio.Off(valve)
    return

def CloseValvesOut():
    for valve,name in zip(ALLValvesOut,ALLValvesOutNames):
        print("bitOut-",name," GPIO-",valve," Off")       
        gpio.Off(valve)
    return
    
def Close(): # close system before return or exit
    CloseValvesIn()
    CloseValvesOut()

def Return():
    print("return")
    if canStop: Stop()
    if canNext: Next()
    PumpOff(True) # stop pump & update icon
    Close()
    frame.destroy()
    WinMain()

def Exit():
    print("exit")
    PumpOff(False)  # without updating icon
    Close()
    gpio.Reset()
    root.destroy()

def FillBB(): # start BB fill
    global canStart,canStop
    print("fill BB clicked")
    if canStart:
        print("fill")
        sum = 0
        for i in range(numBitsBB):
            sum += bitsBB[i]                  
        CloseValvesIn() # close all input valves
        OpenValvesOut() # open all output valves
        if sum > 0:
            OpenBBValvesIn(sum) # open each input valve according to bits after closing the matching output valve
            PumpOn(True)        # start pump & update icon
            canStart = False
            canStop = True
            startMusic.play()
    else:
        Beep()
        
def NextBB():
    global bitsBB
    print("next BB clicked")
    if Next():
        # clear bits
        bitsBB = [0]*numBitsBB 
        btnTextA.set('0')
        btnTextB.set('0')
        btnTextC.set('0')

def AddHPU():
    global isBitCarry,canStart,canStop
    print("Add clicked")
    if canStart and sum(bitsHPU) > 0:
        print("add HPU")
        isBitCarry = bitsHPU[bitA1] * bitsHPU[bitB1]
        CloseValvesIn() # close all input valves
        OpenValvesOut() # open all output valves 
        OpenHPUValvesIn() # open input valves according to bits after closing the matching output valve
        PumpOn(True)    # start pump & update icon
        canStart = False
        canStop = True
        startMusic.play()
    else:
        Beep()
        
def NextHPU():
    global bitsHPU
    print("next HPU clicked")
    if Next():
        # clear bits
        bitsHPU = [0]*numBitsHPU 
        btnTextA1.set('0')
        btnTextB1.set('0')
        btnTextA2.set('0')
        btnTextB2.set('0')

def Stop(): # stop
    global canStop,canNext
    print("stop clicked")
    if canStop:
        print("stop")
        PumpOff(True)      # stop pump & update icon
        CloseValvesIn()    # close input valves
        OpenValvesOut()    # open all drain valves
        canStop = False
        canNext = True
        startMusic.stop()
        stopMusic.play()
    else:
        Beep()
        
def Next():
    global canStart,canNext
    if canNext:
        print("ready to start")
        CloseValvesIn()    # close input valves
        CloseValvesOut()   # close drain valves
        canNext = False
        canStart = True
        stopMusic.stop()
        return True
    else:
        Beep()
        return False

def ToggleSPK():
    global spkON
    pyautogui.moveTo(xCenter,yCenter)
    if spkON:
        spkON = False
        btnSPK.config(bg=bgColorOFF, activebackground=bgColorSpkON)
        SpkOff()
    else:
        spkON = True
        btnSPK.config(bg=bgColorSpkON, activebackground=bgColorOFF)
        SpkOn()

def ToggleLIGHT():
    global lightON
    pyautogui.moveTo(xCenter,yCenter)
    if lightON:       
        lightON = False
        btnLIGHT.config(bg=bgColorOFF, activebackground=bgColorLightON)
    else:
        lightON = True
        btnLIGHT.config(bg=bgColorLightON, activebackground=bgColorOFF)

def TogglePUMP():
    global pumpON
    pyautogui.moveTo(xCenter,yCenter)
    if pumpON:       
        PumpOff(True) # stop pump & update icon
    else:
        PumpOn(True)  # start pump & update icon

def ToggleBITA():
    if canStart:
        bitsBB[2] = 1-bitsBB[2]
        btnTextA.set(str(bitsBB[2]))
    else:
        Beep();

def ToggleBITB():
    if canStart:
        bitsBB[1] = 1-bitsBB[1]
        btnTextB.set(str(bitsBB[1]))
    else:
        Beep();

def ToggleBITC():
    if canStart:
        bitsBB[0] = 1-bitsBB[0]
        btnTextC.set(str(bitsBB[0]))
    else:
        Beep();

def ToggleBITA1():
    if canStart:
        bitsHPU[bitA1] = 1-bitsHPU[bitA1]
        btnTextA1.set(str(bitsHPU[bitA1]))
    else:
        Beep();

def ToggleBITB1():
    if canStart:
        bitsHPU[bitB1] = 1-bitsHPU[bitB1]
        btnTextB1.set(str(bitsHPU[bitB1]))
    else:
        Beep();

def ToggleBITA2():
    if canStart:
        bitsHPU[bitA2] = 1-bitsHPU[bitA2]
        btnTextA2.set(str(bitsHPU[bitA2]))
    else:
        Beep();

def ToggleBITB2():
    if canStart:
        bitsHPU[bitB2] = 1-bitsHPU[bitB2]
        btnTextB2.set(str(bitsHPU[bitB2]))
    else:
        Beep();
    
#===========================================================================================
    
def WinMain():
    global frame,lightON,spkON,pumpON,canNext
    frame = Frame(root)
    ##frame['borderwidth'] = 1
    ##frame['relief'] = 'solid'
    frame.pack()

    canNext = True
    Next()  # reset (just in case)

    label = Label(frame,text="Select Product", width=30, font=labelFont, fg = "blue", bg="white")
    label.grid(row=0, columnspan=10, pady=50, sticky=EW)

    btnF = Button(frame, text="     Binary Beer     ", font=btnFont, bg="yellow", command=DispBB)
    btnF.grid(row=1, column=2, columnspan=6, pady=50)

    btnP = Button(frame, text="         HPU-22         ", font=btnFont, bg="yellow", command=DispHPU)
    btnP.grid(row=2, column=2, columnspan=6, pady=50)

    btnEX= Button(frame, text="           EXIT           ", font=btnFont, bg="red", command=Exit)
    btnEX.grid(row=3, column=2, columnspan=6, pady=100)

def WinBB():
    global frame,btnLIGHT,btnSPK,btnPUMP,canNext
    frame = Frame(root)
    ##frame['borderwidth'] = 1
    ##frame['relief'] = 'solid'
    frame.pack()
##    for i in range(5):
##        frame.columnconfigure(i,weight=1)
##    for i in range(10):
##        frame.rowconfigure(i,weight=1)

    canNext = True
    NextBB()  # reset (just in case)

    label = Label(frame,text="Binary Beer", font=labelFont, fg = "blue", bg="white")
    label.grid(row=0, column=0, columnspan=6, pady=50, sticky=EW)

    btnBitA = Button(frame, font=inpFont, bg="white", textvariable=btnTextA, command=ToggleBITA)
    btnBitA.grid(row=1, column=1)
    btnBitB = Button(frame, font=inpFont, bg="white", textvariable=btnTextB, command=ToggleBITB)
    btnBitB.grid(row=1, column=2)
    btnBitC = Button(frame, font=inpFont, bg="white", textvariable=btnTextC, command=ToggleBITC)
    btnBitC.grid(row=1, column=3)

    tapA = PhotoImage(file="beer tapA.png")
    labelA = Label(frame, image=tapA)
    labelA.grid(row=2, column=1,pady=10)
    labelA.image = tapA

    tapB = PhotoImage(file="beer tapB.png")
    labelB = Label(frame, image=tapB)
    labelB.grid(row=2, column=2, pady=10)
    labelB.image = tapB

    tapC = PhotoImage(file="beer tapC.png")
    labelC = Label(frame, image=tapC)
    labelC.grid(row=2, column=3, pady=10)
    labelC.image = tapC

    space1 = Label(frame,text="", font=labelFont)
    space1.grid(row=3, column=0)
    
    btnFill = Button(frame, text="    CHEERS!    ", font=btnFont, bg="yellow", command=FillBB)
    btnFill.grid(row=4, column=2, pady=15)

    btnStop = Button(frame, text="      GOT IT!      ", font=btnFont, bg="#ffbb77", command=Stop)
    btnStop.grid(row=5, column=2, pady=15)

    btnNext = Button(frame, text=" NEXT GLASS ", font=btnFont, bg="#ff7777", command=NextBB)
    btnNext.grid(row=6, column=2, pady=15)

    back = PhotoImage(file="back.png")
    btnRET = Button(frame, image=back, bg=bgColorOFF, command=Return)
    #btnRET = Button(frame, text="RETURN", font=smallFont, bg="#77aaff", command=Return)
    btnRET.grid(row=6, column=5, padx = 20, pady=1, sticky=E)
    btnRET.image = back

    light = PhotoImage(file="light.png")
    if lightON:
        col = bgColorLightON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorLightON
    btnLIGHT = Button(frame, image=light, bg=col, activebackground=acol, command=lambda:ToggleLIGHT())
    btnLIGHT.grid(row=6, column=0, padx = 20, pady=5, sticky=W)
    btnLIGHT.image = light

    speaker = PhotoImage(file="speaker.png")
    if spkON:
        col = bgColorSpkON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorSpkON
    btnSPK = Button(frame, image=speaker, bg=col, activebackground=acol, command=lambda:ToggleSPK())
    btnSPK.grid(row=5, column=0, padx=20, pady=5, sticky=SW)
    btnSPK.image = speaker

    pump = PhotoImage(file="water-pump.png")
    if pumpON:
        col = bgColorPumpON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorPumpON
    btnPUMP = Button(frame, image=pump, bg=col, activebackground=acol, command=lambda:TogglePUMP())
    btnPUMP.grid(row=5, column=5, padx=20, pady=1, sticky=SE)
    btnPUMP.image = pump

def WinHPU():
    global frame,btnLIGHT,btnSPK,btnPUMP,canNext
    frame = Frame(root)
    ##frame['borderwidth'] = 1
    ##frame['relief'] = 'solid'
    frame.pack()

    canNext = True
    NextHPU()  # reset (just in case)

    label = Label(frame,text="HPU-22", font=labelFont, fg = "blue", bg="white")
    label.grid(row=0, column=0, columnspan=6, pady=20, sticky=EW)

    labelA = Label(frame, text='A  ', font=inpFont, fg="#007700")
    labelA.grid(row=1, column=1)  
    btnBitA2 = Button(frame, font=inpFont, bg="white", textvariable=btnTextA2, command=ToggleBITA2)
    btnBitA2.grid(row=1, column=2)
    labelA2 = Label(frame, text='A2', font=labelFont, fg="#008800")
    labelA2.grid(row=2, column=2)  
    btnBitA1 = Button(frame, font=inpFont, bg="white", textvariable=btnTextA1, command=ToggleBITA1)
    btnBitA1.grid(row=1, column=3)
    labelA1 = Label(frame, text='A1', font=labelFont, fg="#008800")
    labelA1.grid(row=2, column=3)  

    space1 = Label(frame,text=" ",font=smallFont)
    space1.grid(row=4, column=0, pady=0)
##    space2 = Label(frame,text=" ",font=inpFont)
##    space2.grid(row=2, column=4, pady=10)

    labelB = Label(frame, text='B  ', font=inpFont, fg="#007700")
    labelB.grid(row=5, column=1)
    btnBitB2 = Button(frame, font=inpFont, bg="white", textvariable=btnTextB2, command=ToggleBITB2)
    btnBitB2.grid(row=5, column=2)
    labelB2 = Label(frame, text='B2', font=labelFont, fg="#008800")
    labelB2.grid(row=6, column=2, sticky=N)  
    btnBitB1 = Button(frame, font=inpFont, bg="white", textvariable=btnTextB1, command=ToggleBITB1)
    btnBitB1.grid(row=5, column=3)
    labelB1 = Label(frame, text='B1', font=labelFont, fg="#008800")
    labelB1.grid(row=6, column=3, sticky=N)  

    space1 = Label(frame,text=" ",font=smallFont)
    space1.grid(row=7, column=3, pady=10)

    btnADD = Button(frame, text="      ADD      ", font=btnFont, bg="yellow", command=AddHPU)
    btnADD.grid(row=8, column=2, pady=15)

    btnSTOP = Button(frame, text="   GOT IT!   ", font=btnFont, bg="#ffbb77", command=Stop)
    btnSTOP.grid(row=9, column=2, pady=15)

    btnNEXT = Button(frame, text="     NEXT     ", font=btnFont, bg="#ff7777", command=NextHPU)
    btnNEXT.grid(row=10, column=2, pady=15)

    back = PhotoImage(file="back.png")
    btnRET = Button(frame, image=back, bg=bgColorOFF, command=Return)
    btnRET.grid(row=10, column=5, padx = 20, pady=1, sticky=E)
    btnRET.image = back

    light = PhotoImage(file="light.png")
    if lightON:
        col = bgColorLightON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorLightON
    btnLIGHT = Button(frame, image=light, bg=col, activebackground=acol, command=lambda:ToggleLIGHT())
    btnLIGHT.grid(row=10, column=0, padx = 20, pady=10, sticky=SW)
    btnLIGHT.image = light

    speaker = PhotoImage(file="speaker.png")
    if spkON:
        col = bgColorSpkON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorSpkON
    btnSPK = Button(frame, image=speaker, bg=col, activebackground=acol, command=lambda:ToggleSPK())
    btnSPK.grid(row=9, column=0, padx = 20, pady=10, sticky=SW)
    btnSPK.image = speaker

    pump = PhotoImage(file="water-pump.png")
    if pumpON:
        col = bgColorPumpON
        acol = bgColorOFF
    else: 
        col = bgColorOFF
        acol = bgColorPumpON
    btnPUMP = Button(frame, image=pump, bg=col, activebackground=acol, command=lambda:TogglePUMP())
    btnPUMP.grid(row=9, column=5, padx = 20, pady=1, sticky=SE)
    btnPUMP.image = pump

WinMain()
root.mainloop()
