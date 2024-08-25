from dataclasses import dataclass
import pickle
import os

import pyvisa
import serial.tools.list_ports
import numpy as np

from automatic_spectral_acquisition.calibration import Calibration
from automatic_spectral_acquisition.constants import * 

@dataclass
class Config:
    """Dataclass for the configuration."""
    arduino_port:str|None = None
    oscilloscope_port:str|None = None
    m:float|None = None
    c:float|None = None
  
    
class ConfigHandler:
    """Class to handle the configuration."""
    def __init__(self,
                 arduino_port:str|None=None,
                 oscilloscope_port:str|None=None,
                 m:float|None=None,
                 c:float|None=None,
                 wavelengths:list[float]=None,
                 positions:list[float]=None) -> None:
        
        self.config = Config(arduino_port, oscilloscope_port, m, c)
        self.calibration = Calibration(wavelengths, positions)


    def __str__(self) -> str:
        """Return the configuration as a string."""
        return f'Arduino port: {self.config.arduino_port}\nOscilloscope port: {self.config.oscilloscope_port}\nm: {self.config.m}\nc: {self.config.c}'
    
    
    def save_config(self) -> None:
        """Save the configuration to a file."""
        with open(f'{TEMP_DIRECTORY}/{CONFIG_FILE}', 'wb') as f:
            pickle.dump(self.config, f)
    
    
    def load_config(self) -> None:
        """Load the configuration from a file."""
        with open(f'{TEMP_DIRECTORY}/{CONFIG_FILE}', 'rb') as f:
            self.config = pickle.load(f)
            self.calibration = Calibration(m=self.config.m, c=self.config.c)
        
        
    def calibrate(self, wavelengths:np.ndarray, positions:np.ndarray) -> None:
        """Calibrate the monochromator."""
        self.calibration.calibrate(wavelengths, positions)
        self.config.m = self.calibration.m
        self.config.c = self.calibration.c
        
        
    def position(self, wavelength:float) -> float:
        """Calculate the position for a given wavelength."""
        return self.calibration.position(wavelength)
    
    
    def list_serial_ports(self) -> None:
        """List the serial available ports."""
        return sorted(serial.tools.list_ports.comports())
         
         
    def list_pyvisa_instruments(self) -> None:
        """List the pyvisa available instruments."""
        return pyvisa.ResourceManager().list_resources()
    
    
    def check_config_exists(self) -> bool:
        """Check if the configuration file exists."""
        return os.path.exists(f'{TEMP_DIRECTORY}/{CONFIG_FILE}')
    