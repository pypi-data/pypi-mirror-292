from casadi import vertcat, SX, log
from collections import namedtuple
from cobra.core.model import Model as SBMLModel
import polars as pl
from pheflux.get_eg import get_gene_expression, BIAS
from gene_rule_parser import (
    ExpressionParser, 
    tree_analysis, 
    Gene, 
    distribute_rules)
from dataclasses import field
from pydantic.dataclasses import dataclass

CasADIData = namedtuple("CasADIData", ["casadi", "names","variables",
                                       "lower_bounds", "upper_bounds", 
                                       "objetive_fn", "sx_variables", 
                                       "primal"]) 


@dataclass(config=dict(arbitrary_types_allowed=True))
class ReactionVariables:
    variables:dict[str, SX] = field(default_factory=dict)

    def set(self, key, value):
        self.variables[key] = value
    
    def get(self, key):
        return self.variables.get(key)


def set_variables(
        model:SBMLModel, 
        fpkm:pl.DataFrame
)->CasADIData:
    """
    Input:
        model (cobra.Model): Metabolic model.
        fpkmDic (dict): Dictionary with gene expression values.
    
    Output:
        tuple: CasADI object with all variables, dictionary with CasADI variables, lists of lower and upper bounds, and objective function.
    """
    
    v = vertcat() # saves the total of variables of the model. Used to """nlp['x']"""
    v_dic = {}
    v_fpkm = {} # 
    fba_primal = {}
    ubx, lbx = [],[]
    reaction_names = []
    ##############################################################
    ## Gets the median value of 'g'
    parser = ExpressionParser()
    # Esperanza(g), g_metab (booleans by rule [dict])

    
    gen_metab = get_gene_expression(parser, model, fpkm)     
    r_vars = ReactionVariables()
    counter = 0

    for i, reaction in enumerate(model.reactions):
        rule = reaction.gene_reaction_rule
        # dar expr genética = promedio de las conocidas
        fba_primal[reaction.id] = getattr(model.variables,
                                         reaction.id).primal
        fba_primal[reaction.reverse_id] = getattr(model.variables,
                                                  reaction.reverse_id).primal

        var_name = reaction.id
        reaction_id = var_name
        var_name = SX.sym(var_name)
        v = vertcat(v, var_name)

        var_name_reverse = reaction.reverse_id
        var_name_reverse = SX.sym(var_name_reverse)
        v = vertcat(v,var_name_reverse)
        
        # add primals, get default
        g = gen_metab.get(rule)
        
        #reaction = gen_metab.get_id(rule)
        
        r_vars.set(reaction.id, var_name)
        v_dic[reaction_id] = var_name

        ubx.append(reaction.upper_bound)    
        lbx.append(0.0)

        # reverse
        r_vars.set(reaction.reverse_id, var_name_reverse)
        v_dic[reaction.reverse_id] = var_name_reverse

        ubx.append(-reaction.lower_bound)
        lbx.append(0.0)

        #
        reaction_names.append((reaction.id, reaction.reverse_id))
        # calc
        v_fpkm[var_name] = g
        v_fpkm[var_name_reverse] = g

        ##########################################################
        ## Define a objective function
        for j, name in enumerate([var_name,var_name_reverse]):
            if counter == 0 and j==0:
                v_ViLogVi = ( (name)+BIAS )*log( (name)+BIAS ) # 1.1
                v_VilogQi = ( (name)+BIAS )*log( g ) # 2.1
            else:
                v_ViLogVi += ( (name)+BIAS )*log( (name)+BIAS ) # 1.1
                v_VilogQi += ( (name)+BIAS )*log( g ) # 2.1            
        counter += 1
    ##############################################################
    ## Set objetive function
    f = (v_ViLogVi) - (v_VilogQi)
    # v is ---> x variables
    # f is ---> f objetive function
    return CasADIData(v,reaction_names, v_dic,lbx,ubx,f, r_vars, fba_primal)
    #gen_metab: contains list of genes and values, and have property method: mean
#################################################################################
### Variables and objective function: CasADI object
"""
def setVariables(model,fpkmDic):
    v = vertcat() 
    v_dic = {}
    v_fpkm = {} # 
    ubx, lbx = [],[]
    ##############################################################
    ## Gets the median value of 'g'
    E_g,g_metab = getEg(model,fpkmDic)     
    
    for i, reaction in enumerate(model.reactions):
        ##########################################################
        ## Gets the GPR and a boolean list with known or unknown genes
        rule = reaction.gene_reaction_rule # gene reaction rule
        boolean_list = booleanVectorRule(rule,fpkmDic) # useful to discriminate between genes with known fkpm.
        ##########################################################
        ## Gets the expression value 'g'
        # get 'g' for reaction with GPR.
        if not ('False' in boolean_list or rule == ''): 
            g = getG(rule, fpkmDic)+1e-8#*1e-8
        # set 'g' (median value) for reaction without GPR. 
        else:
            g = E_g
        ##########################################################
        ## Set forward and reverse variables as a CasADI object
        # forward
        var_name = reaction.id
        expression = var_name+' = SX.sym("'+var_name+'")'
        exec(expression, globals())
        vf = eval(var_name)
        v = vertcat(v, vf)
        v_dic[reaction.id]=vf
        ubx.append(reaction.upper_bound)    
        lbx.append(0.0)

        # reverse
        var_name_reverse = reaction.reverse_id
        expression = var_name_reverse+' = SX.sym("'+var_name_reverse+'")'
        exec(expression, globals())
        vr = eval(var_name_reverse)
        v = vertcat(v,vr)
        v_dic[reaction.reverse_id]=vr
        ubx.append(-reaction.lower_bound)
        lbx.append(0.0)

        v_fpkm[var_name] = g
        v_fpkm[var_name_reverse] = g
        ##########################################################
        ## Define a objective function
        for name in [vf,vr]:
            if i == 0:
                v_ViLogVi = ( (name)+1e-8 )*log( (name)+1e-8 ) # 1.1
                v_VilogQi = ( (name)+1e-8 )*log( g ) # 2.1
            else:
                v_ViLogVi += ( (name)+1e-8 )*log( (name)+1e-8 ) # 1.1
                v_VilogQi += ( (name)+1e-8 )*log( g ) # 2.1            
    ##############################################################
    ## Set objetive function
    f = (v_ViLogVi) - (v_VilogQi)
    return(v,v_dic,lbx,ubx,f)
"""
