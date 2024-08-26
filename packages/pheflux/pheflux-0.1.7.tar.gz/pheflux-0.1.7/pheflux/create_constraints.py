from cobra.core.model import Model as SBMLModel
from casadi import vertcat, SX, log

def is_number(s: str) -> bool:
    try:
        float(s)  # for int, float, and complex numbers
        return True
    except ValueError:
        return False

def createConstraints(
        model:SBMLModel,
        reaction_names:list[tuple[str,str]],
        k:float,
        v_dic,
        sumVi:SX, 
        sx_variables):
    """
    Input:
        model (cobra.Model): Metabolic model.
        k (float): SumV constraint value.
        v_dic (dict): Dictionary with CasADI variables.
        sumVi (CasADI object): Sum of all variables.
    
    Output:
        tuple: Lists of upper and lower bounds for constraints, and CasADI object with all constraints.
    """
    g = vertcat()
    lbg,ubg=[],[]
    ##############################################################
    ## Gets the name of the forward/reverse variables
    v_vars, rev_vars = zip(*reaction_names)
    v_vars = list(v_vars)
    rev_vars = list(rev_vars)
    ##############################################################
    ## Defines constraints
    discard = False
    ops = {"*","-","+"}
    for met in model.metabolites:
        ##########################################################
        ## Gets constraint for a one metabolite
        elements = str(met.constraint.expression).replace("*"," * ").split()
        sx_expression = []
        mults = []
        for im, e in enumerate(elements):
            if e=="*":
                mults.append(im)
            if is_number(e):
                e = float(e)
            
            elif e not in ops and not is_number(e):
                e_ = sx_variables.get(e)
                if e_ is None:
                    discard = True
                else:
                    e = e_
            sx_expression.append(e)
        #breakpoint()
        #constraint = str(met.constraint.expression).replace('+ ','+').replace('- ','-')
        ##########################################################
        ## Reconstruct the constraint as a CasADI object
        post_sx_expression = []
        new_muls = []
        if not discard:
            for im in mults:
                pre = im-1
                post = im+1
                pre_val = sx_expression[pre]
                post_val = sx_expression[post]
                post_sx_expression.append(pre_val*post_val)
                next_symbol = im+2
                if next_symbol<len(sx_expression):
                    symbol = sx_expression[next_symbol]
                    post_sx_expression.append(f"{symbol}")

            for m,value in enumerate(post_sx_expression):
                if m==0:
                    tmp_constraint = value 

                if value in {"-","+"}:
                    pre_value = post_sx_expression[m-1]
                    post_value = post_sx_expression[m+1]
                    
                    match value:
                        case "-":
                            tmp_constraint -= post_value
                        case "+":
                            tmp_constraint += post_value

            ##########################################################
            ## Adds constraint to CasADI
            g = vertcat(g,tmp_constraint)
            lbg.append(0)
            ubg.append(0)
        discard = False
    ##############################################################
    ## SumV constraint
    g = vertcat(g,sumVi)
    lbg.append( k )
    ubg.append( k )

    return ubg,lbg,g
