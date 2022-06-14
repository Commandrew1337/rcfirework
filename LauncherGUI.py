import time
import serial
import tkinter as tk 
from functools import partial
import math
import sys
import serial.tools.list_ports
import threading
import queue


class FireWorkLauncherControllerThread( threading.Thread ):
    DELAY_AFTER_SEND    = 0.25
    DELAY_AFTER_RECEIVE = 0.1
    GAP_IGNITOR_TIME = 0.75 - (DELAY_AFTER_SEND + DELAY_AFTER_RECEIVE) #is 1/2 ignitor timing in microcontroller code

    def __init__( self, q, comStr, *args, **kwargs ):
        super( FireWorkLauncherControllerThread, self ).__init__( *args, **kwargs )
        self.queue       = q
        self._stopThread = threading.Event()

        print( 'Open Serial Port: {}'.format( comStr ) )

        self.serialPort = serial.Serial(
            port        = comStr,
            baudrate    = 115200,
            parity      = serial.PARITY_NONE,
            stopbits    = serial.STOPBITS_ONE,
            bytesize    = serial.EIGHTBITS
        )

        self.serialPort.isOpen()



    def senddata( self, ignitorIdx ):

        if (ignitorIdx<10):
            ignitorIdxStr  = '{}'.format( ignitorIdx )
        else:
            ignitorIdxStr = chr(ignitorIdx+87) #ascii encoding of a to z starting at 10 to NUM_IGNITORS, will fail at NUM_IGNITORS=35
        ignitorIdxByte = ignitorIdxStr.encode(encoding="ascii",errors="xmlcharrefreplace")
        print('Sending:', ignitorIdxByte)
        response       = ''

        if self.serialPort:
            self.serialPort.write( ignitorIdxByte )

        # wait before reading output (give device time to answer)
        # maybe if the PIC wasnt so slow...
        time.sleep( self.DELAY_AFTER_SEND )
        if self.serialPort:
            while self.serialPort.inWaiting() > 0:
                response += bytes.decode( self.serialPort.read( 1 ) )
        else:
            response = 'rec_{}'.format( ignitorIdx )

        time.sleep( self.DELAY_AFTER_RECEIVE )
        print('Response:', response)
        time.sleep( self.GAP_IGNITOR_TIME ) #prevents more than two ignitors to be on at the same time
        return response

    def run( self ):
        while True:
            if self.threadStopped():
                return

            try:
                ignitorRequest = self.queue.get( timeout = 1 )
            except queue.Empty:
                continue

            print( self.senddata( ignitorRequest ) )

            self.queue.task_done()


    def stop( self ):
        if self.serialPort:
            self.serialPort.close()

        self._stopThread.set()

    def threadStopped( self ):
        return self._stopThread.is_set()

 
class FireworkLauncherControllerClass():
    NUM_IGNITORS        = 23
    IGNITORS            = range( 1, NUM_IGNITORS + 1 )

    def __init__( self ):
        self.queue                    = queue.Queue()
        self.serialPort               = None
        self.debug_disableSerialPort  = True
        self.serialCommunicatorThread = None

    def openSerialPort( self, comStr ):
        self.serialCommunicatorThread = FireWorkLauncherControllerThread( self.queue, comStr )
        self.serialCommunicatorThread.start()

    def closeSerialPort( self ):
        if self.serialCommunicatorThread:
            self.serialCommunicatorThread.stop()
            self.serialCommunicatorThread.join()
            self.serialCommunicatorThread = None

    def addIgniterRequestToQueue( self, ignitorIdx ):
        self.queue.put_nowait( ignitorIdx )


    def buttonPressed( self, ignitorIdx ):
        response = self.addIgniterRequestToQueue( ignitorIdx )
        


class IgniterButton():
    font = ( "Arial Bold", 20 )
    buttonReadyColor   = 'green'
    buttonDefaultColor = ( 100, 100, 100 )

    def __init__( self, root, command, ignitorIdx, column, row ):
        self.button = tk.Button( 
            root, 
            text    = "  {}  ".format( ignitorIdx ), 
            command = self.pressed,
            font    = self.font,
            bg      = self.buttonReadyColor
        )
        self.command = command
        self.ignitorIdx = ignitorIdx
        self.button.grid( column = column, row = row )
        self.color = list( self.buttonDefaultColor )

    def pressed( self ):
        self.color = [ 250, 0, 0 ]
        self.draw()
        self.command()

    def reset( self ):
        self.color = list( self.buttonDefaultColor )
        self.button.configure( bg = self.buttonReadyColor )

    def draw( self ):
        if tuple(self.color) != self.buttonDefaultColor:
            for idx, color in enumerate( self.color ):
                if color != self.buttonDefaultColor[idx]:
                    self.color[idx] += max( -5, min( 5, self.buttonDefaultColor[idx] - color ) )

            self.button.configure( bg = '#{:02X}{:02X}{:02X}'.format( self.color[0], self.color[1], self.color[2] ) )
            self.button.after( 50, self.draw )



