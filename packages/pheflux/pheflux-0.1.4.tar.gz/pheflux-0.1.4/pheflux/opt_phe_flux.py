import polars as pl
from collections import namedtuple
from rich import print
from cobra.core.model import Model as SBMLModel
from collections import namedtuple
from casadi import nlpsol
import time
import pandas as pd
import polars as pl
from pheflux.set_variables import set_variables, CasADIData
from pheflux.sum_v import getSumV
from pheflux.create_constraints import createConstraints

Fluxes = namedtuple("Fluxes",[
    "series",
    "optimization_time",
    "total_time",
    "status",
    "success_flag",
    "bounds"
])


def fill_unknown(df:pl.DataFrame)->pl.DataFrame:
    exists = df.filter(pl.col('Gene_ID') == "G_UNKNOWN").count().to_dict()["Gene_ID"][0] > 0

    if not exists:
        df = df[["Gene_ID", "Expression"]]
        average_expression = df.select(
            pl.col("Expression").mean()
        ).item()
        item = {"Gene_ID":"G_UNKNOWN",
                "Expression":average_expression}
        new_row = pl.DataFrame([item])
        df = df.vstack(new_row)
        return df
    else:
        return fpkm

def opt_phe_flux(
        model:SBMLModel,
        fpkm:pl.DataFrame,
        init_time:float,
        k:float=1000,
)->Fluxes:

    """
    Input:
        model (cobra.Model): Metabolic model.
        fpkmDic (dict): Dictionary with gene expression values.
        k (float): SumV constraint value.
        init_time (float): Initial time for measuring optimization time.
    
    Output:
        tuple: Series with fluxes, optimization time, total time, status, success flag, and lists of lower and upper bounds.
    """
    fpkm = fill_unknown(fpkm)
    casadi_data= set_variables(model,fpkm)
    sumVi = getSumV(casadi_data.casadi)
    ubg, lbg, g = createConstraints(
        model,
        casadi_data.names,
        k,
        casadi_data.variables,
        sumVi, 
        casadi_data.sx_variables)    

    #v,v_dic,lbx,ubx,f 
    v = casadi_data.casadi
    f = casadi_data.objetive_fn
    lbx = casadi_data.lower_bounds
    ubx = casadi_data.upper_bounds
    ##############################################################
    # Non-linear programming
    nlp = {}     # NLP declaration
    nlp['x']=  v # variables
    nlp['f'] = f # objective function
    nlp['g'] = g # constraints

    ##############################################################
    # Create solver instance, define Fcas optimization function 
    options = {"ipopt":{"print_level":3}}
    Fcas = nlpsol('F','ipopt',nlp,options)
    ##############################################################
    ##############################################################
    # Solve the problem using a guess
    fba_primal = casadi_data.primal
    x0=[]
    for i in range(v.shape[0]): # VARIABLES
        x0.append(fba_primal[str(v[i])])       
    ## Solver
    start = time.time()
    sol=Fcas(x0=x0,ubg=ubg,lbg=lbg,lbx=lbx,ubx=ubx)
    final = time.time()
    total_time = final - init_time
    optimization_time = final - start
    status = Fcas.stats()['return_status']
    success = Fcas.stats()['success']
    ##############################################################
    ## Save data as Pandas Series
    PheFlux = sol['x']
    PheFlux_fluxes = {}
    dataset = []
    for num, i in enumerate (range(0, v.shape[0] , 2)):
        name = str(v[i])
        reaction_flux = ( PheFlux[i] - PheFlux[i+1] ) # (forward - reverse)
        item = {"name":name, "value": float(reaction_flux)}
        dataset.append(item)

    PheFlux_fluxes = pl.DataFrame(dataset)

    return PheFlux_fluxes,optimization_time,total_time,status,success, lbx, ubx
