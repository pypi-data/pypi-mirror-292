from time import sleep

import pyvisa
import numpy as np
from statemachine import State, StateMachine
from statemachine.exceptions import TransitionNotAllowed

from automatic_spectral_acquisition.config import ConfigHandler
from automatic_spectral_acquisition.helper import error_message
from automatic_spectral_acquisition.constants import *


class OscilloscopeStateMachine(StateMachine):
    """State machine for the oscilloscope."""
    # Define states
    start = State('Start', initial=True)
    connected = State('Connected')
    requested = State('Requested') # Requested a measurement
    completed = State('Completed')
    disconnected = State('Disconnected')

    # Define transitions
    connect = start.to(connected) | disconnected.to(connected)
    request = connected.to(requested) | completed.to(requested)  
    complete = requested.to(completed)
    disconnect = completed.to(disconnected)

    # Define transition actions
    def on_connect(self, *args, **kwargs): # from previous code
        # Check if config_handler is passed
        config_handler:ConfigHandler = kwargs.get('config_handler')
        if not isinstance(config_handler, ConfigHandler):
            error_message('TypeError', 'ConfigHandler object not passed.')

        # Check if oscilloscope port is set
        oscilloscope_port = config_handler.config.oscilloscope_port
        if oscilloscope_port is None:
            error_message('ValueError', 'Oscilloscope port not set.')
            
        # Check if oscilloscope_instance is passed
        oscilloscope_instance:Oscilloscope = kwargs.get('oscilloscope_instance')
        if not isinstance(oscilloscope_instance, Oscilloscope):
            error_message('TypeError', 'Oscilloscope object not passed.')
            
        # Connect to oscilloscope
        try:
            oscilloscope_instance.oscilloscope_connection = pyvisa.ResourceManager().open_resource(oscilloscope_port)
        except pyvisa.errors.VisaIOError as e:
            error_message('VisaIOError', e)
            
        # Configure oscilloscope
        oscilloscope_instance.oscilloscope_connection.timeout = OSCILLOSCOPE_TIMEOUT
        oscilloscope_instance.oscilloscope_connection.encoding = 'latin_1'
        oscilloscope_instance.oscilloscope_connection.read_termination = '\n'
        oscilloscope_instance.oscilloscope_connection.write_termination = None
        
        oscilloscope_instance.oscilloscope_connection.write('*cls') # clear ESR
        oscilloscope_instance.oscilloscope_connection.write('HEADer OFF')
        oscilloscope_instance.oscilloscope_connection.write('VERBose OFF')
        oscilloscope_instance.oscilloscope_connection.write('ACQUIRE:STOPAFTER SEQUENCE') # single measurement
        oscilloscope_instance.oscilloscope_connection.write('TRIGger:A:MODe AUTO') # set trigger to auto
        oscilloscope_instance.oscilloscope_connection.write(f'HORizontal:SCAle {OSCILLOSCOPE_HORIZONTAL_SCALE}') # set time scale
        oscilloscope_instance.oscilloscope_connection.write(f'CH1:SCAle {OSCILLOSCOPE_VERTICAL_SCALE}') # set vertical scale
        oscilloscope_instance.oscilloscope_connection.write(f'CH1:OFFSet {OSCILLOSCOPE_OFFSET}') # set offset
        oscilloscope_instance.oscilloscope_connection.write('CH1:POSition 0') # set position to 0
        oscilloscope_instance.oscilloscope_connection.write('DATa:SOUrce CH1')
        oscilloscope_instance.oscilloscope_connection.write('DATa:RESOlution FULL')
        oscilloscope_instance.oscilloscope_connection.write('DATa:ENCdg RIBinary')
        oscilloscope_instance.oscilloscope_connection.write('DATa:STARt 1')
        oscilloscope_instance.oscilloscope_connection.write('DATa:STOP 10000')
        oscilloscope_instance.oscilloscope_connection.write('WFMOutpre:COMPosition SINGULAR_YT')
        oscilloscope_instance.oscilloscope_connection.write('DATa:WIDth 1')
    
    
    def on_request(self, *args, **kwargs): # from previous code
        # Check if oscilloscope_instance is passed
        oscilloscope_instance:Oscilloscope = kwargs.get('oscilloscope_instance')
        if not isinstance(oscilloscope_instance, Oscilloscope):
            error_message('TypeError', 'Oscilloscope object not passed.')
        
        while True:
            sleep(0.5)
            wave = oscilloscope_instance._get_curve()
            mean, std = oscilloscope_instance._get_measurements(wave, *oscilloscope_instance._get_settings())
            vertical_scale = float(oscilloscope_instance.oscilloscope_connection.query('CH1:SCAle?'))

            if np.any(np.abs(wave)>4*vertical_scale) and oscilloscope_instance.v_scale_index < len(OSCILLOSCOPE_SCALES)-1:
                oscilloscope_instance.v_scale_index += 1
                vertical_scale = OSCILLOSCOPE_SCALES[oscilloscope_instance.v_scale_index]
                oscilloscope_instance.oscilloscope_connection.write(f'CH1:SCAle {vertical_scale}')
                continue

            if np.all(np.abs(wave)<0.5*vertical_scale) and oscilloscope_instance.v_scale_index > 0:
                oscilloscope_instance.v_scale_index -= 1
                vertical_scale = OSCILLOSCOPE_SCALES[oscilloscope_instance.v_scale_index]
                oscilloscope_instance.oscilloscope_connection.write(f'CH1:SCAle {vertical_scale}')
                continue
            
            return mean, std
    
    
    # def on_complete(self, *args, **kwargs): # not needed for now
    #     pass
    
    
    def on_disconnect(self, *args, **kwargs):
        # Check if oscilloscope_instance is passed
        oscilloscope_instance:Oscilloscope = kwargs.get('oscilloscope_instance')
        if not isinstance(oscilloscope_instance, Oscilloscope):
            error_message('TypeError', 'Oscilloscope object not passed.')
            
        # Check if serial connection is set
        if oscilloscope_instance.oscilloscope_connection is None:
            error_message('ValueError', 'Cannot disconnect oscilloscope without a connection.')
            
        oscilloscope_instance.oscilloscope_connection.close()
        oscilloscope_instance.oscilloscope_connection = None


