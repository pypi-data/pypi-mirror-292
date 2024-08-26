import polars as pl
from collections import namedtuple
from rich import print
from cobra.core.model import Model as SBMLModel

"""
##############################################################################
# UPDATE MODEL
def updateModel(model_default,mediumFile):
    model=model_default.copy()
    ##########################################################
    ## Add 'R_' to reactions names
    for reaction in model.reactions:
        reaction.id = 'R_'+reaction.id
    ##########################################################        
    ## Opening the model: exchange reactions
    for rxn in model.reactions: 
        if (rxn.lower_bound<0 and rxn.upper_bound>0):
            rxn.bounds = (-1000,1000)
        if (rxn.lower_bound>=0 and rxn.upper_bound>0):
            rxn.bounds = (0,1000)
        if (rxn.lower_bound<0 and rxn.upper_bound<=0):
            rxn.bounds = (-1000,0)
    ##########################################################
    ## Set culture medium
    #############################################
    if mediumFile != 'NA':
        #####################
        # load medium
        medium = pd.read_csv(mediumFile,sep="\t", lineterminator='\n')
        #####################
        # set bounds of exchange reactions to (0, 1000)
        for reaction in model.exchanges:
            reaction.bounds = (0, 1000)
        #####################
        # add culture medium
        for reaction in medium['Reaction_ID']:
            if 'R_'+reaction in model.reactions:
                model.reactions.get_by_id('R_'+reaction).lower_bound = -1000
        
    return(model)


"""

def update_model(
        model_default:SBMLModel,
        medium:pl.DataFrame):
    """
    Input:
        model_default (cobra.Model): Original metabolic model.
        mediumFile (str): File name of the medium conditions.
    
    Output:
        cobra.Model: Updated metabolic model.
    """
    model = model_default.copy()
    ##########################################################
    ## Add 'R_' to reactions names
    for rxn in model.reactions:
        rxn.id = f"R_{rxn.id}"
        lower = rxn.lower_bound
        upper = rxn.upper_bound
        match lower, upper:
            case (v1,v2) if v1<0 and v2>0:
                rxn.bounds = (-1000,1000)
            case (v1,v2) if v1>=0 and v2>0:
                rxn.bounds = (0,1000)
            case (v1,v2) if v1<0 and v2<=0:
                rxn.bounds = (-1000,0)
    ##########################################################
    ## Set culture medium
    #############################################
    if not medium.is_empty():
        for reaction in model.exchanges:
            reaction.bounds = (0, 1000)

        unique_reactions = medium.select(pl.col("Reaction_ID").unique()).to_series().to_list()

        for reaction in unique_reactions:
            name = f"R_{reaction}"
            if name in model.reactions:
                model.reactions.get_by_id(name).lower_bound = -1000


    return model
