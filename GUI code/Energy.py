import numpy as np

class EnergyCalc():

    def __init__(self):
        ## consideraciones generales
        
        self.T = [0.01, 10, 20 ,30 ,40 ,50] # intervalo de temperatura
        
        self.Patm = 100            # presión atmosferica [KPa]
        
        self.Rair = 0.287          # constante de gas ideal aire [KPa*m3/Kg*K]
        
        self.d = 10                # diámetro del ventilador [cm]
        
        self.A = np.pi*(self.d/100)**2  # área del ventilador [m2]
        
        self.Vin = 10              # velocidad de entrada del aire [m/s]
        
        self.vp = 45               # flujo volumétríco [m3/min]


        ## variables cengel
        
        self.Cp = 1.005           # calor específico aire [KJ/Kg°C] se considera constante para el rango de T
        
        self.hv = [2500.9 ,2519.2 ,2537.4 ,2555.6 ,2573.5 ,2591.3]   # entalpía de saturación del vapor [KJ/Kg] aprox a la entalpía saturación para el rango de T
        
        self.Psat = [0.6117 ,1.2281 ,2.3392 ,4.2469 ,7.3851 ,12.352] # presión de  saturación vapor [KPa] para una cierta T

    def balance(self, Tin, Tout, Hin):        
        self.Hin = float(Hin)
        self.Tin = float(Tin)
        self.Tout = float(Tout)
        #print(f"{self.Tin}; {self.Hin}; {self.Tout}")

        #datos de tablas
        self.Psat1 = np.interp(self.Tin, self.T, self.Psat) # presión de saturación para la temperatura de entrada
        self.hg1 = np.interp(self.Tin, self.T, self.hv) # entalpía de saturación en la entrada
        #print (hg1)
        self.hg2 = np.interp(self.Tout, self.T, self.hv) # entalpía de saturación en la salida
        #print (hg2)

        #presión de vapor 1
        self.Pv1 = self.Hin*self.Psat1
        #print (Pv1)

        #presión del aire en la entrada
        self.Pa1 = self.Patm-self.Pv1
        #print (Pa1)

        #volumen específico 1
        self.v1 = self.Rair*(self.Tin+273.15)/self.Pa1
        #print(v1)

        #flujo másico de aire 1
        self.ma = self.vp/self.v1
        #print(ma)

        #humedad absoluta 1
        self.w1 = 0.622*self.Pv1/(self.Patm-self.Pv1)
        #print(w1)

        #entalpía 1
        self.h1 = self.Cp*self.Tin+self.w1*self.hg1
        #print(h1)

        #entapía 2
        self.h2 = self.Cp*self.Tout+self.w1*self.hg2
        #print (h2)

        #energía
        self.Q = self.ma*(self.h2-self.h1)

        #se redondea el valor quitando los decimales
        self.Q = round(self.Q, 0)

        self.Q.tolist()

        return self.Q