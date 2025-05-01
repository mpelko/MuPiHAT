#!/usr/bin/python3 
""" Module Mupihat_BQ25792.py, class: bq25792
Parameters
----------
none

Returns
-------
none

Licence
-------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
__author__ = "Lars Stopfkuchen"
__license__ = "GPLv3"
__version__ = "0.1.1"
__email__ = "larsstopfkuchen@mupihat.de"
__status__ = "released"

import smbus2
import sys
import time
import json

class I2CError(Exception):
    """Custom exception for I2C communication errors."""
    pass

class bq25792:
    """ 
    Summary
    ----------
      A class for accessing BQ25792 charger IC 
    
    Usage: 
    ----------
        TODO

    Attributes
    ----------
    i2c_device : int (default: 1)
         see number in /dev/i2c-X
    i2c_addr : int (default: 0x6b)
        i2c adresss of BQ25792
    busWS_ms : int (default: 10)
        sleep time after i2c access in [ms]

    Methods
    -------
    TODO
        
    """
     # constructor method
    def __init__(self, i2c_device=1, i2c_addr=0x6b, busWS_ms=10, exit_on_error = False, battery_conf_file="/etc/mupibox/mupiboxconfig.json"):
        try:
            self.battery_conf_file = battery_conf_file
            self.battery_conf = {'battery_type' : "Default",
                                 'v_100': 8100,
                                 'v_75': 7800,
                                 'v_50': 7400,
                                 'v_25': 7000,
                                 'v_0': 6700,
                                 'th_warning': 7000,
                                 'th_shutdown': 6800 }
            self._exit_on_error = exit_on_error
            self.i2c_device = i2c_device
            self.i2c_addr = i2c_addr
            self.busWS_ms = busWS_ms
            self.registers = [0xFF]*73
            #BQ25792 Register
            self.REG00_Minimal_System_Voltage = self.REG00_Minimal_System_Voltage(0x0)
            self.REG01_Charge_Voltage_Limit = self.REG01_Charge_Voltage_Limit()
            self.REG03_Charge_Current_Limit = self.REG03_Charge_Current_Limit()
            self.REG05_Input_Voltage_Limit = self.REG05_Input_Voltage_Limit()
            self.REG06_Input_Current_Limit = self.REG06_Input_Current_Limit()
            self.REG08_Precharge_Control = self.REG08_Precharge_Control()
            self.REG09_Termination_Control = self.REG09_Termination_Control()
            self.REG0A_Recharge_Control = self.REG0A_Recharge_Control() 
            self.REG0B_VOTG_regulation = self.REG0B_VOTG_regulation()
            self.REG0D_IOTG_regulation = 0xD
            self.REG0E_Timer_Control = 0xE
            self.REG0F_Charger_Control_0 = self.REG0F_Charger_Control_0()
            self.REG10_Charger_Control_1 = self.REG10_Charger_Control_1()
            self.REG11_Charger_Control_2 = self.REG11_Charger_Control_2()
            self.REG12_Charger_Control_3 = 0x12
            self.REG13_Charger_Control_4 = self.REG13_Charger_Control_4()
            self.REG14_Charger_Control_5 = self.REG14_Charger_Control_5()
            self.REG15_Reserved = 0x15
            self.REG16_Temperature_Control = self.REG16_Temperature_Control()
            self.REG17_NTC_Control_0 = 0x17
            self.REG18_NTC_Control_1 = 0x18
            self.REG19_ICO_Current_Limit = self.REG19_ICO_Current_Limit()
            self.REG1B_Charger_Status_0 = 0x1b
            self.REG1C_Charger_Status_1 = self.REG1C_Charger_Status_1()
            self.REG1D_Charger_Status_2 = self.REG1D_Charger_Status_2()
            self.REG1E_Charger_Status_3 = 0x1e
            self.REG1F_Charger_Status_4 = 0x1f
            self.REG20_FAULT_Status_0  = 0x20
            self.REG21_FAULT_Status_1  = 0x21
            self.REG22_Charger_Flag_0  = 0x22
            self.REG23_Charger_Flag_1  = 0x23
            self.REG24_Charger_Flag_2  = 0x24
            self.REG25_Charger_Flag_3  = 0x25
            self.REG26_FAULT_Flag_0  = 0x26
            self.REG27_FAULT_Flag_1  = 0x27
            self.REG28_Charger_Mask_0  = 0x28
            self.REG29_Charger_Mask_1  = 0x29
            self.REG2A_Charger_Mask_2  = 0x2a
            self.REG2B_Charger_Mask_3  = 0x2b
            self.REG2C_FAULT_Mask_0   = 0x2c
            self.REG2D_FAULT_Mask_1  = 0x2d
            self.REG2E_ADC_Control = self.REG2E_ADC_Control()
            self.REG2F_ADC_Function_Disable_0 = 0x2f 
            self.REG30_ADC_Function_Disable_1 = 0x30
            self.REG31_IBUS_ADC = self.REG31_IBUS_ADC()
            self.REG33_IBAT_ADC = self.REG33_IBAT_ADC()
            self.REG35_VBUS_ADC = self.REG35_VBUS_ADC()
            self.REG37_VAC1_ADC = self.REG37_VAC1_ADC()
            self.REG39_VAC2_ADC = self.REG39_VAC2_ADC()
            self.REG3B_VBAT_ADC = self.REG3B_VBAT_ADC()
            self.REG3D_VSYS_ADC = self.REG3D_VSYS_ADC()
            self.REG3F_TS_ADC = 0x3f
            self.REG41_TDIE_ADC  = self.REG41_TDIE_ADC()
            self.REG43_Dp_ADC = 0x43
            self.REG45_Dm_ADC = 0x45
            self.REG47_DPDM_Driver = 0x47
            self.REG48_Part_Information = 0x48
            # handle to bus
            self.bq = smbus2.SMBus(i2c_device)
            self.battery_conf_load()
        except Exception as _error:
            sys.stderr.write('%s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
        finally:
            pass

    def battery_conf_load(self):
        '''
        load the battery configuration from yaml file
        '''
        try:
            with open(self.battery_conf_file) as file:
                config = json.load(file)
            
            selected_battery_name = config["mupihat"]["selected_battery"]
            for bt in config["mupihat"]["battery_types"]:
                if bt["name"] == selected_battery_name:
                    self.battery_conf["battery_type"] = selected_battery_name
                    self.battery_conf["v_100"] = int(bt["config"]["v_100"])
                    self.battery_conf["v_75"] = int(bt["config"]["v_75"])
                    self.battery_conf["v_50"] = int(bt["config"]["v_50"])
                    self.battery_conf["v_25"] = int(bt["config"]["v_25"])
                    self.battery_conf["v_0"] = int(bt["config"]["v_0"])
                    self.battery_conf["th_warning"] = int(bt["config"]["th_warning"])
                    self.battery_conf["th_shutdown"] = int(bt["config"]["th_shutdown"])
                    print(json.dumps(self.battery_conf, indent=4))
                    break            
            return 0
        except Exception as _error:
            sys.stderr.write('battery_conf_load from JSON failed, use standard configuration, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass

    def battery_soc(self):
        '''
        Description
        -------
        Calc the Battery State-of-Charge
        Compares the voltage of battery (from VBat register value) with thresholds from battery_conf

        Outputs
        ------
            Bat_SOC -> str {100%, 75%, 50%, 25%, 0%} \n
            Bat_Stat -> {OK, LOW, SHUTDOWN}
        '''
        Bat_SOC = ''
        Bat_Stat = ''
        v_100, v_75, v_50, v_25, v_0 = self.battery_conf['v_100'], self.battery_conf['v_75'],self.battery_conf['v_50'],self.battery_conf['v_25'],self.battery_conf['v_0']
        th_warning, th_shutdown = self.battery_conf['th_warning'], self.battery_conf['th_shutdown']

        VBat = self.read_Vbat()

        if VBat > v_100     : Bat_SOC = "100%"
        elif VBat > v_75    : Bat_SOC = "75%"
        elif VBat > v_50    : Bat_SOC = "50%"
        elif VBat > v_25    : Bat_SOC = "25%"
        elif VBat > v_0     : Bat_SOC = "0%"

        if VBat > th_warning : Bat_Stat = 'OK'
        elif (VBat < th_warning) & (VBat > th_shutdown) : Bat_Stat = 'LOW'
        elif (VBat < th_shutdown) : Bat_Stat = 'SHUTDOWN'

        return Bat_SOC, Bat_Stat

    # BQ25795 Register
    class BQ25795_REGISTER:
        def __init__(self, addr, value=0):
            self._addr = addr
            self._value = value
        def set (self, value):
            self._value = value
        def get(self):
            return self._value
        def twos_complement(self):
            if (self._value >> 15) == 1:
                ret = (-1)*(65535 + 1 - self._value) #two's complement
            else:
                ret = self._value
            return ret

    class REG00_Minimal_System_Voltage(BQ25795_REGISTER):
        """
        BQ25795 - REG00_Minimal_System_Voltage
        ----------
        VSYSMIN, Minimal System Voltage: 
            During POR, the device reads the resistance tie to PROG pin, 
            to identify the default battery cell count and determine the default power on VSYSMIN list below: 
                1s: 3.5V 
                2s: 7V 
                3s: 9V 
                4s: 12V 
            RW Range : 2500mV-16000mV 
            Fixed Offset : 2500mV Bit Step Size : 250mV Clamped High
        """
        def __init__(self, addr, value=0):
            super().__init__(addr, value)
            self.VSYSMIN = self._value * 250 + 2500
        def set (self, value):
            super().set(value)
            self.VSYSMIN = self._value * 250 + 2500

    class REG01_Charge_Voltage_Limit(BQ25795_REGISTER):
        """
        BQ25795 - REG01_Charge_Voltage_Limit
        ---------
        VREG, Battery Voltage Limit: 
            During POR, the device reads the resistance tie to PROG pin, 
            to identify the default battery cell count and determine the default power-on battery voltage regulation limit: 
            1s: 4.2V 
            2s: 8.4V 
            3s: 12.6V 
            4s: 16.8V 
            Type : RW 
            Range : 3000mV-18800mV 
            Fixed Offset : 0mV 
            Bit Step Size : 10mV
        """
        def __init__(self, addr=0x1, value=0):
            super().__init__(addr, value)
            self._value = value
            self.VREG = self._value * 10
        def set (self, value):
            super().set(value)
            self.VRE0G = self._value * 10

    class REG03_Charge_Current_Limit:
        #Charge Current Limit During POR, the device reads the resistance tie to PROG pin, to identify the default battery cell count and determine the default power-on battery charging current: 1s and 2s: 3s and 4s: 1A Type : RW Range : 50mA-5000mA Fixed Offset : 0mA Bit Step Size : 10mA
        def __init__(self, value = 0):
            self._addr = 0x3
            self._value = value
            self.ICHG = self._value * 10
        def set (self, value):
            self._value = value
            self.ICHG = self._value * 10

    class REG05_Input_Voltage_Limit:
        #Absolute VINDPM Threshold VINDPM register is reset to 3600mV upon adapter unplugged and it is set to the value based on the VBUS measurement when the adapter plugs in. It is not reset by the REG_RST and the WATCHDOG Type : RW POR: 3600mV (24h) Range : 3600mV-22000mV Fixed Offset : 0mV Bit Step Size : 100mV
        def __init__(self, value = 0):
            self._addr = 0x5
            self._value = value
            self.VINDPM = self._value * 100
        def set (self, value):
            self._value = value
            self.VINDPM = self._value * 100

    class REG06_Input_Current_Limit(BQ25795_REGISTER):
        '''
        IINDPM
            Based on D+/D- detection results: 
            USB SDP = 500mA USB CDP = 1.5A 
            USB DCP = 3.25A Adjustable High Voltage 
            DCP = 1.5A 
            Unknown Adapter = 3A 
            Non-Standard Adapter = 1A/2A/2.1A/2.4A 
            Type : RW POR: 3000mA (12Ch) 
            Range : 100mA-3300mA 
            Fixed Offset : 0mA Bit Step Size : 10mA
        '''
        def __init__(self, addr=0x6, value=0x12c):
            super().__init__(addr, value)
            self.IINDPM = (self._value & 0b111111111) * 10
        def set (self, value):
            super().set(value)
            self.IINDPM = (self._value & 0b111111111) * 10
        def get (self):
            self._value = int(self.IINDPM / 10)
            return self._value, self.IINDPM
        def get_IINDPM(self):
            '''return input current limit in mA'''
            return self.IINDPM
        
        def set_input_current_limit(self, input_current_limit):
            '''
            Set input current limit in mA steps (10mA steps, Range : 100mA-3300mA)
            '''
            self.IINDPM = input_current_limit
            self.get()
        
        def __init__(self, value = 0):
            self._addr = 0x6
            self._value = value
            self.IINDPM = self._value * 10
        def set (self, value):
            self._value = value
            self.IINDPM = self._value * 10

    class REG08_Precharge_Control:
        # VBAT_LOWV: Battery voltage thresholds for the transition from precharge to fast charge, which is defined as a ratio of battery regulation limit (VREG) Type : RW POR: 11b 0h = 15%*VREG 1h = 62.2%*VREG 2h = 66.7%*VREG 3h = 71.4%*VREG
        # IPRECHG: Precharge current limit Type : RW POR: 120mA (3h) Range : 40mA-2000mA Fixed Offset : 0mA Bit Step Size : 40mA
        def __init__(self, value = 0):
            self._addr = 0x8
            self._value = value
            self.VBAT_LOWV = ((self._value & 0b11000000) >> 6)
            self.IPRECHG   = (self._value & 0b00111111) * 40
        def set (self, value):
            self._value = value
            self.VBAT_LOWV = ((self._value & 0b11000000) >> 6)
            self.IPRECHG   = (self._value & 0b00111111) * 40
    
    class REG09_Termination_Control(BQ25795_REGISTER):
        """
        BQ25795 - EG09_Termination_Control
        ----------
        REG_RST: 
            Reset registers to default values and reset timer 
            Type : RW POR: 0b 0h = Not reset 1h = Reset
        ITERM: 
            Termination current 
            Type : RW POR: 200mA (5h) 
            Range : 40mA-1000mA 
            Fixed Offset : 0mA 
            Bit Step Size : 40mA
        """

        def __init__(self, addr=0x9, value=0):
            super().__init__(addr, value)
            self.REG_RST = ((self._value & 0b01000000) >> 6)
            self.ITERM   = (self._value & 0b00011111) * 40
        def set (self, value):
            super().set(value)
            self.REG_RST = ((self._value & 0b01000000) >> 6)
            self.ITERM   = (self._value & 0b00011111) * 40

    class REG0A_Recharge_Control:
        """
        BQ25795 - REG0A_Recharge_Control
        ----------
        CELL:
            At POR, the charger reads the PROG pin resistance to determine the battery cell count and update this CELL bits accordingly. 
            Type : RW 
            0h = 1s 
            1h = 2s 
            2h = 3s 
            3h = 4s
        TRECHG:
            Battery recharge deglich time 
            Type : RW 
            POR: 10b
            0h = 64ms 
            1h = 256ms 
            2h = 1024ms (default) 
            3h = 2048ms
        VRECHG:
            Battery Recharge Threshold Offset (Below VREG) 
            Type : RW 
            POR: 200mV (3h) 
            Range : 50mV-800mV 
            Fixed Offset : 50mV 
            Bit Step Size : 50mV
        """
        def __init__(self, value = 0):
            self._addr = 0xa
            self._value = value
            self.CELL       = ((self._value & 0b11000000) >> 6)
            self.TRECHG     = ((self._value & 0b00110000) >> 4)
            self.VRECHG     = ((self._value & 0b00001111) >> 0) * 50 + 50
        def set (self, value):
            self._value = value
            self.CELL       = ((self._value & 0b11000000) >> 6)
            self.TRECHG     = ((self._value & 0b00110000) >> 4)
            self.VRECHG     = ((self._value & 0b00001111) >> 0)

    class REG0B_VOTG_regulation(BQ25795_REGISTER):
        """
        BQ25795 - REG0B_VOTG_regulation
        ----------
        VOTG: 
            OTG mode regulation voltage
            Type : RW 
            POR: 5000mV (DCh) 
            Range : 2800mV-22000mV 
            Fixed Offset : 2800mV 
            Bit Step Size : 10mV 
            Clamped High
        """
        def __init__(self, addr=0xb, value=0):
            super().__init__(addr, value)
            self.VOTG = ((self._value & 0b11111111111))
        def set (self, value):
            super().set(value)
            self.VOTG = ((self._value & 0b11111111111))
        def get (self):
            self._value = self.VOTG
            return self._value, self.VOTG
        
    class REG0F_Charger_Control_0(BQ25795_REGISTER):
        """
        BQ25795 - REG0F_Charger_Control_0
        ----------
        EN_AUTO_IBATDIS
            Enable the auto battery discharging during the battery OVP fault 
            Type : RW POR: 1b 
            0h = The charger will NOT apply a discharging current on BAT during battery OVP 
            1h = The charger will apply a discharging current on BAT during battery OVP
        FORCE_IBATDIS
            Force a battery discharging current 
            Type : RW POR: 0b 
            0h = IDLE (default) 
            1h = Force the charger to apply a discharging current on BAT regardless the battery OVP status
        EN_CHG
            Charger Enable Configuration 
            Type : RW POR: 1b 
            0h = Charge Disable 
            1h = Charge Enable (default)
        EN_ICO
            Input Current Optimizer (ICO) Enable 
            Type : RW POR: 0b 
            0h = Disable ICO (default) 
            1h = Enable ICO
        FORCE_ICO
            Force start input current optimizer (ICO) Note: This bit can only be set and returns 0 after ICO starts. This bit only valid when EN_ICO = 1 
            Type : RW POR: 0b 
            0h = Do NOT force ICO (Default) 
            1h = Force ICO start
        EN_HIZ
            Enable HIZ mode. This bit will be also reset to 0, when the adapter is plugged in at VBUS. 
            Type : RW POR: 0b 
            0h = Disable (default) 
            1h = Enable
        EN_TERM
            Enable termination 
            Type : RW POR: 1b 
            0h = Disable 
            1h = Enable (default)
        """
        def __init__(self, addr=0xf, value = 0):
            super().__init__(addr, value)
            self.EN_AUTO_IBATDIS = ((self._value & 0b10000000) == 128)
            self.FORCE_IBATDIS   = ((self._value & 0b01000000) == 64)
            self.EN_CHG          = ((self._value & 0b00100000) == 32)
            self.EN_ICO          = ((self._value & 0b00010000) == 16)
            self.FORCE_ICO       = ((self._value & 0b00001000) == 8)
            self.EN_HIZ          = ((self._value & 0b00000100) == 4)
            self.EN_TERM         = ((self._value & 0b00000010) == 2)
        def set (self, value):
            super().set(value)
            self.EN_AUTO_IBATDIS = ((self._value & 0b10000000) == 128)
            self.FORCE_IBATDIS   = ((self._value & 0b01000000) == 64)
            self.EN_CHG          = ((self._value & 0b00100000) == 32)
            self.EN_ICO          = ((self._value & 0b00010000) == 16)
            self.FORCE_ICO       = ((self._value & 0b00001000) == 8)
            self.EN_HIZ          = ((self._value & 0b00000100) == 4)
            self.EN_TERM         = ((self._value & 0b00000010) == 2)
        def get (self):
            self._value = (self.EN_AUTO_IBATDIS << 7) | (self.FORCE_IBATDIS << 6) | (self.EN_CHG << 5) | (self.EN_ICO << 4)| (self.FORCE_ICO << 3)| (self.EN_HIZ << 2) | (self.EN_TERM << 1) | 0
            return self._value, self.EN_AUTO_IBATDIS, self.FORCE_IBATDIS, self.EN_CHG, self.EN_ICO, self.FORCE_ICO, self.EN_HIZ, self.EN_TERM 

    class REG10_Charger_Control_1(BQ25795_REGISTER):
        """
        BQ25795 - REG10_Charger_Control_1
        ----------
        VAC_OVP
            VAC_OVP thresholds 
            Type : RW POR: 00b 
            0h = 26V (default) 
            1h = 18V 
            2h = 12V 
            3h = 7V
        WD_RST
            I2C watch dog timer reset 
            Type : RW POR: 0b 
            0h = Normal (default) 
            1h = Reset (this bit goes back to 0 after timer resets)
        WATCHDOG
            Watchdog timer settings 
            Type : RW POR: 101b 
            0h = Disable 
            1h = 0.5s 
            2h = 1s 
            3h = 2s 
            4h = 20s 
            5h = 40s (default) 
            6h = 80s 
            7h = 160s
        """
        def __init__(self, addr=0x10, value = 0):
            super().__init__(addr, value)
            self.VAC_OVP       = ((self._value & 0b00110000) >> 4)
            self.WD_RST        = ((self._value & 0b00001000) >> 3)
            self.WATCHDOG      = ((self._value & 0b00000111) >> 0)
        def set (self, value):
            super().set(value)
            self.VAC_OVP       = ((self._value & 0b00110000) >> 4)
            self.WD_RST        = ((self._value & 0b00001000) >> 3)
            self.WATCHDOG      = ((self._value & 0b00000111) >> 0)
        def get (self):
            self._value = (self.VAC_OVP << 4) | (self.WD_RST << 3) | (self.WATCHDOG)
            return self._value, self.VAC_OVP, self.WD_RST, self.WATCHDOG

    class REG11_Charger_Control_2(BQ25795_REGISTER):
        """
        BQ25795 - REG11_Charger_Control_2
        ----------
        FORCE_INDET
            Force D+/D- detection 
            Type : RW POR: 0b 
            0h = Do NOT force D+/D- detection (default) 
            1h = Force D+/D- algorithm, when D+/D- detection is done, this bit will be reset to 0
        AUTO_INDET_EN
            Automatic D+/D- Detection Enable 
            Type : RW POR: 1b 
            0h = Disable D+/D- detection when VBUS is pluggedin 
            1h = Enable D+/D- detection when VBUS is plugged-in (default)
        EN_12V
            EN_12V HVDC 
            Type : RW POR: 0b 
            0h = Disable 12V mode in HVDCP (default) 
            1h = Enable 12V mode in HVDCP
        EN_9V
            EN_9V HVDC 
            Type : RW POR: 0b 
            0h = Disable 9V mode in HVDCP (default) 
            1h = Enable 9V mode in HVDCP
        HVDCP_EN
            High voltage DCP enable. 
            Type : RW POR: 0b 
            0h = Disable HVDCP handshake (default) 
            1h = Enable HVDCP handshake
        SDRV_CTRL
            SFET control The external ship FET control logic to force the device enter different modes. 
            Type : RW POR: 00b 
            0h = IDLE (default) 
            1h = Shutdown Mode 
            2h = Ship Mode 
            3h = System Power Reset
        SDRV_DLY
            Delay time added to the taking action in bit [2:1] of the SFET control 
            Type : RW POR: 0b 
            0h = Add 10s delay time (default) 
            1h = Do NOT add 10s delay time
        """
        def __init__(self, addr=0x11, value = 0x40):
            super().__init__(addr, value)
            self.FORCE_INDET   = ((self._value & 0b10000000) >> 7)
            self.AUTO_INDET_EN = ((self._value & 0b01000000) >> 6)
            self.EN_12V        = ((self._value & 0b00100000) >> 5)
            self.EN_9V         = ((self._value & 0b00010000) >> 4)
            self.HVDCP_EN      = ((self._value & 0b00001000) >> 3)
            self.SDRV_CTRL     = ((self._value & 0b00000110) >> 1)
            self.SDRV_DLY      = ((self._value & 0b00000001) >> 0)
        def set (self, value):
            super().set(value)
            self.FORCE_INDET   = ((self._value & 0b10000000) >> 7)
            self.AUTO_INDET_EN = ((self._value & 0b01000000) >> 6)
            self.EN_12V        = ((self._value & 0b00100000) >> 5)
            self.EN_9V         = ((self._value & 0b00010000) >> 4)
            self.HVDCP_EN      = ((self._value & 0b00001000) >> 3)
            self.SDRV_CTRL     = ((self._value & 0b00000110) >> 1)
            self.SDRV_DLY      = ((self._value & 0b00000001) >> 0)
        def get (self):
            self._value = (self.FORCE_INDET << 7) | (self.AUTO_INDET_EN << 6) | (self.EN_12V << 5) | (self.EN_9V << 4) | (self.HVDCP_EN << 3) | (self.SDRV_CTRL << 1) | (self.SDRV_DLY)
            return self._value, self.SDRV_DLY, self.SDRV_CTRL, self.HVDCP_EN, self.EN_9V, self.EN_12V, self.AUTO_INDET_EN, self.FORCE_INDET
        
    class REG13_Charger_Control_4(BQ25795_REGISTER):
        """
        BQ25795 - REG13_Charger_Control_4
        ----------
        EN_ACDRV2
            External ACFET2-RBFET2 gate driver control At POR, if the charger detects that there is no ACFET2-RBFET2 populated, this bit will be locked at 0 
            Type : RW POR: 0b 
            0h = turn off (default) 
            1h = turn on
        EN_ACDRV1
            External ACFET1-RBFET1 gate driver control At POR, if the charger detects that there is no ACFET1-RBFET1 populated, this bit will be locked at 0 
            Type : RW POR: 0b 
            0h = turn off (default) 
            1h = turn on
        PWM_FREQ
            Switching frequency selection, this bit POR default value is based on the PROG pin strapping. 
            Type : RW 
            0h = 1.5 MHz 
            1h = 750 kHz
        DIS_STAT
            Disable the STAT pin output 
            Type : RW POR: 0b 
            0h = Enable (Default) 
            1h = Disable
        DIS_VSYS_SHORT
            Disable forward mode VSYS short hiccup protection. 
            Type : RW POR: 0b 
            0h = Enable (Default) 
            1h = Disable
        DIS_VOTG_UVP
            Disable OTG mode VOTG UVP hiccup protection. 
            Type : RW POR: 0b 
            0h = Enable (Default) 
            1h = Disable
        FORCE_VINDPM_DET
            Force VINDPM detection Note: only when VBAT>VSYSMIN, this bit can be set to 1. Once the VINDPM auto detection is done, this bits returns to 0. 
            Type : RW POR: 0b 
            0h = Do NOT force VINDPM detection (default) 
            1h = Force the converter stop switching, and ADC measures the VBUS voltage without input current, then the charger updates the VINDPM register accordingly.
        EN_IBUS_OCP
            Enable IBUS_OCP in forward mode 
            Type : RW POR: 1b 
            0h = Disable 
            1h = Enable (default)
        """
        def __init__(self, addr=0x13, value = 0):
            super().__init__(addr, value)
            self.EN_ACDRV2          = ((self._value & 0b10000000) >> 7)
            self.EN_ACDRV1          = ((self._value & 0b01000000) >> 6)
            self.PWM_FREQ           = ((self._value & 0b00100000) >> 5)
            self.DIS_STAT           = ((self._value & 0b00010000) >> 4)
            self.DIS_VSYS_SHORT     = ((self._value & 0b00001000) >> 3)
            self.DIS_VOTG_UVP       = ((self._value & 0b00000100) >> 2)
            self.FORCE_VINDPM_DET   = ((self._value & 0b00000010) >> 1)
            self.EN_IBUS_OCP        = ((self._value & 0b00000001) >> 0)
        def set (self, value):
            super().set(value)
            self.EN_ACDRV2          = ((self._value & 0b10000000) >> 7)
            self.EN_ACDRV1          = ((self._value & 0b01000000) >> 6)
            self.PWM_FREQ           = ((self._value & 0b00100000) >> 5)
            self.DIS_STAT           = ((self._value & 0b00010000) >> 4)
            self.DIS_VSYS_SHORT     = ((self._value & 0b00001000) >> 3)
            self.DIS_VOTG_UVP       = ((self._value & 0b00000100) >> 2)
            self.FORCE_VINDPM_DET   = ((self._value & 0b00000010) >> 1)
            self.EN_IBUS_OCP        = ((self._value & 0b00000001) >> 0)
        def get (self):
            self._value =  (self.EN_ACDRV2 << 7) | (self.EN_ACDRV1 << 6) | (self.PWM_FREQ << 5) | (self.DIS_STAT << 4) | (self.DIS_VSYS_SHORT << 3) | (self.DIS_VOTG_UVP << 2) | (self.FORCE_VINDPM_DET << 1) | (self.EN_IBUS_OCP)
            return self._value, self.EN_ACDRV2, self.EN_ACDRV1, self.PWM_FREQ, self.DIS_STAT, self.DIS_VSYS_SHORT, self.DIS_VOTG_UVP, self.FORCE_VINDPM_DET, self.EN_IBUS_OCP 
    class REG14_Charger_Control_5(BQ25795_REGISTER):
        """
        BQ25795 - REG14_Charger_Control_5
        ----------
        SFET_PRESENT
            The user has to set this bit based on whether a ship FET is populated or not. 
            The POR default value is 0, which means the charger does not support all the features associated with the ship FET. 
            The register bits list below all are locked at 0. 
            EN_BATOC=0 FORCE_SFET_OFF=0 SDRV_CTRL=00 
            When this bit is set to 1, the register bits list above become programmable, and the charger can support the features associated with the ship FET 
            Type : RW POR: 0b 
            0h = No ship FET populated 
            1h = Ship FET populated
        EN_IBAT
            IBAT discharge current sensing enable for ADC 
            Type : RW POR: 0b 
            0h = Disable IBAT discharge current sensing for ADC (default) 
            1h = Enable the IBAT discharge current sensing for ADC
        IBAT_REG
            Battery discharging current regulation in OTG mode 
            Type : RW POR: 10b 
            0h = 3A 
            1h = 4A 
            2h = 5A (default) 
            3h = Disable
        EN_IINDPM
            Enable the internal IINDPM register input current regulation 
            Type : RW POR: 1b 
            0h = Disable 
            1h = Enable (default)
        EN_EXTILIM
            Enable the external ILIM_HIZ pin input current regulation 
            Type : RW POR: 1b 
            0h = Disable 
            1h = Enable (default)
        EN_BATOC
            Enable the battery discharging current OCP 
            Type : RW POR: 0b 
            0h = Disable (default) 
            1h = Enable
        """
        def __init__(self, addr=0x14, value = 0x16):
            super().__init__(addr, value)
            self.SFET_PRESENT           = ((self._value & 0b10000000) >> 7)
            self.EN_IBAT                = ((self._value & 0b00100000) >> 5)
            self.IBAT_REG               = ((self._value & 0b00011000) >> 3)
            self.EN_IINDPM              = ((self._value & 0b00000100) >> 2)
            self.EN_EXTILIM             = ((self._value & 0b00000010) >> 1)
            self.EN_BATOC               = ((self._value & 0b00000001) >> 0)
        def set (self, value):
            super().set(value)
            self.SFET_PRESENT           = ((self._value & 0b10000000) >> 7)
            self.EN_IBAT                = ((self._value & 0b00100000) >> 5)
            self.IBAT_REG               = ((self._value & 0b00011000) >> 3)
            self.EN_IINDPM              = ((self._value & 0b00000100) >> 2)
            self.EN_EXTILIM             = ((self._value & 0b00000010) >> 1)
            self.EN_BATOC               = ((self._value & 0b00000001) >> 0)
        def get (self):
            self._value =  (self.SFET_PRESENT << 7) | 0 | (self.EN_IBAT << 5) | (self.IBAT_REG << 3) | (self.EN_IINDPM << 2) | (self.EN_EXTILIM << 1) | self.EN_BATOC
            return self._value, self.SFET_PRESENT, self.EN_IBAT, self.IBAT_REG, self.EN_IINDPM, self.EN_EXTILIM, self.EN_BATOC

    class REG16_Temperature_Control(BQ25795_REGISTER):
        """
        BQ25795 - REG16_Temperature_Control
        ----------
        TREG
            Thermal regulation thresholds. 
            Type : RW POR: 11b 
            0h = 60°C 
            1h = 80°C 
            2h = 100°C 
            3h = 120°C (default)
        TSHUT
            Thermal shutdown thresholds. 
            Type : RW POR: 00b 
            0h = 150°C (default) 
            1h = 130°C 
            2h = 120°C 
            3h = 85°C
        VBUS_PD_EN
            Enable VBUS pull down resistor (6k Ohm) 
            Type : RW POR: 0b 
            0h = Disable (default) 
            1h = Enable
        VAC1_PD_EN 
            Enable VAC1 pull down resistor 
            Type : RW POR: 0b 
            0h = Disable (default) 
            1h = Enable
        VAC2_PD_EN
             Enable VAC2 pull down resistor 
             Type : RW POR: 0b 
             0h = Disable (default) 
             1h = Enable
        """
        def __init__(self, addr=0x16, value = 0xc0):
            super().__init__(addr, value)
            self.TREG                   = ((self._value & 0b11000000) >> 6)
            self.TSHUT                  = ((self._value & 0b00110000) >> 4)
            self.VBUS_PD_EN             = ((self._value & 0b00001000) >> 3)
            self.VAC1_PD_EN             = ((self._value & 0b00000100) >> 2)
            self.VAC2_PD_EN             = ((self._value & 0b00000010) >> 1)
        def set (self, value):
            super().set(value)
            self.TREG                   = ((self._value & 0b11000000) >> 6)
            self.TSHUT                  = ((self._value & 0b00110000) >> 4)
            self.VBUS_PD_EN             = ((self._value & 0b00001000) >> 3)
            self.VAC1_PD_EN             = ((self._value & 0b00000100) >> 2)
            self.VAC2_PD_EN             = ((self._value & 0b00000010) >> 1)
        def get (self):
            self._value =  (self.TREG << 6) | (self.TSHUT << 4) | (self.VBUS_PD_EN << 3) | (self.VAC1_PD_EN << 2) | (self.VAC2_PD_EN << 1) | 0
            return self._value,   self.TREG,  self.TSHUT, self.VBUS_PD_EN, self.VAC1_PD_EN, self.VAC2_PD_EN
        
        def get_thermal_reg_threshold(self):
            if self.TREG == 0x0: return "60°C"
            elif self.TREG == 0x1: return"80°C"
            elif self.TREG == 0x2: return "100°C"
            elif self.TREG == 0x3: return "120°C"
            else: return "unknown" 
        def get_thermal_shutdown_threshold(self):
            if self.TSHUT == 0x0: return "150°C"
            elif self.TSHUT == 0x1: return"130°C"
            elif self.TSHUT == 0x2: return "120°C"
            elif self.TSHUT == 0x3: return "85°C"
            else: return "unknown" 
    
    class REG19_ICO_Current_Limit(BQ25795_REGISTER):
        """
        BQ25795 - REG19_ICO_Current_Limit
        -----------
        ICO_ILIM - Input Current Limit obtained from ICO or ILIM_HIZ pin setting 
        Type : R POR: 0mA (0h) 
        Range : 100mA-3300mA 
        Fixed Offset : 0mA 
        Bit Step Size : 10mA 
        Clamped Low
        """
        def __init__(self, addr=0x19, value = 0):
            super().__init__(addr, value)
            self.ICO_ILIM           = ((self._value & 0b0000000111111111))
        def set (self, value):
            super().set(value)
            self.ICO_ILIM           = ((self._value & 0b0000000111111111))
        def get (self):
            return self._value, self.ICO_ILIM
        def get_ICO_ILIM (self):
            '''return Input Current Limit obtained from ICO or ILIM_HIZ pin setting in [mA]'''
            return self.ICO_ILIM*10
        
    class REG1C_Charger_Status_1(BQ25795_REGISTER):
        """
        BQ25795 - REG1C_Charger_Status_1
        ----------
        CHG_STAT
            Charge Status bits 
            Type : R POR: 000b 
            0h = Not Charging 
            1h = Trickle Charge 
            2h = Pre-charge 
            3h = Fast charge (CC mode) 
            4h = Taper Charge (CV mode) 
            5h = Reserved 
            6h = Top-off Timer Active Charging 
            7h = Charge Termination Done
        VBUS_STAT
            VBUS status bits 
            0h: No Input or BHOT or BCOLD in OTG mode 
            1h: USB SDP (500mA) 
            2h: USB CDP (1.5A) 
            3h: USB DCP (3.25A) 
            4h: Adjustable High Voltage DCP (HVDCP) (1.5A) 
            5h: Unknown adaptor (3A) 
            6h: Non-Standard Adapter (1A/2A/2.1A/2.4A) 
            7h: In OTG mode 
            8h: Not qualified adaptor 
            9h: Reserved 
            Ah: Reserved 
            Bh: Device directly powered from VBUS 
            Ch: Reserved Dh: Reserved Eh: Reserved Fh: Reserved 
            Type : R 
            POR: 0h
        """
        def __init__(self, addr=0x1C, value = 0):
            super().__init__(addr, value)
            self.CHG_STAT           = ((self._value & 0b11100000) >> 5)
            self.VBUS_STAT          = ((self._value & 0b00011110) >> 1)
            self.CHG_STAT_STRG      = self.chg_stat_get_string(self.CHG_STAT)
        def set (self, value):
            super().set(value)
            self.CHG_STAT           = ((self._value & 0b11100000) >> 5)
            self.VBUS_STAT          = ((self._value & 0b00011110) >> 1)
            self.CHG_STAT_STRG      = self.chg_stat_get_string(self.CHG_STAT)
        def get (self):
            return self._value, self.CHG_STAT, self.VBUS_STAT, self.CHG_STAT_STRG
        def chg_stat_get_string (self, CHG_STAT):
            '''
            CHG_STAT
            Charge Status bits 
            Type : R POR: 000b 
            0h = Not Charging 
            1h = Trickle Charge 
            2h = Pre-charge 
            3h = Fast charge (CC mode) 
            4h = Taper Charge (CV mode) 
            5h = Reserved 
            6h = Top-off Timer Active Charging 
            7h = Charge Termination Done
            '''
            if CHG_STAT == 0x0: return "Not Charging"
            elif CHG_STAT == 0x1: return"Trickle Charge"
            elif CHG_STAT == 0x2: return "Pre-charge"
            elif CHG_STAT == 0x3: return "Fast charge (CC mode)"
            elif CHG_STAT == 0x4: return "Taper Charge (CV mode)"
            elif CHG_STAT == 0x5: return "Reserved"
            elif CHG_STAT == 0x6: return "Top-off Timer Active Charging"
            elif CHG_STAT == 0x7: return "Charge Termination Done"
            else: return "Reserved"

    class REG1D_Charger_Status_2(BQ25795_REGISTER):
        """
        BQ25795 - REG1D_Charger_Status_2
        ----------
        ICO_STAT
            Input Current Optimizer (ICO) status 
            Type : R POR: 00b 
            0h = ICO disabled 
            1h = ICO optimization in progress 
            2h = Maximum input current detected 
            3h = Reserved
        TREG_STAT
            IC thermal regulation status 
            Type : R POR: 0b 
            0h = Normal 
            1h = Device in thermal regulation
        DPDM_STAT
            D+/D- detection status bits 
            Type : R POR: 0b 
            0h = The D+/D- detection is NOT started yet, or the detection is done 
            1h = The D+/D- detection is ongoing
        VBAT_PRESENT_STAT
            Battery present status (VBAT > VBAT_UVLOZ) 
            Type : R POR: 0b 
            0h = VBAT NOT present 
            1h = VBAT present
        """
        def __init__(self, addr=0x1D, value = 0):
            super().__init__(addr, value)
            self.ICO_STAT           = ((self._value & 0b11000000) >> 6)
            self.TREG_STAT          = ((self._value & 0b00000100) >> 2)
            self.DPDM_STAT          = ((self._value & 0b00000010) >> 1)
            self.VBAT_PRESENT_STAT  = ((self._value & 0b00000001) >> 0)
        def set (self, value):
            super().set(value)
            self.ICO_STAT           = ((self._value & 0b11000000) >> 6)
            self.TREG_STAT          = ((self._value & 0b00000100) >> 2)
            self.DPDM_STAT          = ((self._value & 0b00000010) >> 1)
            self.VBAT_PRESENT_STAT  = ((self._value & 0b00000001) >> 0)
        def get (self):
            return self._value, self.ICO_STAT, self.TREG_STAT, self.DPDM_STAT, self.VBAT_PRESENT_STAT
        def get_thermal_regulation_status(self):
            ''' 
            Returns IC thermal regulation status 
            0h = Normal 
            1h = Device in thermal regulation
            '''
            if self.TREG_STAT == 0: return "Normal"
            elif self.TREG_STAT == 1: return "Device in thermal regulation"
            else: return "unknown"


    class REG2E_ADC_Control(BQ25795_REGISTER):
        """
        BQ25795 - REG2E_ADC_Control
        ----------
        ADC_EN
            ADC Control 
            Type : RW POR: 0b 
            0h = Disable 
            1h = Enable
        ADC_RATE
            ADC conversion rate control 
            Type : RW POR: 0b 
            0h = Continuous conversion 
            1h = One shot conversion
        ADC_SAMPLE
            ADC sample speed 
            Type : RW POR: 11b 
            0h = 15 bit effective resolution 
            1h = 14 bit effective resolution 
            2h = 13 bit effective resolution 
            3h = 12 bit effective resolution (default - not recommended)
        ADC_AVG
            ADC average control 
            Type : RW POR: 0b 
            0h = Single value 
            1h = Running average
        ADC_AVG_INIT
            ADC average initial value control 
            Type : RW POR: 0b 
            0h = Start average using the existing register value 
            1h = Start average using a new ADC conversion
        """
        def __init__(self, addr=0x2e, value = 0):
            super().__init__(addr, value)
            self.ADC_EN             = ((self._value & 0b10000000) >> 7)
            self.ADC_RATE           = ((self._value & 0b01000000) >> 6)
            self.ADC_SAMPLE         = ((self._value & 0b00110000) >> 4)
            self.ADC_AVG            = ((self._value & 0b00001000) >> 3)
            self.ADC_AVG_INIT       = ((self._value & 0b00000100) >> 2)
        def set (self, value):
            super().set(value)
            self.ADC_EN             = ((self._value & 0b10000000) >> 7)
            self.ADC_RATE           = ((self._value & 0b01000000) >> 6)
            self.ADC_SAMPLE         = ((self._value & 0b00110000) >> 4)
            self.ADC_AVG            = ((self._value & 0b00001000) >> 3)
            self.ADC_AVG_INIT       = ((self._value & 0b00000100) >> 2)
        def get(self):
            self._value = (self.ADC_EN << 7) | (self.ADC_RATE << 6) | (self.ADC_SAMPLE << 4) | (self.ADC_AVG << 3) | (self.ADC_AVG_INIT << 2) | 0b00
            return self._value, self.ADC_EN, self.ADC_RATE, self.ADC_SAMPLE, self.ADC_AVG, self.ADC_AVG_INIT
    class REG31_IBUS_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG31_IBUS_ADC
        ----------
            IBUS_ADC
                IBUS ADC reading Reported in 2 's Complement. 
                When the current is flowing from VBUS to PMID, IBUS ADC reports positive value, and when the current is flowing from PMID to VBUS, IBUS ADC reports negative value. 
                Type : R POR: 0mA (0h) 
                Range : 0mA-5000mA 
                Fixed Offset : 0mA 
                Bit Step Size : 1mA
        """
        def __init__(self, addr=0x31, value = 0):
            super().__init__(addr, value)
            self.IBUS_ADC             = super().twos_complement()
        def set (self, value):
            super().set(value)
            self.IBUS_ADC             = super().twos_complement()
        def get(self):
            return self._value, self.IBUS_ADC
        def get_Ibus(self):
            return self.IBUS_ADC
        
    class REG33_IBAT_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG33_IBAT_ADC
        ----------
            IBAT_ADC
                IBAT ADC reading Reported in 2 's Complement. 
                The IBAT ADC reports positive value for the battery charging current, and negative value for the battery discharging current if EN_IBAT in REG0x14[5] = 1. 
                Type : R POR: 0mA (0h) 
                Range : 0mA-8000mA 
                Fixed Offset : 0mA 
                Bit Step Size : 1mA
        """
        def __init__(self, addr=0x33, value = 0):
            super().__init__(addr, value)
            self.IBAT_ADC             = super().twos_complement()
        def set (self, value):
            super().set(value)
            self.IBAT_ADC             = super().twos_complement()
        def get(self):
            return self._value, self.IBAT_ADC
        def get_Ibat(self):
            return self.IBAT_ADC
        
    class REG35_VBUS_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG35_VBUS_ADC
        ----------
            VBUS_ADC
                VBUS ADC reading 
                Type : R POR: 0mV (0h) 
                Range : 0mV-30000mV 
                Fixed Offset : 0mV Bit Step Size : 1mV
        """
        def __init__(self, addr=0x35, value = 0):
            super().__init__(addr, value)
            self.VBUS_ADC             = self._value
        def set (self, value):
            super().set(value)
            self.VBUS_ADC             = self._value
        def get(self):
            return self._value, self.VBUS_ADC  
        def get_Vbus(self):
            return self.VBUS_ADC  
          
    class REG37_VAC1_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG37_VAC1_ADC
        ----------
            VAC1_ADC
                VAC1 ADC reading. 
                Type : R POR: 0mV (0h) 
                Range : 0mV-30000mV 
                Fixed Offset : 0mV Bit Step Size : 1mV
        """
        def __init__(self, addr=0x37, value = 0):
            super().__init__(addr, value)
            self.VAC1_ADC             = self._value
        def set (self, value):
            super().set(value)
            self.VAC1_ADC             = self._value
        def get(self):
            return self._value, self.VAC1_ADC    
    
    class REG39_VAC2_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG39_VAC2_ADC
        ----------
            VAC2_ADC
                VAC2 ADC reading. 
                Type : R POR: 0mV (0h) 
                Range : 0mV-30000mV 
                Fixed Offset : 0mV Bit Step Size : 1mV
        """
        def __init__(self, addr=0x39, value = 0):
            super().__init__(addr, value)
            self.VAC2_ADC             = self._value
        def set (self, value):
            super().set(value)
            self.VAC2_ADC             = self._value
        def get(self):
            return self._value, self.VAC2_ADC

    class REG3B_VBAT_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG3B_VBAT_ADC
        ----------
            VBAT_ADC
                The battery remote sensing voltage (VBATP-GND) ADC reading 
                Type : R POR: 0mV (0h) 
                Range : 0mV-20000mV 
                Fixed Offset : 0mV 
                Bit Step Size : 1mV
        """
        def __init__(self, addr=0x3B, value = 0):
            super().__init__(addr, value)
            self.VBAT_ADC             = self._value
        def set (self, value):
            super().set(value)
            self.VBAT_ADC             = self._value
        def get(self):
            return self._value, self.VBAT_ADC
        def get_Vbat(self):
            return self.VBAT_ADC
    
    class REG3D_VSYS_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG3D_VSYS_ADC
        ----------
            VSYS_ADC
                VSYS ADC reading Type : R POR: 0mV (0h) 
                Range : 0mV-24000mV 
                Fixed Offset : 0mV 
                Bit Step Size : 1mV
        """
        def __init__(self, addr=0x3D, value = 0):
            super().__init__(addr, value)
            self.VSYS_ADC             = self._value
        def set (self, value):
            super().set(value)
            self.VSYS_ADC             = self._value
        def get(self):
            return self._value, self.VSYS_ADC

    class REG41_TDIE_ADC(BQ25795_REGISTER):
        """
        BQ25795 - REG41_TDIE_ADC
        ----------
            TDIE_ADC
                TDIE ADC reading Reported in 2 's Complement. 
                Type : R POR: 0°C (0h) 
                Range : -40°C-150°C 
                Fixed Offset : 0°C 
                Bit Step Size : 0.5°C
        """
        def __init__(self, addr=0x41, value = 0):
            super().__init__(addr, value)
            self.TDIE_ADC             = super().twos_complement()
            self.TemperatureIC       = self.TDIE_ADC*0.5
        def set (self, value):
            super().set(value)
            self.TDIE_ADC             = super().twos_complement()
            self.TemperatureIC       = self.TDIE_ADC*0.5
        def get(self):
            return self._value, self.TDIE_ADC, self.TemperatureIC
        def get_IC_temperature(self):
            '''
            Get Temperature of BQ2595 IC in °C
            '''
            return self.TemperatureIC 
        
    # class methods
    def safe_execute(self, func, *args, **kwargs):
        """
        Executes a function safely, catching exceptions and handling errors.
        If `_exit_on_error` is True, the program will exit on error.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            sys.stderr.write(f"Error in {func.__name__}: {str(e)}\n")
            if self._exit_on_error:
                sys.exit(1)
            raise I2CError(f"Failed to execute {func.__name__}") from e

    def read_register(self, reg_addr, length=1):
        """
        Reads data from a register safely using the `safe_execute` method.
        """
        return self.safe_execute(self.bq.read_i2c_block_data, self.i2c_addr, reg_addr, length)

    def write_register(self, reg):
        """
        Writes a single-byte register value safely.
        """
        reg.get()
        self.safe_execute(self.bq.write_byte_data, self.i2c_addr, reg._addr, reg._value)

    def write_register_word(self, reg):
        """
        Writes a two-byte register value safely.
        """
        reg.get()
        self.safe_execute(self.bq.write_byte_data, self.i2c_addr, reg._addr, reg._value & 0xFF)
        self.safe_execute(self.bq.write_byte_data, self.i2c_addr, reg._addr + 1, (reg._value >> 8) & 0xFF)

   

    def read_TDIE_Temp(self):
        """
        Reads the TDIE_ADC register and returns the IC temperature in degrees Celsius.
        If the read operation fails, it returns the last known value.
        """
        try:
            reg_addr = self.REG41_TDIE_ADC._addr
            data = self.safe_execute(self.bq.read_i2c_block_data, self.i2c_addr, reg_addr, 2)
            if data:
                self.REG41_TDIE_ADC.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_TDIE_Temp failed, returning previous value.\n")
        return self.REG41_TDIE_ADC.get_IC_temperature()

    def read_Vbat(self) -> int:
        """
        Reads the VBAT_ADC register and returns the battery voltage in mV.
        """
        try:
            reg_addr = self.REG3B_VBAT_ADC._addr
            data = self.read_register(reg_addr, length=2)
            self.REG3B_VBAT_ADC.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_Vbat failed, returning previous value.\n")
        return self.REG3B_VBAT_ADC.get_Vbat()


    def read_Vbus(self):
        """
        Reads the VBUS_ADC register and returns the bus voltage in mV.
        If the read operation fails, it returns the last known value.
        """
        try:
            reg_addr = self.REG35_VBUS_ADC._addr
            data = self.safe_execute(self.bq.read_i2c_block_data, self.i2c_addr, reg_addr, 2)
            if data:
                self.REG35_VBUS_ADC.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_Vbus failed, returning previous value.\n")
        return self.REG35_VBUS_ADC.get_Vbus()

    def read_Ibus(self):
        """
        Reads the IBUS_ADC register and returns the bus current in mA.
        The IBUS ADC reading is reported in 2's complement.
        If the read operation fails, it returns the last known value.
        """
        try:
            reg_addr = self.REG31_IBUS_ADC._addr
            data = self.safe_execute(self.bq.read_i2c_block_data, self.i2c_addr, reg_addr, 2)
            if data:
                self.REG31_IBUS_ADC.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_Ibus failed, returning previous value.\n")
        return self.REG31_IBUS_ADC.get_Ibus()

    def read_Ibat(self) -> int:
        """
        Reads the IBAT_ADC register and returns the battery current in mA.
        """
        try:
            reg_addr = self.REG33_IBAT_ADC._addr
            data = self.read_register(reg_addr, length=2)
            self.REG33_IBAT_ADC.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_Ibat failed, returning previous value.\n")
        return self.REG33_IBAT_ADC.get_Ibat()


    def read_all_register(self):
        """
        Reads all BQ25792 registers and updates the class attributes.
        """
        try:
            val = [0xFF] * 73
            val[0:31] = self.read_register(0x0, 32)
            val[32:63] = self.read_register(0x20, 32)
            val[64:72] = self.read_register(0x40, 9)
            self.registers = val
            # Update register values
            self.REG00_Minimal_System_Voltage.set(self.registers[self.REG00_Minimal_System_Voltage._addr])
            self.REG01_Charge_Voltage_Limit.set((self.registers[self.REG01_Charge_Voltage_Limit._addr] << 8) | (self.registers[self.REG01_Charge_Voltage_Limit._addr+1]))
            self.REG03_Charge_Current_Limit.set((self.registers[self.REG03_Charge_Current_Limit._addr] << 8) | (self.registers[self.REG03_Charge_Current_Limit._addr+1]))
            self.REG05_Input_Voltage_Limit.set(self.registers[self.REG05_Input_Voltage_Limit._addr])
            self.REG06_Input_Current_Limit.set((self.registers[self.REG06_Input_Current_Limit._addr] << 8) | (self.registers[self.REG06_Input_Current_Limit._addr+1]))
            self.REG08_Precharge_Control.set(self.registers[self.REG08_Precharge_Control._addr])
            self.REG09_Termination_Control.set(self.registers[self.REG09_Termination_Control._addr])
            self.REG0A_Recharge_Control.set(self.registers[self.REG0A_Recharge_Control._addr])
            self.REG0B_VOTG_regulation.set(self.registers[self.REG0B_VOTG_regulation._addr]<< 8) | (self.registers[self.REG0B_VOTG_regulation._addr+1])  
            self.REG0F_Charger_Control_0.set(self.registers[self.REG0F_Charger_Control_0._addr])
            self.REG10_Charger_Control_1.set(self.registers[self.REG10_Charger_Control_1._addr])
            self.REG11_Charger_Control_2.set(self.registers[self.REG11_Charger_Control_2._addr])
            self.REG13_Charger_Control_4.set(self.registers[self.REG13_Charger_Control_4._addr])
            self.REG14_Charger_Control_5.set(self.registers[self.REG14_Charger_Control_5._addr])
            self.REG16_Temperature_Control.set(self.registers[self.REG16_Temperature_Control._addr])
            self.REG1C_Charger_Status_1.set(self.registers[self.REG1C_Charger_Status_1._addr])
            self.REG1D_Charger_Status_2.set(self.registers[self.REG1D_Charger_Status_2._addr])
            self.REG2E_ADC_Control.set(self.registers[self.REG2E_ADC_Control._addr])
            self.REG31_IBUS_ADC.set((self.registers[self.REG31_IBUS_ADC._addr] << 8) | (self.registers[self.REG31_IBUS_ADC._addr+1]))
            self.REG33_IBAT_ADC.set((self.registers[self.REG33_IBAT_ADC._addr] << 8) | (self.registers[self.REG33_IBAT_ADC._addr+1]))
            self.REG35_VBUS_ADC.set((self.registers[self.REG35_VBUS_ADC._addr] << 8) | (self.registers[self.REG35_VBUS_ADC._addr+1]))
            self.REG37_VAC1_ADC.set((self.registers[self.REG37_VAC1_ADC._addr] << 8) | (self.registers[self.REG37_VAC1_ADC._addr+1]))
            self.REG39_VAC2_ADC.set((self.registers[self.REG39_VAC2_ADC._addr] << 8) | (self.registers[self.REG39_VAC2_ADC._addr+1]))
            self.REG3B_VBAT_ADC.set((self.registers[self.REG3B_VBAT_ADC._addr] << 8) | (self.registers[self.REG3B_VBAT_ADC._addr+1]))
            self.REG3D_VSYS_ADC.set((self.registers[self.REG3D_VSYS_ADC._addr] << 8) | (self.registers[self.REG3D_VSYS_ADC._addr+1]))
            self.REG41_TDIE_ADC.set((self.registers[self.REG41_TDIE_ADC._addr] << 8) | (self.registers[self.REG41_TDIE_ADC._addr+1]))
            return 0
        except I2CError:
            sys.stderr.write("read_all_register failed.\n")
            return -1

    def read_InputCurrentLimit(self) -> int:
        """
        Reads the input current limit (ICO_ILIM) in mA.
        Returns the last known value if the read operation fails.
        """
        try:
            reg_addr = self.REG19_ICO_Current_Limit._addr
            data = self.read_register(reg_addr, length=2)
            self.REG19_ICO_Current_Limit.set((data[0] << 8) | data[1])
        except I2CError:
            sys.stderr.write("read_InputCurrentLimit failed, returning previous value.\n")
        return self.REG19_ICO_Current_Limit.get_ICO_ILIM()
                  

    def read_ChargerStatus(self) -> str:
        """
        Reads the charger status and returns the charge status string.
        """
        try:
            reg_addr = self.REG1C_Charger_Status_1._addr
            data = self.read_register(reg_addr, length=1)
            self.REG1C_Charger_Status_1.set(data[0])
        except I2CError:
            sys.stderr.write("read_ChargerStatus failed, returning previous value.\n")
        return self.REG1C_Charger_Status_1.CHG_STAT_STRG
    
    def soft_reset(self):
        """
        Performs a soft reset of the charger IC.
        """
        try:
            reg = self.REG09_Termination_Control
            reg.REG_RST = 1
            self.write_register(reg)
            time.sleep(0.1)
            reg = self.REG09_Termination_Control
            reg.REG_RST = 0
            self.write_register(reg)
            time.sleep(0.1)
            return 0
        except I2CError:
            sys.stderr.write("soft_reset failed.\n")
            return -1

    def write_defaults(self):
        '''
        Write default settings to the charger IC.   
        ''' 
        #Watchdog
        reg = self.REG10_Charger_Control_1
        #reg.WATCHDOG = 0 #disable watchdog
        reg.WD_RST = 1 #reset watchdog
        reg.WATCHDOG = 7 #160s watchdog
        self.write_register(reg)

        # Thermal Regulation Threshold - a bit more conservative
        reg = self.REG16_Temperature_Control
        reg.TREG = 0x2 #100°C
        reg.TSHUT = 0x2 #120°C
        self.write_register(reg)

        reg = self.REG2E_ADC_Control
        reg.ADC_EN = 1
        reg.ADC_SAMPLE = 0 # 15bit resolution
        reg.ADC_AVG = 0 # running avg
        reg.ADC_AVG_INIT = 0 
        self.write_register(reg)

        reg = self.REG0F_Charger_Control_0
        reg.EN_TERM = 1 # Enable Charge Termination
        self.write_register(reg)

        reg = self.REG14_Charger_Control_5
        reg.EN_IBAT = 1 # Enable the IBAT discharge current sensing for ADC
        self.write_register(reg)
        
        #self.enable_extilim()
        self.disable_extilim()
        self.set_input_current_limit(2200) # todo this value to be taken from json
        return

    def MuPiHAT_Default(self):
        ''' 
        Write MuPiHAT Default Settings to Charger IC
        '''
        #self.soft_reset()
        self.read_all_register()
        self.write_defaults()
        #tries = 0
        #max_tries = 3
        #while tries < max_tries:
        #    if (self.read_all_register()) == 0:
        #        self.write_defaults()
        #        return 0
        #    else:
        #        tries += 1
        #return -1

    def get_IC_temperature(self):
        '''
        reads and return IC temperature of charger IC 
        '''
        self.read_all_register()
        return self.REG41_TDIE_ADC.get_IC_temperature()

    def disable_extilim(self):
        '''
        Diable External ILIM_HIZ Input Current Limit pin input
        '''
        try:
            # first read register
            reg_addr = self.REG14_Charger_Control_5._addr
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG14_Charger_Control_5.set((self.registers[reg_addr]))
            # then set bit
            self.REG14_Charger_Control_5.EN_EXTILIM = 0
            self.REG14_Charger_Control_5.get()
            # now write back
            self.write_register(self.REG14_Charger_Control_5)
            return 0
        except Exception as _error:
            sys.stderr.write('disable_extilim failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass

    def enable_extilim(self):
        '''
        Enable External ILIM_HIZ Input Current Limit pin input
        '''
        try:
            #self.read_all_register()
            # first read register
            reg_addr = self.REG14_Charger_Control_5._addr
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG14_Charger_Control_5.set((self.registers[reg_addr]))
            # then set bit
            self.REG14_Charger_Control_5.EN_EXTILIM = 1
            self.REG14_Charger_Control_5.get()
            # now write back
            self.write_register(self.REG14_Charger_Control_5)
            return 0
        except Exception as _error:
            sys.stderr.write('disable_extilim failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass

    def enable_HVDCP(self):
        '''
        Enable High voltage DCP
        Do not use. Not tested!
        TODO Follow Datsheet 9.3.4.5.2 HVDCP Detection Procedure
        '''
        try:
            # first read register
            reg_addr = self.REG11_Charger_Control_2._addr
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG11_Charger_Control_2.set((self.registers[reg_addr]))
            # then set bit
            self.REG11_Charger_Control_2.HVDCP_EN = 1
            self.REG11_Charger_Control_2.get()
            # now write back
            self.write_register(self.REG11_Charger_Control_2)
            return 0
        except Exception as _error:
            sys.stderr.write('enable_HVDCP failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass

    def read_REG14_Charger_Control_5(self):
        '''
        Read read_REG14_Charger_Control_5
        Return register value
        '''
        try:
            #self.read_all_register()
            # first read register
            reg_addr = self.REG14_Charger_Control_5._addr
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG14_Charger_Control_5.set((self.registers[reg_addr]))
            value, SFET_PRESENT, EN_IBAT, IBAT_REG, EN_IINDPM, EN_EXTILIM, EN_BATOC = self.REG14_Charger_Control_5.get()
            return value
        except Exception as _error:
            sys.stderr.write('read_REG14_Charger_Control_5 failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass

    def read_EN_CHG(self):
        '''
        Read read_REG0F_Charger_Control_0 and return value of Charger Enable Configuration
        Return Value
        ---------
          0h = Charge Disable
          1h = Charge Enable
        '''
        try:
            #self.read_all_register()
            # first read register
            reg_addr = self.REG0F_Charger_Control_0._addr 
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG0F_Charger_Control_0.set((self.registers[reg_addr]))
            value, EN_AUTO_IBATDIS, FORCE_IBATDIS, EN_CHG, EN_ICO, FORCE_ICO, EN_HIZ, EN_TERM = self.REG0F_Charger_Control_0.get()
            return EN_CHG
        except Exception as _error:
            sys.stderr.write('read_EN_CHG failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            return -1
        finally:
            pass
    def read_VBAT_PRESENT(self):
        '''
        Read REG1D_Charger_Status_2 and return value VBAT_PRESENT_STAT
        Return Value
        ---------
          0h = VBAT NOT present 
          1h = VBAT present
        '''
        try:
            #self.read_all_register()
            # first read register
            reg_addr = self.REG1D_Charger_Status_2._addr 
            val = self.bq.read_byte_data(self.i2c_addr, reg_addr)
            self.registers[reg_addr] = val
            self.REG1D_Charger_Status_2.set((self.registers[reg_addr]))
            value, ICO_STAT, TREG_STAT, DPDM_STAT, VBAT_PRESENT_STAT = self.REG1D_Charger_Status_2.get()
            return VBAT_PRESENT_STAT
        except Exception as _error:
            sys.stderr.write('read_VBAT_PRESENT failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
            value, ICO_STAT, TREG_STAT, DPDM_STAT, VBAT_PRESENT_STAT = self.REG1D_Charger_Status_2.get()
            return VBAT_PRESENT_STAT
        finally:
            pass

    def set_input_current_limit(self, input_current_limit):
        '''
        set ILIM
        '''
        try:
            reg = self.REG06_Input_Current_Limit
            reg.set_input_current_limit(input_current_limit)
            self.bq.write_byte_data(self.i2c_addr, reg._addr, (reg._value >> 8))
            self.bq.write_byte_data(self.i2c_addr, reg._addr+1, reg._value)
            #sys.stderr.write('set_input_current_limit to: %s\n' % str(reg._value))
            #self.read_all_register()
            #sys.stderr.write('get_input_current_limit to: %s\n' % str(reg._value))
            pass
        except Exception as _error:
            sys.stderr.write('set_input_current_limit failed, %s\n' % str(_error))
            if self._exit_on_error: sys.exit(1)
        finally:
            pass



    def get_ibat(self) -> int:
        """
        Get the IBAT current in mA, reports positive value for the battery charging current, and negative value for the battery discharging current
        """
        return self.REG33_IBAT_ADC.IBAT_ADC
    
    def get_ibus(self) -> int:
        """
        Get the IBUS current in mA
        """
        return self.REG31_IBUS_ADC.IBUS_ADC
    
    def get_vbat(self) -> int:
        """
        Get the VBAT Battery Voltage  in mV
        """
        return self.REG3B_VBAT_ADC.VBAT_ADC
    def get_vbus(self) -> int:
        """
        Get the VBUS Bus Voltage  in mV
        """

        return self.REG35_VBUS_ADC.VBUS_ADC
    
    def bq25792_REG1C_Charger_Status_1(self, i2c_read=True):
        if i2c_read:
            self.read_all_register()
        val = self.registers[self.REG1C_Charger_Status_1]
        CHG_STAT = val >> 5
        if CHG_STAT == 0x0: ret = 'Not Charging'
        elif CHG_STAT == 0x01: ret = 'Trickle Charge'
        elif CHG_STAT == 0x02: ret = 'Pre-Charge'
        elif CHG_STAT == 0x03: ret = 'Fast-Charge'
        elif CHG_STAT == 0x04: ret = 'Taper-Charge'
        elif CHG_STAT == 0x05: ret = 'Reserved'
        elif CHG_STAT == 0x06: ret = 'Top-off Timer Active Charging'
        elif CHG_STAT == 0x07: ret = 'Charge Termination Done' 
        else: ret = CHG_STAT
        return val, ret 
    
    def bq25792_REG0F_Charger_Control_0(self, i2c_read=True):
        if i2c_read:
            self.read_all_register()
        val = self.registers[self.REG0F_Charger_Control_0]
        EN_AUTO_IBATDIS = ((val & 0b10000000) == 128)
        FORCE_IBATDIS   = ((val & 0b01000000) == 64)
        EN_CHG          = ((val & 0b00100000) == 32)
        EN_ICO          = ((val & 0b00010000) == 16)
        FORCE_ICO       = ((val & 0b00001000) == 8)
        EN_HIZ          = ((val & 0b00000100) == 4)
        EN_TERM         = ((val & 0b00000010) == 2)
        return val, EN_AUTO_IBATDIS, FORCE_IBATDIS, EN_CHG, EN_ICO, FORCE_ICO, EN_HIZ, EN_TERM

    def to_json(self):
        '''
        Returns json input
        
        Output Values
        ------

        'Charger_Status'
            Not Charging 
            Trickle Charge 
            Pre-charge 
            Fast charge (CC mode) 
            Taper Charge (CV mode) 
            Reserved 
            Top-off Timer Active Charging 
            Charge Termination Done
        'VBus'
            Bus Power (USB-C or from J2) in mV
        'Vbat'
            Battery Voltage in mV
        'Ibat'
            Battery Current in mA, reports positive value for the battery charging current, and negative value for the battery discharging current
        'IBus'
            Bus Current in mA
        'Temp'
            Temperature of Charger IC
        'BatteryConnected'
            0 = Battery not present 
            1 = Battery present
        'Bat_SOC'
            Estimated State-oF-Charge of Battery (based on VBat) and Battery Config File
        'Bat_Stat'
            Battery Status - Indication for Front-End, (OK, LOW, SHUTDOWN)
        'Bat_Type'
            Battery Type as read from Battery Config File
        'Input_Current_Limit'
            Input Current Limit obtained from ICO or ILIM_HIZ pin setting
        '''
        #self.read_all_register()
        self.write_defaults()

        bat_SOC, bat_Stat = self.battery_soc()
        return {
            'Charger_Status': self.read_ChargerStatus(),
            'Vbat': self.read_Vbat(),
            'Vbus': self.read_Vbus(),
            'Ibat': self.read_Ibat(),
            'IBus': self.read_Ibus(),
            'Temp': self.read_TDIE_Temp(),
            'BatteryConnected' : self.read_VBAT_PRESENT(),
            #'REG14' : self.read_REG14_Charger_Control_5(),
            'Bat_SOC' : bat_SOC,
            'Bat_Stat' : bat_Stat,
            'Bat_Type' : self.battery_conf['battery_type'],
            'Input_Current_Limit' : self.read_InputCurrentLimit()
        }
    
    def dump_register(self):
        return {
            'dump': str(self.registers)
        }
    
    def to_json_registers(self):
        """
        Returns a JSON object containing all variables with their names and values
        from instances of BQ25795_REGISTER.
        """
        registers_data = {}

        # Iterate over all attributes of the bq25792 class
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            # Check if the attribute is an instance of BQ25795_REGISTER
            if isinstance(attr, self.BQ25795_REGISTER):
                # Collect all variables and their values from the instance
                register_values = {}
                for var_name, var_value in vars(attr).items():
                    if not var_name.startswith("_"):  # Skip private/internal variables
                        register_values[var_name] = var_value
                registers_data[attr_name] = register_values
        return registers_data
####
