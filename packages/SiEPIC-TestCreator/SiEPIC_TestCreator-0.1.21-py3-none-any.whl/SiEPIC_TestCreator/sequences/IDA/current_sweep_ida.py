from SiEPIC_TestCreator.sequences.core.smu_sweep import SmuSweep

class CurrentSweepIda(SmuSweep):
    """
    Current sweep sequence class.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start current (mA)',
            'Start_bounds': [-1000, 1000],
            'Stop': 1, 
            'Stop_info': 'Please enter stop current (mA)',
            'Stop_bounds': [-1000, 1000],
            'Step': 0.1, 
            'Step_info': 'Please enter stepsize (mA)',
            'Step_bounds': [0.01, 1000],
            'Center': '',
            'Center_info': 'Please enter center current',
            'Center_bounds': [0, 100],
            'Span': '',
            'Span_info': 'Please enter span current',
            'Span_bounds': [0, 100],
            'Range': '',
            'Range_info': 'Please enter range current',
            'Range_bounds': [0, 100],
            'Spacing': '',
            'Spacing_info': 'Please enter spacing current',
            'Spacing_bounds': [0, 100],
            'Points': '',
            'Points_info': 'Please enter points current',
            'Points_bounds': [0, 1000],
            'Direction': 'UP',
            'Direction_info': 'Please enter direction current',
            'Direction_options': ['UP', 'DOWN'],
            'Sweeptype': 'Current',
            'Sweeptype_info': 'Please enter sweep type',
            'Sweeptype_options': ['Current'],
            'Upper Limit': 5,
            'Upper Limit_info': 'Please enter upper limit current',
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
            'Channel Stagger': 'Staggered',
            'Channel Stagger_info': 'Choose whether to stagger the channels or have them sweep at the same time',
            'Channel Stagger_options': ['Sync', 'Staggered']
        }

        self.results_info = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Current Sweep',
            'save_location': '',
            'foldername': '',
            'xtitle': 'Current (A)',
            'ytitle': 'Voltage (V)',
            'xscale': 1,
            'yscale': 1,
            'legend': True,
            'csv': True,
            'pdf': True,
            'mat': True,
            'pkl': False
        }
        
        super().__init__(variables=self.variables,sweeptype='current', resultsinfo=self.resultsinfo, ps=ps)

        
    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        settings = self.ps.get_settings(self.verbose)
        self.execute()
        self.ps.set_settings(settings)