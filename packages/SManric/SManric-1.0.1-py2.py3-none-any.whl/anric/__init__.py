#!/usr/bin/python3

from smbus2 import SMBus
import struct
import datetime

import anric.anric_data as data
I2C_MEM = data.I2C_MEM
CHANNEL_NO = data.CHANNEL_NO
CALIB = data.CALIB

class SManric: 
    """Python class to control the ANRIC controller for Raspberry Pi.

    Args:
        stack (int): Stack level/device number.
        i2c (int): i2c bus number
    """
    def __init__(self, stack=0, i2c=1):
        if stack < 0 or stack > data.STACK_LEVEL_MAX:
            raise ValueError("Invalid stack level!")
        self._hw_address_ = data.SLAVE_OWN_ADDRESS_BASE + stack
        self._i2c_bus_no = i2c
        self.bus = SMBus(self._i2c_bus_no)
        try:
            self._card_rev_major = self.bus.read_byte_data(self._hw_address_, I2C_MEM.REVISION_HW_MAJOR_ADD)
            self._card_rev_minor = self.bus.read_byte_data(self._hw_address_, I2C_MEM.REVISION_HW_MINOR_ADD)
        except Exception:
            print("{} not detected!".format(data.CARD_NAME))
            raise

    def _get_byte(self, address):
        return self.bus.read_byte_data(self._hw_address_, address)
    def _get_word(self, address):
        return self.bus.read_word_data(self._hw_address_, address)
    def _get_i16(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 2)
        i16_value = struct.unpack("h", bytearray(buf))[0]
        return i16_value
    def _get_float(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        float_value = struct.unpack("f", bytearray(buf))[0]
        return float_value
    def _get_i32(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        i32_value = struct.unpack("i", bytearray(buf))[0]
        return i32_value
    def _get_u32(self, address):
        buf = self.bus.read_i2c_block_data(self._hw_address_, address, 4)
        u32_value = struct.unpack("I", bytearray(buf))[0]
        return u32_value
    def _get_block_data(self, address, byteno=4):
        return self.bus.read_i2c_block_data(self._hw_address_, address, byteno)
    def _set_byte(self, address, value):
        self.bus.write_byte_data(self._hw_address_, address, int(value))
    def _set_word(self, address, value):
        self.bus.write_word_data(self._hw_address_, address, int(value))
    def _set_float(self, address, value):
        ba = bytearray(struct.pack("f", value))
        self.bus.write_block_data(self._hw_address_, address, ba)
    def _set_i32(self, address, value):
        ba = bytearray(struct.pack("i", value))
        self.bus.write_block_data(self._hw_address_, address, ba)
    def _set_block(self, address, ba):
        self.bus.write_i2c_block_data(self._hw_address_, address, ba)

    @staticmethod
    def _check_channel(channel_type, channel):
        if not (0 <= channel and channel <= CHANNEL_NO[channel_type]):
            raise ValueError("Invalid {} channel number. Must be [1..{}]!".format(channel_type, CHANNEL_NO[channel_type]))
    def _calib_set(self, channel, value):
        ba = bytearray(struct.pack("f", value))
        ba.extend([channel, data.CALIBRATION_KEY])
        self._set_block(I2C_MEM.CALIB_VALUE, ba)

    def _calib_reset(self, channel):
        ba = bytearray([channel, data.CALIBRATION_KEY])
        self._set_block(I2C_MEM.CALIB_CHANNEL, ba)

    def calib_status(self):
        """Get current calibration status of device.

        Returns:
            (int) Calib status
        """
        status = self._get_byte(I2C_MEM.CALIB_STATUS)
        return status

    def get_version(self):
        """Get firmware version.

        Returns: (int) Firmware version number
        """
        version_major = self._get_byte(I2C_MEM.REVISION_MAJOR_ADD)
        version_minor = self._get_byte(I2C_MEM.REVISION_MINOR_ADD)
        version = str(version_major) + "." + str(version_minor)
        return version

    def get_relay(self, relay):
        """Get relay state.

        Args:
            relay (int): Relay number

        Returns:
            (int) Relay state
        """
        self._check_channel("relay", relay)
        val = self._get_byte(I2C_MEM.RELAYS)
        if (val & (1 << (relay - 1))) != 0:
            return 1
        return 0
    def get_all_relays(self):
        """Get all relays state as bitmask.

        Returns:
            (int) Relays state bitmask
        """
        val = self._get_byte(I2C_MEM.RELAYS)
        return val
    def set_relay(self, relay, val):
        """Set relay state.

        Args:
            relay (int): Relay number
            val: 0(OFF) or 1(ON)
        """
        self._check_channel("relay", relay)
        if val == 0:
            self._set_byte(I2C_MEM.RELAY_CLR, relay)
        elif val == 1:
            self._set_byte(I2C_MEM.RELAY_SET, relay)
        else:
            raise ValueError("Invalid relay value[0-1]")
    def set_all_relays(self, val):
        """Set all relays states as bitmask.

        Args:
            val (int): Relay bitmask
        """
        if(not (0 <= val and val <= (1 << CHANNEL_NO["relay"]) - 1)):
            raise ValueError("Invalid relay mask!")
        self._set_byte(I2C_MEM.RELAYS, 0xff & val)
#################################################################################################################
    def get_mosfet(self, mosfet):
        """Get mosfet state.

        Args:
            mosfet (int): Mosfet number

        Returns:
            (int) Mosfet state
        """
        self._check_channel("mos", mosfet)
        val = self._get_word(I2C_MEM.MOS_DIG_READ_REG1)
        if (val & (1 << (mosfet - 1))) != 0:
            return 1
        return 0

    def get_all_mosfets(self):
        """Get all mosfets state as bitmask.

        Returns:
            (int) Mosfets state bitmask
        """
        val = self._get_word(I2C_MEM.MOS_DIG_READ_REG1)
        return val

    def set_mosfet(self, mosfet, val):
        """Set mosfet state.

        Args:
            mosfet (int): Mosfet number
            val: 0(OFF) or 1(ON)
        """
        self._check_channel("mos", mosfet)
        bitmap = self.get_all_mosfets()
        if val == 0:
            bitmap &= ~(1 << (mosfet-1))
            self._set_word(I2C_MEM.MOS_DIG_REG1, bitmap)
        elif val == 1:
            bitmap |= 1 << (mosfet - 1)
            self._set_word(I2C_MEM.MOS_DIG_REG1, bitmap)
        else:
            raise ValueError("Invalid mosfet value[0-1]")

    def set_all_mosfets(self, val):
        """Set all mosfets states as bitmask.

        Args:
            val (int): Mosfet bitmask
        """
        if (not (0 <= val and val <= (1 << CHANNEL_NO["mos"]) - 1)):
            raise ValueError("Invalid mosfets mask!")
        self._set_word(I2C_MEM.MOS_DIG_REG1, val)

    def set_mosfet_pwm(self, mosfet, val):
        """Set mosfet state.

        Args:
            mosfet (int): Mosfet number
            val: 0(OFF) or 1(ON)
        """
        self._check_channel("mos", mosfet)
        if (not (0 <= val and val <= 100)):
            raise ValueError("Invalid mosfets pwm value [0..100]!")
        self._set_word(I2C_MEM.MOS_PWM1 + (mosfet - 1) * 2, val*10)

    def get_u_in(self):
        """Get 0-10V input value in volts.

        Returns:
            (float) Input value in volts
        """
       
        value = self._get_word(I2C_MEM.U_IN )
        return value / data.VOLT_TO_MILIVOLT
    # def cal_u_in(self, channel, value):
    #     """Calibrate 0-10V input channel.
    #     Calibration must be done in 2 points at min 5V apart.
    # 
    #     Args:
    #         channel (int): Channel number
    #         value (int): Voltage value
    #     """
    #     self._check_channel("u_in", channel)
    #     self._calib_set(CALIB.U_IN_CH1 + channel, value)
    def get_u_out(self):
        """Get 0-10V output channel value in volts.

        Returns:
            (float) 0-10V output value
        """
        value = self._get_word(I2C_MEM.U_OUT )
        return value / data.VOLT_TO_MILIVOLT
    def set_u_out(self, value):
        """Set 0-10V output value in volts.

        Args:
            value (float): Voltage value
        """
        value = value * data.VOLT_TO_MILIVOLT
        self._set_word(I2C_MEM.U_OUT , value)

