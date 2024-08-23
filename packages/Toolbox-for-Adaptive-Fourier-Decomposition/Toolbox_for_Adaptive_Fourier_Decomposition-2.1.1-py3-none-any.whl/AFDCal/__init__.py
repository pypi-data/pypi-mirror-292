from numpy import ndarray
from typing import Union, Optional, Dict, List, Tuple

import importlib

class AFDCal:
    def __init__(self, 
                 n_jobs : Optional[int] = None):
        """
        Initialize AFD calculation

        Parameters
        -----------------
        n_jobs : Optional[int] = None
            Number of threadings for parallel computing (Not implement)
        """
        self.n_jobs = n_jobs
        self.initSetting()
    
    from ._initfun import (initSetting, loadInputSignal, 
                           setDecompMethod, setDicGenMethod, setAFDMethod, 
                           setPhase, setPhase_min_max,
                           set_an_array)
    from ._logfun import clearLog, addLog, dispLog
    from ._decomposition import (genDic, genEva, 
                                 init_decomp, nextDecomp, 
                                 reconstrct, decomp)
    from ._plot import (plot_dict, plot_base, 
                        plot_decomp, plot_basis_comp, 
                        plot_re_sig, plot_energy_rate, 
                        plot_searchRes, plot_base_random, 
                        plot_remainder, plot_an, plot_ori_sig)

    