class Oscilloscope:
    """Class to handle the oscilloscope."""
    def __init__(self, config_handler:ConfigHandler) -> None:
        self.config_handler:ConfigHandler = config_handler
        self.state_machine:OscilloscopeStateMachine = OscilloscopeStateMachine()
        self.oscilloscope_connection:pyvisa.Resource = None
        self.v_scale_index = 0


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
    
    
    def _get_curve(self) -> np.ndarray:
        """Get the curve from the oscilloscope. Internal method."""
        self.oscilloscope_connection.write('ACQUIRE:STATE RUN')
        sleep(12*OSCILLOSCOPE_HORIZONTAL_SCALE)
        wave = self.oscilloscope_connection.query_binary_values('curve?', datatype='b', container=np.array)
        return np.array(wave, dtype='double') 


    def _get_settings(self) -> tuple[float, float, float]:
        """Get ymult, yoff, and yzero from the oscilloscope. Internal method."""
        ymult = float(self.oscilloscope_connection.query('WFMOutpre:YMUlt?'))
        yoff  = float(self.oscilloscope_connection.query('WFMOutpre:YOFf?'))
        yzero = float(self.oscilloscope_connection.query('WFMOutpre:YZEro?'))
        return ymult, yoff, yzero
      
            
    def _get_measurements(self, 
                          wave: np.ndarray, 
                          ymult: float, 
                          yoff: float, 
                          yzero: float) -> tuple[float, float]:
        """Calculate the average and standard deviation of the waveform.

        Args:
            wave (np.ndarray): The waveform data.
            ymult (float): The y-axis multiplier.
            yoff (float): The y-axis offset.
            yzero (float): The y-axis zero.

        Returns:
            Tuple[float, float]: The average and standard deviation of the waveform.
        """
        wave = (wave-yoff)*ymult+yzero
        return np.average(wave), np.std(wave)
    
    
    def connect(self):
        """Connect to the oscilloscope."""
        return self._send('connect', config_handler=self.config_handler, oscilloscope_instance=self)
    
    
    def get_measurement(self):
        """Get a measurement from the oscilloscope. Returns the mean and standard deviation."""
        val = self._send('request', oscilloscope_instance=self)
        self._send('complete')
        return val
    
    
    def disconnect(self):
        """Disconnect from the oscilloscope."""
        return self._send('disconnect', oscilloscope_instance=self)
    
