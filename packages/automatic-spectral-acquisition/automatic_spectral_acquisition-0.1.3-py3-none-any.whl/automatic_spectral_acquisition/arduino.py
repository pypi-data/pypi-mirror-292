import serial
from time import sleep

from statemachine import State, StateMachine
from statemachine.exceptions import TransitionNotAllowed

from automatic_spectral_acquisition.config import ConfigHandler
from automatic_spectral_acquisition.helper import error_message
from automatic_spectral_acquisition.constants import *


class CommandError(Exception):
    """Raised when an invalid command is received from the arduino."""
    pass


class ArduinoStateMachine(StateMachine):
    """State machine for the Arduino connection."""
    # Define states
    start = State('Start', initial=True)
    connected = State('Connected') 
    requested = State('Requested') # Requested a change in position
    completed = State('Completed') # Received confirmation by the arduino
    disconnected = State('Disconnected')

    # Define transitions
    connect = start.to(connected) | disconnected.to(connected)
    request = connected.to(requested) | completed.to(requested)
    wait = requested.to.itself()
    complete = requested.to(completed)
    disconnect = completed.to(disconnected)
    
    # Define transition actions
    def on_connect(self, *args, **kwargs):
        if IGNORE_CONNECTIONS:
            return
        
        # Check if config_handler is passed
        config_handler:ConfigHandler = kwargs.get('config_handler')
        if not isinstance(config_handler, ConfigHandler):
            error_message('TypeError', 'ConfigHandler object not passed.')

        # Check if arduino port is set
        arduino_port = config_handler.config.arduino_port
        if arduino_port is None:
            error_message('ValueError', 'Arduino port not set.')
            
        # Check if arduino_instance is passed
        arduino_instance:Arduino = kwargs.get('arduino_instance')
        if not isinstance(arduino_instance, Arduino):
            error_message('TypeError', 'Arduino object not passed.')
        
        # Connect to arduino
        try:
            arduino_instance.arduino_connection = serial.Serial(port=arduino_port, 
                                                                baudrate=ARDUINO_BAUDRATE, 
                                                                timeout=ARDUINO_TIMEOUT)
            sleep(2)
            arduino_instance.arduino_connection.reset_input_buffer()
        except serial.SerialException:
            error_message('SerialException', f'Could not connect to arduino on port {arduino_port}.')
        
        
    def on_request(self, *args, **kwargs):
        if IGNORE_REQUESTS:
            return
        
        # Check if position is passed
        position:float = kwargs.get('position')
        if not isinstance(position, float):
            error_message('TypeError', 'Position not passed or not a float.')
        
        # Check if arduino_instance is passed
        arduino_instance:Arduino = kwargs.get('arduino_instance')
        if not isinstance(arduino_instance, Arduino):
            error_message('TypeError', 'Arduino object not passed.')

        arduino_instance.arduino_connection.write(bytes(f'{GOTO} {position}~', 'UTF-8'))
        
        
    def on_wait(self, *args, **kwargs):
        # Check if arduino_instance is passed
        arduino_instance:Arduino = kwargs.get('arduino_instance')
        if not isinstance(arduino_instance, Arduino):
            error_message('TypeError', 'Arduino object not passed.')
          
        while True:
            if arduino_instance.arduino_connection.in_waiting: # check if there is data to read
                received_bytes = arduino_instance.arduino_connection.read_until(expected=b'~')
                try:
                    command = received_bytes.decode('UTF-8')[:-1]
                except UnicodeDecodeError:
                    error_message('UnicodeDecodeError', f'Could not decode command from arduino. Received: {received_bytes}')
                
                if command == DONE:
                    return
                elif command == INVALID:
                    error_message('CommandError', 'Arduino received an invalid command.')
                elif command == RUNNING:
                    error_message('CommandError', 'Tried to send command while motor was already moving.')
                elif command == STOP:
                    error_message('CommandError', 'Stop button was pressed.')
                else:
                    error_message('CommandError', f'Unknown command received: {command}')

    # def on_complete(self, *args, **kwargs): # Not needed for now
    #     pass
        
        
    def on_disconnect(self, *args, **kwargs):
        if IGNORE_CONNECTIONS:
            return
        
        # Check if arduino_instance is passed
        arduino_instance:Arduino = kwargs.get('arduino_instance')
        if not isinstance(arduino_instance, Arduino):
            error_message('TypeError', 'Arduino object not passed.')

        # Check if serial connection is set
        if arduino_instance.arduino_connection is None:
            error_message('ValueError', 'Cannot disconnect Arduino without a connection.')
        
        arduino_instance.arduino_connection.close()
        arduino_instance.arduino_connection = None
        

class Arduino:
    """Class for controlling the Arduino connection."""
    def __init__(self, config_handler:ConfigHandler) -> None:
        self.config_handler:ConfigHandler = config_handler
        self.state_machine:ArduinoStateMachine = ArduinoStateMachine()
        self.arduino_connection:serial.Serial = None


    def _send(self, transition:str, *args, **kwargs) -> None:
        """Send a transition to the state machine. Internal method.

        Args:
            transition (str): The name of the transition to send.

        Returns:
            Any: The result of the transition.
        """
        try:
            return self.state_machine.send(transition, *args, **kwargs)
        except TransitionNotAllowed as e:
            error_message('TransitionNotAllowed', e)
          
            
    def connect(self) -> None:
        """Connect to the Arduino."""
        self._send('connect', config_handler=self.config_handler, arduino_instance=self)
        
        
    def change_wavelength(self, wavelength:float) -> None:
        """Change the wavelength of the monochromator.

        Args:
            wavelength (float): The desired wavelength.
        """
        self._send('request', position=self.config_handler.position(wavelength),
                   arduino_instance=self)
        self._send('wait', arduino_instance=self)
        self._send('complete')
    
    
    def change_position(self, position:float) -> None:
        """Change the position of the monochromator.

        Args:
            position (float): The desired position.
        """
        self._send('request', position=position, arduino_instance=self)
        self._send('wait', arduino_instance=self)
        self._send('complete')
    
    
    def disconnect(self) -> None:
        """Disconnect from the Arduino."""
        self._send('disconnect', arduino_instance=self)