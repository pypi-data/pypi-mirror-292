from cobra.core.model import Model as SBMLModel

def getForwardReverse(model):
    """
    Input:
        model (cobra.Model): Metabolic model.
    
    Output:
        tuple: Lists of forward and reverse variable names.
    """
    v_vars, rev_vars = [], []
    for reaction in model.reactions:
        v_vars.append(reaction.id)
        rev_vars.append(reaction.reverse_id)  
    return(v_vars,rev_vars)
