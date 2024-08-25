import logging 
import os
import signal

from rich import print
from rich.progress import track
import pyinputplus as pyin

from automatic_spectral_acquisition.arduino import Arduino
from automatic_spectral_acquisition.oscilloscope import Oscilloscope
from automatic_spectral_acquisition.file_manager import FileManager
from automatic_spectral_acquisition.config import ConfigHandler
from automatic_spectral_acquisition.constants import *
from automatic_spectral_acquisition.helper import error_message, info_message
from automatic_spectral_acquisition.extras import plot_spectrum


class Core:
    """Class to handle the core functionality of the program."""
    def __init__(self,
                 output_directory:str=OUTPUT_DIRECTORY, 
                 output_file:str=OUTPUT_FILE,
                 temp_directory:str=TEMP_DIRECTORY,
                 log_file:str=LOG_FILE,
                 output_header:list[str]=DEFAULT_HEADER,
                 arduino_port:str|None=None,
                 oscilloscope_port:str|None=None,
                 m:float|None=None,
                 c:float|None=None,
                 wavelengths:list[float]=None,
                 positions:list[float]=None) -> None:
        
        if DEBUG or IGNORE_CONNECTIONS or IGNORE_REQUESTS:
            info_message('Debug mode is enabled.', 'Information')
            
        # Catch interrupt signal to make sure the program ends correctly
        signal.signal(signal.SIGINT, self.interrupt_handler)
        
        # Create file_manager instance
        self.file_manager = FileManager(output_directory, output_file, temp_directory, log_file, output_header)
        
        # Setup logging
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=self.file_manager.log_file_directory,
                            filemode='w')
        
        # create the rest of the class instances
        self.config_handler = ConfigHandler(arduino_port, oscilloscope_port, m, c, wavelengths, positions)
        self.arduino = Arduino(self.config_handler)
        self.oscilloscope = Oscilloscope(self.config_handler)
    
    
    @staticmethod
    def check_parameters_spectrum(start: float, end: float, step: float, number_of_measurements: int) -> None:
        """Check if the parameters for spectral acquisition are valid.

        Args:
            start (float): The starting wavelength.
            end (float): The ending wavelength.
            step (float): The step size between measurements.
            number_of_measurements (int): The number of measurements to take for each wavelength.

        Raises:
            TypeError: If any of the parameters are not of the expected type.
            ValueError: If any of the parameters are invalid.
        """
        # check type of parameters
        if not isinstance(start, (int, float)):
            error_message('TypeError', 'Start wavelength must be a number.')
        if not isinstance(end, (int, float)):
            error_message('TypeError', 'End wavelength must be a number.')
        if not isinstance(step, (int, float)):
            error_message('TypeError', 'Step must be a number.')
        if not isinstance(number_of_measurements, int):
            error_message('TypeError', 'Number of measurements must be an integer.')
        
        # check if the wavelength parameters are valid
        if start < WAVELENGTH_MIN:
            error_message('ValueError', f'Start wavelength must be greater than {WAVELENGTH_MIN}.')
        if end > WAVELENGTH_MAX:
            error_message('ValueError', f'End wavelength must be less than {WAVELENGTH_MAX}.')
        if start >= end:
            error_message('ValueError', 'Start wavelength must be less than end wavelength.')
        if step <= 0:
            error_message('ValueError', 'Step must be greater than 0.')
        if (end - start) < step:
            error_message('ValueError', 'Step must be less than the difference between start and end wavelength.')
        
        # check if the number of measurements is valid
        if number_of_measurements <= 0:
            error_message('ValueError', 'Number of measurements must be greater than 0.')


    @staticmethod
    def check_parameters_single(wavelength: float, number_of_measurements: int) -> None:
        """Check if the parameters for a single measurement are valid.

        Args:
            wavelength (float): The wavelength to measure.
            number_of_measurements (int): The number of measurements to take.

        Raises:
            TypeError: If any of the parameters are not of the expected type.
            ValueError: If any of the parameters are invalid.
        """
        # check type of parameters
        if not isinstance(wavelength, (int, float)):
            error_message('TypeError', 'Wavelength must be a number.')
        if not isinstance(number_of_measurements, int):
            error_message('TypeError', 'Number of measurements must be an integer.')
        
        # check if the wavelength is valid
        if wavelength < WAVELENGTH_MIN:
            error_message('ValueError', f'Wavelength must be greater than {WAVELENGTH_MIN}.')
        if wavelength > WAVELENGTH_MAX:
            error_message('ValueError', f'Wavelength must be less than {WAVELENGTH_MAX}.')
        
        # check if the number of measurements is valid
        if number_of_measurements <= 0:
            error_message('ValueError', 'Number of measurements must be greater than 0.')


    @staticmethod
    def create_wavelengths(start: float, end: float, step: float) -> None:
        """Create a list of wavelengths.

        Args:
            start (float): The starting wavelength.
            end (float): The ending wavelength.
            step (float): The step size between wavelengths.

        Raises:
            ValueError: If the step size is smaller than 0.

        Returns:
            list: A list of wavelengths.
        """
        
        if step <= 0:
            error_message('ValueError', 'Step must be greater than 0.')
        
        wavelengths = []
        current_wavelength = start
        while current_wavelength <= end:
            wavelengths.append(current_wavelength)
            current_wavelength += step
        return wavelengths


    def interrupt_handler(self, signum, frame) -> None:
        """Interrupt handler to stop the program safely."""
        info_message('Interrupt signal received. Exiting...', 'Exit')
        self.finalize()
        exit()
    
    
    def perform_measurement(self,
                            wavelength:float, 
                            number_of_measurements:int=DEFAULT_NUMBER_OF_MEASUREMENTS) -> None:
        """Perform a measurement at a specific wavelength.

        Args:
            wavelength (float): The wavelength to measure.
            number_of_measurements (int, optional): The number of measurements to take. Defaults to DEFAULT_NUMBER_OF_MEASUREMENTS.
        """
        logging.info(f'Performing measurement at wavelength {wavelength:.2f}nm {number_of_measurements} times.')
        
        if IGNORE_REQUESTS:
            from numpy import sin
            measurement_avg = sin(wavelength*0.0628)
            error_avg = 0.1
            self.file_manager.add_buffer([wavelength, measurement_avg, error_avg])
            return
        
        self.arduino.change_wavelength(wavelength)
        
        measurements = []
        errors = []
        
        for _ in range(number_of_measurements):
            measurement, error = self.oscilloscope.get_measurement()
            measurements.append(measurement)
            errors.append(error)
        
        if len(measurements)==0 or len(errors)==0:
            info_message('No measurements were taken.', 'Information')
            measurement_avg = None
            error_avg = None
        else:
            measurement_avg = sum(measurements) / number_of_measurements
            error_avg = sum(errors) / number_of_measurements
        
        self.file_manager.add_buffer([wavelength, measurement_avg, error_avg])
    
    
    def connect_arduino(self) -> None:
        """Connect to the Arduino."""
        self.arduino = Arduino(self.config_handler)
        self.arduino.connect()
     
         
    def connect_oscilloscope(self) -> None:
        """Connect to the oscilloscope."""
        self.oscilloscope = Oscilloscope(self.config_handler)
        self.oscilloscope.connect()
       
        
    def get_arduino_port(self) -> str:
        """Get the Arduino port from the user."""
        ports = self.config_handler.list_serial_ports()
        
        if len(ports) == 0:
            error_message('Error', 'No port was detected.')
            
        arduino_port = pyin.inputMenu(prompt='Select the Arduino port:\n', 
                                      choices=[i.description for i in ports]+['Exit',], 
                                      numbered=True)
        
        if arduino_port == 'Exit':
            info_message('Configuration not saved.', 'Exit')
            exit()
        
        for i in ports:
            if arduino_port == i.description:
                arduino_port = i.name
                break
        
        if arduino_port is None:
            error_message('Error', 'Port not valid.')
            
        return arduino_port
     
     
    def get_oscilloscope_port(self) -> str:
        """Get the oscilloscope port from the user."""
        instruments = self.config_handler.list_pyvisa_instruments()
        if len(instruments) == 0:
            error_message('Error', 'No instrument was detected.')

        oscilloscope_port = pyin.inputMenu(prompt='Select the oscilloscope port:\n', 
                                           choices=instruments+('Exit',), 
                                           numbered=True)
        
        if oscilloscope_port == 'Exit':
            info_message('Configuration not saved.', 'Exit')
            exit()
            
        return oscilloscope_port


    def record_single(self, 
                      wavelength:float,
                      number_of_measurements:int=DEFAULT_NUMBER_OF_MEASUREMENTS) -> None:
        """Perform a single measurement.

        Args:
            wavelength (float): The wavelength to measure.
            number_of_measurements (int, optional): The number of measurements to take. Defaults to DEFAULT_NUMBER_OF_MEASUREMENTS.
        """
        self.perform_measurement(wavelength, number_of_measurements)
        self.file_manager.save_buffer()
    
    
    def record_spectrum(self, 
                        start:float, 
                        end:float, 
                        step:float, 
                        number_of_measurements:int=DEFAULT_NUMBER_OF_MEASUREMENTS) -> None:
        """Perform spectral acquisition.

        Args:
            start (float): The starting wavelength.
            end (float): The ending wavelength.
            step (float): The step size between measurements.
            number_of_measurements (int, optional): The number of measurements to take for each wavelength. Defaults to DEFAULT_NUMBER_OF_MEASUREMENTS.
        """
        wavelengths = self.create_wavelengths(start, end, step)
        for wl in track(wavelengths, description='Performing measurements...'):
            self.perform_measurement(wl, number_of_measurements)
        self.file_manager.save_buffer()
        
        
    def initialize(self) -> None:
        """Load the configuration and connect to the Arduino and oscilloscope."""

        if self.config_handler.check_config_exists():
            self.config_handler.load_config()
        else:
            self.cli_config_create()
        
        if IGNORE_CONNECTIONS:
            info_message('Ignoring connections...', 'Information')
            return
        
        if self.config_handler.config.m is None or \
           self.config_handler.config.c is None:
            self.cli_config_calibrate()
        
        self.connect_arduino()
        self.connect_oscilloscope()
        
        
    def finalize(self) -> None: 
        """Disconnect from the Arduino and oscilloscope. Changes the position of the monochromator to the default position."""
        if IGNORE_CONNECTIONS:
            return
        self.arduino.disconnect()
        self.oscilloscope.disconnect()
        self.arduino.change_position(DEFAULT_POSITION)
        
