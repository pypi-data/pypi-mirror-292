
import pandas as pd
from DEAPack.model import DDF
from DEAPack.solver import solve_lp_problem
from typing import Optional, Literal

class ProdNP(DDF):
    '''
    The ProdNP class is used to calculate the productivity index of Decision Making Units (DMUs) based on nonparametric methods.

    Parameters
    ----------
    DMUs : pandas.Series
        The column of DMUs.
    x_vars : pandas.DataFrame
        The data frame of input variables, where the rows are the DMUs and the columns are the input variables.
    y_vars : pandas.DataFrame
        The data frame of desirable variables, where the rows are the DMUs and the columns are the desirable variables.
    b_vars : pandas.DataFrame, optional
        The data frame of undesirable variables, where the rows are the DMUs and the columns are the undesirable variables.
    return_to_scale : str, optional
        The type of return to scale, either 'CRS' (constant return to scale) or 'VRS' (variable return to scale). The default is 'CRS'.
    g_x : pandas.DataFrame, optional
        The data frame of direction components for input adjustment, where the rows are the DMUs and the columns are the input variables. The default is -x_vars.
    g_y : pandas.DataFrame, optional
        The data frame of direction components for desirable output adjustment, where the rows are the DMUs and the columns are the desirable variables. The default is y_vars.
    g_b : pandas.DataFrame, optional
        The data frame of direction components for undesirable output adjustment, where the rows are the DMUs and the columns are the undesirable variables. The default is -b_vars.
    radial : bool, optional
        The type of DEA model, either radial (True) or non-radial (False). The default is True.
    weight_x : list, optional
        The list of weights for the input variables. The default is [1/x_vars.shape[1]/2]*x_vars.shape[1] if no b_vars is provided, otherwise [1/x_vars.shape[1]/3]*x_vars.shape[1].
    weight_y : list, optional
        The list of weights for the desirable variables. The default is [1/y_vars.shape[1]/2]*y_vars.shape[1] if no b_vars is provided, otherwise [1/y_vars.shape[1]/3]*y_vars.shape[1].
    weight_b : list, optional
        The list of weights for the non-discretionary variables. The default is [1/b_vars.shape[1]/2]*b_vars.shape[1] if no b_vars is provided, otherwise [1/b_vars.shape[1]/3]*b_vars.shape[1].
    time : pandas.Series, optional
        The series of time index for panel data.
    ref_type : str, optional
        The type of reference set, either 'Contemporaneous', 'Global', 'Sequential', 'Window', or 'Biennial'. The default is 'Contemporaneous'.
    window : int, optional
        The window size for the 'Window' reference set. The default is 1.
    index_type : str, optional
        The type of productivity index, either 'Malmquist' or 'Luenberger'. The default is 'Malmquist'.

    Attributes
    ----------
    prod_ch : pd.Series
        Estimated productivity change.
    eff_ch : pd.Series
        Estimated efficiency change, one component of productivity change.
    te_ch : pd.Series
        Estimated technique change, one component of productivity change.
    all prameters is also stored as attributes.

    Methods
    -------
    solve(parallel=False, n_jobs=None)
        Solve the model, calculate the index.
    '''
    def __init__(self, 
                 DMUs: Optional[pd.Series] = None,
                 x_vars: Optional[pd.DataFrame] = None, 
                 y_vars: Optional[pd.DataFrame] = None, 
                 b_vars: Optional[pd.DataFrame] = None,
                 return_to_scale: Literal['CRS', 'VRS'] = None,
                 g_x: Optional[pd.DataFrame] = None, 
                 g_y: Optional[pd.DataFrame] = None, 
                 g_b: Optional[pd.DataFrame] = None,
                 radial: Optional[bool] = None,
                 weight_x: Optional[list] = None,
                 weight_y: Optional[list] = None,
                 weight_b: Optional[list] = None,
                 time: Optional[pd.Series] = None, 
                 ref_type: Literal['Contemporaneous', 'Global', 'Sequential', 'Window', 'Biennial'] = None,
                 window: int = None,
                 index_type: Literal['Malmquist', 'Luenberger'] = None
                 ):
        super().__init__(DMUs=DMUs, 
                         x_vars=x_vars, 
                         y_vars=y_vars, 
                         b_vars=b_vars,
                         return_to_scale=return_to_scale, 
                         g_x=g_x, 
                         g_y=g_y, 
                         g_b=g_b, 
                         radial=radial, 
                         weight_x=weight_x,
                         weight_y=weight_y, 
                         weight_b=weight_b)
        self.time = time
        self.ref_type = ref_type
        self.window = window
        self.index_type = index_type
        self.distance = None
        self.prod_ch = None
        self.eff_ch = None
        self.te_ch = None


    # patch the parameters
    def patch_parameters(self):
        super().patch_parameters()
        if self.time is not None and self.ref_type is None:
            self.ref_type = 'Contemporaneous'
        if self.ref_type == 'Window' and self.window is None:
            self.window = 1
        if self.index_type is None:
            self.index_type = 'Malmquist'


    # create a list of LP problems
    def create_problem_list(self) -> list:
        problem_list_st = []
        problem_list_tt = []
        problem_list_ts = []

        for i in range(self.DMUs.shape[0]):
            if self.ref_type == 'Contemporaneous':
                ref_index = self.time.index[self.time == self.time[i]].tolist()
            elif self.ref_type == 'Global':
                ref_index = range(self.DMUs.shape[0])
            elif self.ref_type == 'Sequential':
                ref_index = self.time.index[self.time <= self.time[i]].tolist()
            elif self.ref_type == 'Window':
                ref_index = self.time.index[(self.time <= (self.time[i]+self.window)) & (self.time >= (self.time[i]-self.window))].tolist()
            elif self.ref_type == 'Biennial':
                ref_index = self.time.index[(self.time == self.time[i]) | (self.time == (self.time[i]+1))].tolist()
            else:
                raise ValueError('The ref_type is not valid.')
                
            problem_list_tt.append(self.define_lp_problem(i, ref_index))
        
        for i in range(self.DMUs.shape[0]):
            if self.time[i] == self.time.min():
                ref_index = self.time.index[self.time == self.time[i]].tolist()
            elif self.ref_type == 'Contemporaneous':
                ref_index = self.time.index[self.time == self.time[i]-1].tolist()
            elif self.ref_type == 'Global':
                ref_index = range(self.DMUs.shape[0])
            elif self.ref_type == 'Sequential':
                ref_index = self.time.index[self.time <= self.time[i]-1].tolist()
            elif self.ref_type == 'Window':
                ref_index = self.time.index[(self.time <= (self.time[i]-1+self.window)) & (self.time >= (self.time[i]-1-self.window))].tolist()
            elif self.ref_type == 'Biennial':
                ref_index = self.time.index[(self.time == self.time[i]-1) | (self.time == (self.time[i]))].tolist()
            else:
                raise ValueError('The ref_type is not valid.')
            
            problem_list_ts.append(self.define_lp_problem(i, ref_index))
        
        for i in range(self.DMUs.shape[0]):
            if self.time[i] == self.time.max():
                ref_index = self.time.index[self.time == self.time[i]].tolist()
            elif self.ref_type == 'Contemporaneous':
                ref_index = self.time.index[self.time == self.time[i]+1].tolist()
            elif self.ref_type == 'Global':
                ref_index = range(self.DMUs.shape[0])
            elif self.ref_type == 'Sequential':
                ref_index = self.time.index[self.time <= self.time[i]+1].tolist()
            elif self.ref_type == 'Window':
                ref_index = self.time.index[(self.time <= (self.time[i]+1+self.window)) & (self.time >= (self.time[i]+1-self.window))].tolist()
            elif self.ref_type == 'Biennial':
                ref_index = self.time.index[(self.time == self.time[i]+1) | (self.time == (self.time[i]))].tolist()
            else:
                raise ValueError('The ref_type is not valid.')
            
            problem_list_st.append(self.define_lp_problem(i, ref_index))

        return problem_list_tt + problem_list_ts + problem_list_st


    # solve the model, calculate the distance to the frontier and the index
    def solve(self, parallel: bool = False, n_jobs: int = None):
        '''
        Solve the model, calculate the distance to the frontier and the index.

        Parameters
        ----------
        parallel : bool, optional
            Whether to use parallel computing. The default is False.

            !!! The multiprocessing may not work in some instances.

        n_jobs : int, optional
            The number of jobs to run in parallel. The default is (n_processors-2).
        '''
        self.patch_parameters()

        problem_list = self.create_problem_list()
            
        if parallel:
            import multiprocessing
            if n_jobs is None:
                n_jobs = multiprocessing.cpu_count()
            pool = multiprocessing.Pool(n_jobs)        
            self.distance = pool.map(solve_lp_problem, problem_list)
            pool.close()
            pool.join()
        else:
            self.distance = [solve_lp_problem(prob) for prob in problem_list]
        
        self.calc_prod_ch()

        
    # calculate the efficiency score, based on the distance to the frontier
    def calc_prod_ch(self) -> pd.Series:
        '''
        Calculate the efficiency score, based on the distance to the frontier.
        
        Standardized the score to be between 0 and 1. The higher the score, the more efficient the DMU.
        '''
        distance_tt = pd.Series(self.distance[:self.DMUs.shape[0]])
        distance_ts = pd.Series(self.distance[self.DMUs.shape[0]:2*self.DMUs.shape[0]])
        distance_st = pd.Series(self.distance[2*self.DMUs.shape[0]:])
        
        prod_ch = pd.Series(0, index=self.DMUs.index)
        eff_ch = pd.Series(0, index=self.DMUs.index)
        te_ch = pd.Series(0, index=self.DMUs.index)
        
        for i in range(self.DMUs.shape[0]):
            if self.time[i] == self.time.min():
                prod_ch[i] = None
                eff_ch[i] = None
                te_ch[i] = None
            else:
                d_st = distance_st[(self.DMUs==self.DMUs[i]) & (self.time==self.time[i]-1)].iloc[0]
                d_tt = distance_tt[i]
                d_ss = distance_tt[(self.DMUs==self.DMUs[i]) & (self.time==self.time[i]-1)].iloc[0]
                d_ts = distance_ts[i]
                prod_ch_t = None
                prod_ch_s = None
                te_ch_s = None
                te_ch_t = None

                if self.index_type == 'Malmquist':
                    if d_st is not None and d_tt is not None:
                        prod_ch_t = (1+d_st)/(1+d_tt)
                    if d_ss is not None and d_ts is not None:
                        prod_ch_s = (1+d_ss)/(1+d_ts)
                        
                    if prod_ch_t is not None and prod_ch_s is not None:
                        prod_ch[i] = (prod_ch_t*prod_ch_s)**0.5
                    elif prod_ch_t is not None:
                        prod_ch[i] = prod_ch_t
                    elif prod_ch_s is not None:
                        prod_ch[i] = prod_ch_s
                    else:
                        prod_ch[i] = None

                    if d_ss is not None and d_tt is not None:
                        eff_ch[i] = (1+d_ss)/(1+d_tt)
                    else:
                        eff_ch[i] = None

                    if d_st is not None and d_ss is not None:
                        te_ch_s = (1+d_st)/(1+d_ss)
                    if d_tt is not None and d_ts is not None:
                        te_ch_t = (1+d_tt)/(1+d_ts)
                    if te_ch_s is not None and te_ch_t is not None:
                        te_ch[i] = (te_ch_s*te_ch_t)**0.5
                    elif te_ch_s is not None:
                        te_ch[i] = te_ch_s
                    elif te_ch_t is not None:
                        te_ch[i] = te_ch_t
                    else:
                        te_ch[i] = None

                elif self.index_type == 'Luenberger':
                    if d_st is not None and d_tt is not None:
                        prod_ch_t = d_st-d_tt
                    if d_ss is not None and d_ts is not None:
                        prod_ch_s = d_ss-d_ts
                        
                    if prod_ch_t is not None and prod_ch_s is not None:
                        prod_ch[i] = (prod_ch_t+prod_ch_s)/2
                    elif prod_ch_t is not None:
                        prod_ch[i] = prod_ch_t
                    elif prod_ch_s is not None:
                        prod_ch[i] = prod_ch_s
                    else:
                        prod_ch[i] = None
                    if d_ss is not None and d_tt is not None:
                        eff_ch[i] = d_ss-d_tt
                    else:
                        eff_ch[i] = None
                    if d_st is not None and d_ss is not None:
                        te_ch_s = d_st-d_ss
                    if d_tt is not None and d_ts is not None:
                        te_ch_t = d_tt-d_ts
                    if te_ch_s is not None and te_ch_t is not None:
                        te_ch[i] = (te_ch_s+te_ch_t)/2
                    elif te_ch_s is not None:
                        te_ch[i] = te_ch_s
                    elif te_ch_t is not None:
                        te_ch[i] = te_ch_t
                    else:
                        te_ch[i] = None
                else:
                    raise ValueError('The index_type is not valid.')

        self.prod_ch = prod_ch
        self.eff_ch = eff_ch
        self.te_ch = te_ch
