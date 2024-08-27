from SiEPIC_TestCreator.sequences.core.smu_sweep import SmuSweep
import time

class SetWavelengthVoltageSweepIda(SmuSweep):
    """
    Sets the wavelength then performs a voltage sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start voltage (V)',
            'Start_bounds': [-100, 100],
            'Stop': 1, 
            'Stop_info': 'Please enter stop voltage (V)',
            'Stop_bounds': [-100, 100],
            'Step': 0.1, 
            'Step_info': 'Please enter stepsize (V)',
            'Step_bounds': [0.01, 100],
            'Center': '',
            'Center_info': 'Please enter center voltage',
            'Center_bounds': [0, 100],
            'Span': '',
            'Span_info': 'Please enter span voltage',
            'Span_bounds': [0, 100],
            'Range': '',
            'Range_info': 'Please enter range voltage',
            'Range_bounds': [0, 100],
            'Spacing': '',
            'Spacing_info': 'Please enter spacing voltage',
            'Spacing_bounds': [0, 100],
            'Points': '',
            'Points_info': 'Please enter points voltage',
            'Points_bounds': [0, 1000],
            'Direction': 'UP',
            'Direction_info': 'Please enter direction voltage',
            'Direction_options': ['UP', 'DOWN'],
            'Sweeptype': 'Voltage',
            'Sweeptype_info': 'Please enter sweep type',
            'Sweeptype_options': ['Voltage'],
            'Upper Limit': 5,
            'Upper Limit_info': 'Please enter upper limit voltage',
            'Upper Limit_bounds': [0, 100],
            'Trans_col': 'False',
            'Trans_col_info': 'Please enter transition either True or False',
            'Trans_col_options': ['True', 'False'],
            'Channel A': 'True',
            'Channel A_info': 'Please enter True to use Channel A if not enter False',
            'Channel A_options': ['True', 'False'],
            'Channel B': 'False',
            'Channel B_info': 'Please enter True to use Channel B if not enter False',
            'Channel B_options': ['True', 'False'],
            'Wavelengths': '1480, 1550, 1580',
            'Wavelengths_info': 'Set wavelengths in form x, x1, x2 with unit nm',
            'Wavelengths_bounds': [[1270, 1480], [1350, 1580]],
            'Power': 1,
            'Power_info': 'make sure you match the input to the unit selected',
            'Power_bounds': [-70, 10],
            'Power Unit': 'dBm',
            'Power Unit_options': ['dBm', 'mW'],
            'Channel Stagger': 'Staggered',
            'Channel Stagger_info': 'Choose whether to stagger the channels or have them sweep at the same time, NOTE: for sync channels must be apart of the same smu unit',
            'Channel Stagger_options': ['Sync', 'Staggered']
        }

        self.results_info = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Set Wavelength Voltage Sweep',
            'save_location': '',
            'foldername': '',
            'xtitle': 'Voltage (V)',
            'ytitle': 'Current (A)',
            'xscale': 1,
            'yscale': 1,
            'legend': True,
            'csv': True,
            'pdf': True,
            'mat': True,
            'pkl': False
        }

        super().__init__(variables=self.variables, resultsinfo=self.resultsinfo, sweeptype='voltage', ps=ps)

    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)

        settings = self.ps.get_settings(self.verbose)

        for wav in self.variables['wavelengths']:
            self.ps.optprobe.laser.set_wavl(wav)
            self.ps.optprobe.laser.set_pwr_unit('dBm')
            self.ps.optprobe.laser.set_pwr(self.variables['pwr'])
            self.ps.optprobe.laser.set_pwr_unit('mW')
            self.ps.optprobe.laser.set_output(True)
            time.sleep(3)
        
            self.execute()

            self.ps.optprobe.laser.set_output(False)

        
        self.ps.set_settings(settings)