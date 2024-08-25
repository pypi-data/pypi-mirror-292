from typer import Typer, Argument, Option
from typing_extensions import Annotated

from automatic_spectral_acquisition.core import Core
from automatic_spectral_acquisition.constants import *

def create_config_subcommands() -> Typer:
    app = Typer(no_args_is_help=True, help='Configuration management.')

    @app.command()
    def create():
        """
        Create a new configuration file interactively.
        """
        core = Core()
        core.cli_config_create()
    
    
    @app.command()
    def delete():
        """
        Deletes the configuration file.
        """
        core = Core()
        core.cli_config_delete()


    @app.command()
    def show():
        """
        Show the current configuration.
        """
        core = Core()
        core.cli_config_show()


    @app.command()
    def calibrate():
        """
        Updates the calibration in the configuration file.
        """
        core = Core()
        core.cli_config_calibrate()
    
    return app


def create_app(app_name:str='Spectral data acquisition') -> Typer:
    app = Typer(name=app_name, add_completion=False, no_args_is_help=True)
   
   
    @app.command(short_help='Record a spectrum.')
    def spectrum(start:Annotated[float, Argument(help='Start wavelength')],
                 end:Annotated[float, Argument(help='End wavelength')],
                 step:Annotated[float, Argument(help='Step size')],
                 number_of_measurements:Annotated[int, Option('--number_of_measurements', '-n', help='Number of measurements')]=DEFAULT_NUMBER_OF_MEASUREMENTS,
                 file:Annotated[str, Option('--file', '-f', help='Output file name')]=OUTPUT_FILE,
                 plot:Annotated[bool, Option('--plot', '-p', help='Plot spectrum afterwards')]=False):
        """
        Record a spectrum.
        Using --file <file name> or -f <file name>, the name of the file can be chosen. \"{time}\" will be replaced by the current time.
        If --plot or -p is passed, the spectrum will be plotted after the measurements.
        """
        core = Core()
        core.cli_record_spectrum(start, end, step, number_of_measurements, file, plot)        
        
        
    @app.command()
    def single(wavelength:Annotated[float, Argument(help='Wavelength to measure')],
               number_of_measurements:Annotated[int, Option('--number_of_measurements', '-n', help='Number of measurements')]=DEFAULT_NUMBER_OF_MEASUREMENTS,
               file:Annotated[str, Option('--file', '-f', help='Output file name')]=OUTPUT_FILE,
               print_:Annotated[bool, Option('--print', '-p', help='Print the values measured')]=False):
        """
        Measure a single wavelength.
        Using --file <file name> or -f <file name>, the name of the file can be chosen. \"{time}\" will be replaced by the current time.
        If --print or -p is passed, the values will be printed after the measurement is complete.
        """
        core = Core()
        core.cli_record_single(wavelength, number_of_measurements, file, print_)
    
    app.add_typer(create_config_subcommands(), name='config')
    
    
    return app
