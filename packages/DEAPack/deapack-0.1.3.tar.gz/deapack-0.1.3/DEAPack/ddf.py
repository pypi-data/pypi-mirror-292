
import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, lpDot, LpMaximize
from .solver import solve_lp_problem
from typing import Optional, Literal

class DDF:
    '''
    Directional Distance Function (DDF).

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

    Attributes
    ----------
    all prameters is stored as attributes.

    Methods
    -------
    calc_distance(DMU_index, ref_index)
        Calculate the distance to the prodcution frontier for a specific DMU.
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
                 ):
        self.DMUs = DMUs
        self.x_vars = x_vars
        self.y_vars = y_vars
        self.b_vars = b_vars
        self.return_to_scale = return_to_scale
        self.g_x = g_x
        self.g_y = g_y
        self.g_b = g_b
        self.radial = radial
        self.weight_x = weight_x
        self.weight_y = weight_y
        self.weight_b = weight_b


    # patch the parameters
    def patch_parameters(self):
        if self.return_to_scale is None:
            self.return_to_scale = 'CRS'
        if self.radial is None:
            self.radial = True
        if self.g_x is None:
            self.g_x = -self.x_vars
        if self.g_y is None:
            self.g_y = self.y_vars
        if self.b_vars is not None and self.g_b is None:
            self.g_b = -self.b_vars
        if not self.radial:
            if self.b_vars is None and self.weight_x is None:
                self.weight_x = [1/self.x_vars.shape[1]/2]*self.x_vars.shape[1]
                self.weight_y = [1/self.y_vars.shape[1]/2]*self.y_vars.shape[1]
            if self.b_vars is not None and self.weight_x is None:
                self.weight_x = [1/self.x_vars.shape[1]/3]*self.x_vars.shape[1]
                self.weight_y = [1/self.y_vars.shape[1]/3]*self.y_vars.shape[1]
                self.weight_b = [1/self.b_vars.shape[1]/3]*self.b_vars.shape[1]
                

    # define a LP problem
    def define_lp_problem(self, DMU_index: int, ref_index: list[int]) -> LpProblem:
        # the LP problem
        lp_problem = LpProblem('lp_problem', LpMaximize)

        if self.radial:
            # the variables
            beta = LpVariable("beta", lowBound=0, cat="Continuous")
            lambda_n = list(LpVariable.dicts("lambda", range(len(ref_index)), lowBound=0, cat="Continuous").values())

            # the objective
            lp_problem += beta

            # the constraints
            for j in range(self.x_vars.shape[1]):
                lp_problem += lpDot(lambda_n, self.x_vars.iloc[ref_index,j]) <= self.x_vars.iloc[DMU_index, j] + beta*self.g_x.iloc[DMU_index, j]
            
            for j in range(self.y_vars.shape[1]):
                lp_problem += lpDot(lambda_n, self.y_vars.iloc[ref_index,j]) >= self.y_vars.iloc[DMU_index, j] + beta*self.g_y.iloc[DMU_index, j]

            if self.b_vars is not None:
                for j in range(self.b_vars.shape[1]):
                    lp_problem += lpDot(lambda_n, self.b_vars.iloc[ref_index,j]) == self.b_vars.iloc[DMU_index, j] + beta*self.g_b.iloc[DMU_index, j]
            
            if self.return_to_scale == 'VRS':
                lp_problem += lpSum(lambda_n) == 1
        
        else:
            # the variables
            beta_x = list(LpVariable.dicts("beta_x", range(self.x_vars.shape[1]), lowBound=0, cat="Continuous").values())
            beta_y = list(LpVariable.dicts("beta_y", range(self.y_vars.shape[1]), lowBound=0, cat="Continuous").values())
            if self.b_vars is not None:
                beta_b = list(LpVariable.dicts("beta_b", range(self.b_vars.shape[1]), lowBound=0, cat="Continuous").values())
            
            lambda_n = list(LpVariable.dicts("lambda", range(len(ref_index)), lowBound=0, cat="Continuous").values())

            # the objective
            if self.b_vars is None:
                lp_problem += lpDot(beta_x, self.weight_x) + lpDot(beta_y, self.weight_y)
            else:
                lp_problem += lpDot(beta_x, self.weight_x) + lpDot(beta_y, self.weight_y) + lpDot(beta_b, self.weight_b)
            
            # the constraints
            for j in range(self.x_vars.shape[1]):
                lp_problem += lpDot(lambda_n, self.x_vars.iloc[ref_index,j]) <= self.x_vars.iloc[DMU_index, j] + beta_x[j]*self.g_x.iloc[DMU_index, j]
            
            for j in range(self.y_vars.shape[1]):
                lp_problem += lpDot(lambda_n, self.y_vars.iloc[ref_index,j]) >= self.y_vars.iloc[DMU_index, j] + beta_y[j]*self.g_y.iloc[DMU_index, j]
            
            if self.b_vars is not None:
                for j in range(self.b_vars.shape[1]):
                    lp_problem += lpDot(lambda_n, self.b_vars.iloc[ref_index,j]) == self.b_vars.iloc[DMU_index, j] + beta_b[j]*self.g_b.iloc[DMU_index, j]
            
            if self.return_to_scale == 'VRS':
                lp_problem += lpSum(lambda_n) == 1
            
        return lp_problem
    
    
    def calc_distance(self, DMU_index: int, ref_index: list[int]) -> Optional[float]:
        """
        Calculate the distance to the prodcution frontier for a specific DMU.
        """
        self.patch_parameters()
        lp_problem = self.define_lp_problem(DMU_index, ref_index)
        return solve_lp_problem(lp_problem)