########################### cli commands ###########################
    
    def cli_record_single(self, 
                      wavelength:float,
                      number_of_measurements:int=DEFAULT_NUMBER_OF_MEASUREMENTS,
                      file:str=OUTPUT_FILE,
                      print_:bool=False) -> None:
        """Perform a single measurement. Used by the CLI.

        Args:
            wavelength (float): The wavelength to measure.
            number_of_measurements (int, optional): The number of measurements to take. Defaults to DEFAULT_NUMBER_OF_MEASUREMENTS.
            file (str, optional): The name of the output file. Defaults to OUTPUT_FILE.
            print_ (bool, optional): Whether to print the measurement. Defaults to False.
        """
        self.check_parameters_single(wavelength, number_of_measurements)
        self.initialize()
        self.file_manager.change_output_file_directory(file)
        self.record_single(wavelength, number_of_measurements)
        self.finalize()
        if print_:
            print(f'[white]V(λ=[repr.number]{self.file_manager.buffer[0][0]:.2f}[/repr.number]nm) = '
                  f'([repr.number]{self.file_manager.buffer[0][1]:.2f}[/repr.number] ± '
                  f'[repr.number]{self.file_manager.buffer[0][2]:.2f}[/repr.number])V')
       
        
    def cli_record_spectrum(self, 
                            start:float, 
                            end:float, 
                            step:float, 
                            number_of_measurements:int=DEFAULT_NUMBER_OF_MEASUREMENTS,
                            file:str=OUTPUT_FILE,
                            plot:bool=False) -> None:
        """Perform spectral acquisition. Used by the CLI.

        Args:
            start (float): The starting wavelength.
            end (float): The ending wavelength.
            step (float): The step size between measurements.
            number_of_measurements (int, optional): The number of measurements to take for each wavelength. Defaults to DEFAULT_NUMBER_OF_MEASUREMENTS.
            file (str, optional): The name of the output file. Defaults to OUTPUT_FILE.
            plot (bool, optional): Whether to plot the spectrum. Defaults to False.
        """
        self.check_parameters_spectrum(start, end, step, number_of_measurements)
        self.initialize()
        self.file_manager.change_output_file_directory(file)
        self.record_spectrum(start, end, step, number_of_measurements)
        self.finalize()
        if plot:
            plot_spectrum(file)
    
    
    def cli_config_create(self) -> None:
        """Creates a configuration file. Used by the CLI."""
        # get arduino port
        if IGNORE_CONNECTIONS:
            arduino_port = pyin.inputMenu(prompt='Select the Arduino port:\n', 
                                          choices=['Fake port Arduino', 'Exit'], 
                                          numbered=True)
            if arduino_port == 'Exit':
                info_message('Configuration not saved.', 'Exit')
                exit()
        else:
            arduino_port = self.get_arduino_port()
            
        # get oscilloscope port
        if IGNORE_CONNECTIONS:
            oscilloscope_port = pyin.inputMenu(prompt='Select the oscilloscope port:\n', 
                                          choices=['Fake port oscilloscope', 'Exit'], 
                                          numbered=True)
            if oscilloscope_port == 'Exit':
                info_message('Configuration not saved.', 'Exit')
                exit()
        else:
            oscilloscope_port = self.get_oscilloscope_port()

        # create config handler        
        self.config_handler = ConfigHandler(arduino_port=arduino_port,
                                            oscilloscope_port=oscilloscope_port)
        
        # save config handler
        self.config_handler.save_config()
        
        # calibrate
        self.cli_config_calibrate()
          
           
    def cli_config_delete(self) -> None:
        """Deletes the configuration file. Used by the CLI."""
        if not self.config_handler.check_config_exists():
            info_message('No configuration file found.', 'Information')
            return
        os.remove(f'{TEMP_DIRECTORY}/{CONFIG_FILE}')
        info_message('Configuration file deleted.', 'Information')       


    def cli_config_show(self) -> None:
        """Shows the configuration. Used by the CLI."""
        if not self.config_handler.check_config_exists():
            info_message('No configuration file found.', 'Information')
            return
        self.config_handler.load_config()
        print(self.config_handler)
        
        
    def cli_config_calibrate(self) -> None:
        """Calibrates the monochromator and updades the configuration file. Used by the CLI."""        
        if self.config_handler.check_config_exists():
            self.config_handler.load_config()
        else:
            error_message('Error', 'No configuration file found. Use "spectral config create".')

        if IGNORE_REQUESTS:
            info_message('Faking motor calibration...', 'Information')
            self.config_handler.calibrate([350, 500, 650, 800, 950], CALIBRATION_POSITIONS)
            self.config_handler.save_config()
            info_message('Finished.', 'Information')
            return
        
        self.connect_arduino() # Connect to arduino
        
        info_message('Starting motor calibration...', 'Information')
        wavelengths = [] 
        for position in CALIBRATION_POSITIONS:
            self.arduino.change_position(position)
            
            wavelength = pyin.inputFloat(prompt='Enter the wavelength for the current position: ',
                                         min=WAVELENGTH_MIN, max=WAVELENGTH_MAX)

            wavelengths.append(wavelength)
        
        self.config_handler.calibrate(wavelengths, CALIBRATION_POSITIONS)
        self.config_handler.save_config()
        info_message('Finished.', 'Information')
    