class LauncherGui():

    def __init__( self ):
        self.comPorts = serial.tools.list_ports.comports()
        self.FireworkLauncherController = FireworkLauncherControllerClass()


    def run( self ):
        self.window = tk.Tk()
        self.window.title( 'Fireworks Launcher' )
        self.window.geometry( '700x400' )
         
        self.lbl = tk.Label( self.window, text = '', font = ( 'Arial Bold', 10 ) )
        self.lbl.grid( column = 6, row = 0 )

        buttonFont = ( "Arial Bold", 20 )
        numButtonColumns = 6

        comPortStrs = [ comPort.device for comPort in self.comPorts ]

        if len( comPortStrs ) == 0:
            comPortStrs.append( 'None' )


        self.tkStrComPort = tk.StringVar( self.window )
        self.tkStrComPort.set( comPortStrs[0] ) # set the default option

        comPortSelect = tk.OptionMenu( self.window, self.tkStrComPort, *comPortStrs )
        comPortSelect.grid( column = 1, row = 0 )


        comPortOpen = tk.Button( 
            self.window, 
            text    = "Open COM Port", 
            command = self.openComButtonPressed )
        comPortOpen.grid( column = 2, row = 0 )

        self.comPortSelectLabel = tk.Label( self.window, text = 'Closed' )
        self.comPortSelectLabel.grid( column = 3, row = 0 )

        self.ignitorButtons = []

        for buttonIdx, ignitorIdx in enumerate( self.FireworkLauncherController.IGNITORS ):
            column = int( buttonIdx % numButtonColumns )
            row    = 1+int( math.floor( buttonIdx / numButtonColumns ) )
            windowCommand = partial( self.igniteButtonPressed, ignitorIdx )
            self.ignitorButtons.append( IgniterButton( self.window, windowCommand, ignitorIdx, column, row ) )
    
        btn1 = tk.Button( self.window, text = "ALL", command = self.igniteAllButtonPressed, font = buttonFont, bg = 'orange' )
        btn1.grid( column = 2, row = 6 )

        btn1 = tk.Button( self.window, text = "Reset", command = self.resetButtonPressed, font = buttonFont, bg = 'cyan' )
        btn1.grid( column = 4, row = 6 )

        btn1 = tk.Button( self.window, text = "exit", command = self.exitButtonPressed, font = buttonFont, bg = 'grey'  )
        btn1.grid( column = 6, row = 6 )

        btn1 = tk.Button( self.window, text = "light", command = self.lightButtonPressed, font = buttonFont, bg = 'yellow' )
        btn1.grid( column = 0, row = 6 )

        btn1 = tk.Button( self.window, text = "disarm", command = self.disarmButtonPressed, font = buttonFont, bg = 'purple' )
        btn1.grid( column = 6, row = 5 )

        self.window.mainloop()

        self.FireworkLauncherController.closeSerialPort()


    def igniteButtonPressed( self, ignitorIdx ):
        self.lbl.configure( text = '{} sending'.format( ignitorIdx ) )
        self.FireworkLauncherController.buttonPressed( ignitorIdx )


    def igniteAllButtonPressed( self ):
        for button in self.ignitorButtons:
            button.pressed()

        self.lbl.configure( text = "sending all" )

    def lightButtonPressed( self ):
        self.lbl.configure( text = "toggle light" )
        self.FireworkLauncherController.buttonPressed( ignitorIdx=24 )

    def disarmButtonPressed( self ):
        self.lbl.configure( text = "sent disarm" )
        self.FireworkLauncherController.buttonPressed( ignitorIdx=25 )

    def exitButtonPressed( self ):
        self.lbl.configure( text = "exiting" )
        self.FireworkLauncherController.closeSerialPort()
        self.window.destroy()


    def resetButtonPressed( self ):
        for button in self.ignitorButtons:
            button.reset()


    def openComButtonPressed( self ):
        self.FireworkLauncherController.closeSerialPort()
        self.comPortSelectLabel.configure( text = "Closed" )
        self.window.update()
        comToOpen = self.tkStrComPort.get()
        try:
            self.comPortSelectLabel.configure( text = "Opening {}".format( comToOpen ) )
            self.window.update()
            self.FireworkLauncherController.openSerialPort( comToOpen )
            self.comPortSelectLabel.configure( text = "{} Open".format( comToOpen ) )
        except:
            self.comPortSelectLabel.configure( text = "Failed to open {}".format( comToOpen ) )



if __name__ == '__main__':
    gui = LauncherGui()
    gui.run()
    sys.exit()
