import time
import numpy as np
from datetime import datetime
import csv
import requests

from Energy import EnergyCalc


class DataMaster():
    def __init__(self): 

        self.sync = "#;\n"
        self.sync_ok = "!"
        self.StartStream = "##;\n"
        self.StopStream = "###;\n"
        self.SynchChannel = 0
        self.calculations = 1

        self.Energy = EnergyCalc()

        self.msg = []

        self.XData = []
        self.YData = []
        self.YData_LastROW = []
        self.last_thingspeak_update = time.time()  
        self.thingspeak_interval = 15 

        self.FunctionMaster = {
            "RowData": self.RowData,
            "LRegression": self.LRegression
        }

        self.DisplayTimeRange = 50

        self.ChannelNum = {
            'Tin': 0,
            'Hin': 1,
            'Tout': 2,
            'Hout': 3,
            'FanSpeed': 4,
            'Q': 5,
            'Ch6': 6,
            'Ch7': 7
        }
        self.ChannelColor = {
            'Tin': 'blue',
            'Hin': 'green',
            'Tout': 'red',
            'Hout': 'cyan',
            'FanSpeed': 'magenta',
            'Q': 'yellow',
            'Ch6': 'black',
            'Ch7': 'white'
        }

    def FileNameFunc(self):
        now = datetime.now()
        self.filename = now.strftime("%Y%m%d%H%M%S")+".csv"

    def SaveData(self,gui):
        current_time = time.time()

        # Si han pasado 15 segundos desde la última actualización a ThingSpeak
        if current_time - self.last_thingspeak_update >= self.thingspeak_interval:
            # Realiza la solicitud a ThingSpeak
            try:
                enviar = requests.get("https://api.thingspeak.com/update?api_key=JW4268ZH1X54GXAD&"
                                      + "field1=" + str(self.YData_LastROW[0])
                                      + "&field2=" + str(self.YData_LastROW[1])
                                      + "&field3=" + str(self.YData_LastROW[2])
                                      + "&field4=" + str(self.YData_LastROW[3])
                                      + "&field5=" + str(self.YData_LastROW[4]), 
                                      timeout=100)
                # Actualiza el tiempo de la última actualización
                self.last_thingspeak_update = current_time
            except requests.exceptions.RequestException as e:
                print(f"Error al enviar datos a ThingSpeak: {e}")

        data = [elt for elt in self.YData_LastROW]
        data.insert(0, self.XData[len(self.XData)-1])

        if gui.save:
            with open(self.filename, 'a', newline = '') as f:
                data_writer = csv.writer(f)
                data_writer.writerow(data)


    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf8')

        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                del self.msg[0]
                
                if self.msg[0] in "D":
                    self.messageLen = 0
                    self.messageLenCheck = 0
                    del self.msg[0]
                    del self.msg[len(self.msg)-1]
                    self.messageLen = int(self.msg[len(self.msg)-1])
                    del self.msg[len(self.msg)-1]
                    for item in self.msg:
                        self.messageLenCheck += len(item)

    def GenChannels(self):
        self.Channels = ["-", "Tin", "Hin", "Tout",  "Hout", "FanSpeed", "Q" ] 

    def buildYdata(self): 
        self.YData = []
        for _ in range(self.SynchChannel+self.calculations):
            self.YData.append([])
            self.YData_LastROW.append([])
        #print(f"self.YData: {self.YData}, self.YData_LatRow: {self.YData_LastROW}")     

    def ClearData(self):
        self.RowMsg = ""
        self.msg = []
        self.YData = []
        self.XData = []

    def IntMsgFunc(self):
        self.IntMsg = [int(msg) for msg in self.msg]
        #print(f"IntMsg: {self.IntMsg}")

    def StreamDataCheck(self):
        self.StreamData = False
        if self.SynchChannel == len(self.msg):
            if self.messageLen == self.messageLenCheck:
                self.StreamData = True
                #print(f"self.msg: {self.msg}")
                self.IntMsgFunc()

    def SetRefTime(self):
        if len(self.XData) == 0:
            self.RefTime = time.perf_counter()
        else:
            self.RefTime = time.perf_counter() - self.XData[len(self.XData)-1]

    def UpdataXdata(self):
        if len(self.XData) == 0:
            self.XData.append(0)
        else:
            self.XData.append(time.perf_counter()-self.RefTime)

    def UpdataYdata(self):
        for ChNumber in range(self.SynchChannel):
            self.YData[ChNumber].append(self.IntMsg[ChNumber])
            self.YData_LastROW[ChNumber] = self.IntMsg[ChNumber]
        #print(f"self.YData: {self.YData}")
        #print(f"self.YData: {self.YData}, self.YData_LatRow: {self.YData_LastROW}") 

        self.YData[5].append(float(self.Energy.balance(self.IntMsg[0], self.IntMsg[2], self.IntMsg[1])))        
        self.YData_LastROW[5] = self.YData[5][-1]       
        #print(f"self.YData: {self.YData}, self.YData_LatRow: {self.YData_LastROW}") 

    def AdjustData(self):
        lenXdata = len(self.XData)
        if (self.XData[lenXdata-1] - self.XData[0]) > self.DisplayTimeRange:
            del self.XData[0]
            for ydata in self.YData:
                del ydata[0]

        x = np.array(self.XData)
        self.XDisplay = np.linspace(x.min(), x.max(), len(x), endpoint=0)        
        self.YDisplay = np.array(self.YData)
        #print(f"self.YDisplay: {self.YDisplay}")

    def RowData(self, gui):
        #print(f"gui.x: {gui.x}, gui.x: {gui.x}")         
        gui.chart.plot(gui.x, gui.y, color=gui.color, dash_capstyle='projecting', linewidth=1)

    def LRegression(self, gui):
        x = gui.x
        y = gui.y
        coefficients = np.polyfit(x, y, 1)
        poly = np.poly1d(coefficients)
        new_y = poly(x)
        gui.chart.plot(x, new_y, color="#db2775", dash_capstyle='projecting', linewidth=1)
