from packet import Packet
import time
import logging
from doorlogic import DoorLogic

class MasterController:
    class LedState:
        ON = 0
        OFF = 1
        BLINK_FAST = 2
        BLINK_SLOW = 3
        FLASH = 4

    def __init__(self, address, interface, input_queue, buttons, leds):
        self.address = address
        
        self.interface = interface
        
        self.supply_voltage = 0
        self.periodic = 10
        self.logger = logging.getLogger('logger')
        self.pressed_buttons = 0

        self.buttons = buttons
        self.leds = leds
        
        self.input_queue = input_queue

    def update(self, message):
    	if len(message) != 16:
            self.logger.warning("The received message is not 16 bytes long")
    	    return

        self.logger.debug("Decoded message: %s"%str(list(message)))
        
        p = Packet.fromMessage(message)
        if p.cmd==83:
            self.supply_voltage = ord(p.data[3])*0.1
            
            pressed_buttons = ord(p.data[0])
            self.logger.debug('master: pressed_buttons = %d', pressed_buttons)
            for pin in self.buttons:
                if pressed_buttons & pin and not self.pressed_buttons & pin:
                    self.pressed_buttons |= pin
                    self.input_queue.put({'origin_name': 'master',
                        'origin_type': DoorLogic.Origin.CONTROL_PANNEL,
                        'input_name': self.buttons[pin],
                        'input_type': DoorLogic.Input.BUTTON,
                        'input_value': True})
                elif not pressed_buttons & pin and self.pressed_buttons & pin:
                    self.input_queue.put({'origin_name': 'master',
                        'origin_type': DoorLogic.Origin.CONTROL_PANNEL,
                        'input_name': self.buttons[pin],
                        'input_type': DoorLogic.Input.BUTTON,
                        'input_value': False})
                    self.pressed_buttons &= ~pin

            self.logger.info('Master state: %s'%self.get_state())

    def get_state(self):
        state = ''
        state = state + ' Voltage=%.1f V'%self.supply_voltage
        state = state.strip()
        return state

    def tick(self):
        self.periodic-=1
        self.logger.debug('master: tick')
        if self.periodic == 0:
            self.periodic = 2
            self._send_command(ord('S'), '')
        
    def set_led(self, led_name, state):
        led = self.leds[led_name]
        self._send_command(ord('L'), '%c%c'%(led, state))
        
    def _send_command(self, command, data):
        p = Packet(seq=0, cmd=command, data=data, seq_sync=False)
        msg = p.toMessage()

        self.logger.debug('Msg to mastercontroller: %s'%list(msg))
        self.interface.writeMessage(self.address, msg)

