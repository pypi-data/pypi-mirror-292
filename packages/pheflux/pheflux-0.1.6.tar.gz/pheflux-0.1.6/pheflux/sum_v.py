from casadi import SX

def getSumV(casadi:SX)->SX:
    """
    Input:
        v (CasADI object): Vector of variables.
    
    Output:
        CasADI object: Sum of all variables.
    """
    n = casadi.shape[0]
    for i in range(n): # VARIABLES
        name = casadi[i]
        if i == 0:
            sumVi = name
        else:
            sumVi += name     
    return sumVi 
