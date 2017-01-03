import minimalmodbus
import time
import datetime
import logging
import sqlite3 as sql

import bledb


class VeritekVips84(minimalmodbus.Instrument):
    """Instrument class for Veritek VIPS84.

    Communicates via Modbus RTU protocol (via RS232 or RS485), using the *MinimalModbus* Python module.
    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247
    """

    def __init__(self, portname, slaveaddress):
        minimalmodbus.BAUDRATE = 9600
        minimalmodbus.PARITY = 'E'
        minimalmodbus.TIMEOUT = 1
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress, mode='rtu')
	self.macid = "nrgmeter0001"

    ## Process value

    def get_frequency(self):
        """in Hz"""
        return self.read_float(41, functioncode=4, numberOfRegisters=2)

    def get_voltage_r_n(self):
        """in V"""
        return self.read_float(59, functioncode=4, numberOfRegisters=2)

    def get_current_r(self):
        """in A"""
        return self.read_float(63, functioncode=4, numberOfRegisters=2)

    def get_pf_r(self):
        """"""
        return self.read_float(65, functioncode=4, numberOfRegisters=2)

    def get_active_power_r(self):
        #in Watt
        return self.read_float(67, functioncode=4, numberOfRegisters=2)

    def get_reactive_power_r(self):
        #in VAR
        return self.read_float(69, functioncode=4, numberOfRegisters=2)

    def get_apparent_power_r(self):
        #in VA
        return self.read_float(71, functioncode=4, numberOfRegisters=2)

    def get_import_active_energy(self):
        #in uWh
        value = self.read_registers(9, 4, functioncode=4)
        return (value[0] << 48 | value[1] << 32 | value[2] << 16 | value[3])

    def get_import_apparent_energy(self):
        #in uVAh
        value = self.read_registers(21, 4, functioncode=4)
        return (value[0] << 48 | value[1] << 32 | value[2] << 16 | value[3])

    def get_export_active_energy(self):
        #in uWh
        value = self.read_registers(25, 4, functioncode=4)
        return (value[0] << 48 | value[1] << 32 | value[2] << 16 | value[3])

    def get_export_apparent_energy(self):
        #in uVAh
        value = self.read_registers(37, 4, functioncode=4)
        return (value[0] << 48 | value[1] << 32 | value[2] << 16 | value[3])

    def getBatt(self):
	return None

    def pushToDB(self):
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	nrgData  = [self.macid, round(self.get_voltage_r_n(),2), round(self.get_current_r(),3), \
				round(self.get_pf_r(),2), round(self.get_apparent_power_r(),2),  \
				round(self.get_import_active_energy()/1000000000.0,9), nodeTS, self.getBatt()]
	print nrgData
		
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO NrgData (NdId, \
			VoltRN, CurrR, PfR, AppPwrR, ActNrg, NdTs, NdBat, upFlag) \
			values (?,?,?,?,?,?,?,?,0);""", nrgData)

			logging.info('Energy Meter  data:%s', nrgData)
        	return True

	except Exception as ex:
		logging.error("Exception pushing energy data to DB: %s",ex)
		return False
    	
   
########################
## Testing the module ##
########################

if __name__ == '__main__':

    minimalmodbus._print_out('TESTING Veritek VIPS 84 MODULE')

    #nrgMeter = VeritekVips84('COM14', 1)			#for windows
    nrgMeter = VeritekVips84('/dev/ttyUSB0', 1)    #for linux
    nrgMeter.debug = False

    while True:
        try:
            value = nrgMeter.get_frequency()
            minimalmodbus._print_out('Frequency : {0}'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_voltage_r_n()
            minimalmodbus._print_out('Voltage \'r-n\' : {0} (V)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_current_r()
            minimalmodbus._print_out('Current \'r\' : {0} (A)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_pf_r()
            value *= 100
            minimalmodbus._print_out('Power Factor \'r\' : {0} %'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_active_power_r()
            minimalmodbus._print_out('Active Power \'r\' : {0} (W)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_reactive_power_r()
            minimalmodbus._print_out('Reactive Power \'r\' : {0} (VAR)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_apparent_power_r()
            minimalmodbus._print_out('Apparent Power \'r\' : {0} (VA)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_import_active_energy()
            value /= (float)(1000000000)
            minimalmodbus._print_out('Import Active Energy : {0} (KWh)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_import_apparent_energy()
            value /= (float)(1000000000)
            minimalmodbus._print_out('Import Apparent Energy : {0} (KVAh)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_export_active_energy()
            value /= (float)(1000000000)
            minimalmodbus._print_out('Export Active Energy : {0} (KWh)'.format(value))
        except Exception as e:
            print(str(e))

        try:
            value = nrgMeter.get_export_apparent_energy()
            value /= (float)(1000000000)
            minimalmodbus._print_out('Export Apparent Energy : {0} (KVAh)'.format(value))
        except Exception as e:
            print(str(e))

        time.sleep(2)

    minimalmodbus._print_out('DONE!')

pass
