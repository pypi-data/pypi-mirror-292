#!/usr/bin/env python3

from casadi import *
import cobra

import pandas as pd
import numpy as np
import time

from datetime import datetime
import random
import string

from pheflux import getG

##############################################################################
### This function gives a useful vector to discriminate if the FPKM of the
### genes associated with a reaction is known.
def booleanVectorRule (rule, fpkmDic):
    boolean_list = []
    vector_rule = rule.replace("or","")
    vector_rule = vector_rule.replace("and","")
    vector_rule = vector_rule.replace("'","") # Removes "'"
    vector_rule = vector_rule.replace("(","") # Remove "("
    vector_rule = vector_rule.replace(")","")
    vector = vector_rule.split()
    g_vector = []
    for gene in vector:
        g_vector.append( f'G_{gene}' )
    for gene in g_vector:
        if gene in fpkmDic:
            boolean_list.append('True')
        else:
            boolean_list.append('False')
    return boolean_list


##############################################################################
### Loading FPKM data
def loadFPKM(fpkm,condition,shuffle=False,shuffledFPKM=pd.DataFrame()):
    ##########################################################
    ## Gets gene IDs and their expression values
    genes=fpkm["Gene_ID"]
    if shuffle:
        fpkms=fpkm["Expression"].sample(frac=1).reset_index(drop=True) 
    else:
        fpkms=fpkm["Expression"]
    shuffledFPKM["Expression"] = fpkms
    ##########################################################
    ## Creates a dictionary gene_ID -> Expression value
    fpkmDic = {}
    for i in range(len(fpkms)): # Run over each line in fpkm file
        # 1. Get gene id and fpkm values for each line
        name = 'G_'+str(genes[i])
        fpkm = fpkms[i]
        if type(fpkm) == np.float64:
            fpkmDic[name] = fpkm
    ##########################################################
    ## Capping at 95%
    cap = np.percentile( list(fpkmDic.values()), 95)
    for i in fpkmDic:
        if fpkmDic[i]>cap:
            fpkmDic[i] = cap
    return(fpkmDic,shuffledFPKM)

##############################################################################
### Loading FPKM data for Homo sapiens. 
def reloadFPKMHsapiens(fpkmDic, model):
    newfpkmDic = {}
    for gene in model.genes:
        if not 'G_'+gene.name in fpkmDic: continue
        fpkm = fpkmDic['G_'+gene.name]
        gene = 'G_'+gene.id
        newfpkmDic[gene] = fpkm
    return(newfpkmDic)

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

##############################################################################
## Obtains a median value of the expression of genes associated with metabolism
def getEg(model,fpkmDic):
    g_metab = [] # gene expression of reactions partakin in the metabolism
    for i, reaction in enumerate(model.reactions):
        ##########################################################
        ## Gets the GPR and a boolean list with known or unknown genes
        rule = reaction.gene_reaction_rule
        boolean_list = booleanVectorRule(rule,fpkmDic)
        ##########################################################
        ## Gets the expression value 'g'
        if not ('False' in boolean_list or rule == ''): # get 'g' for reaction with GPR.
            g = getG(rule, fpkmDic)
            g_metab.append(g+1e-8)
    ##############################################################
    ## Obtains a median value
    E_g = np.median(g_metab)
    return(E_g,g_metab)

##############################################################################
### SAVE PRIMAL VALUES
def getPrimalValues(model):
    ##########################################################
    ### Model optimize: save fluxes and primal values of variables
    sol = model.optimize()
    fba_primal = {}
    for reaction in model.reactions:
        f_name = reaction.id
        r_name = reaction.reverse_id
        fba_primal[f_name] = eval ('model.variables.'+f_name+'.primal')
        fba_primal[r_name] = eval ('model.variables.'+r_name+'.primal')
    return(fba_primal)
##############################################################################
### Save forward and reverse variables
def getFowardReverse(model):
    v_vars, rev_vars = [], []
    for reaction in model.reactions:
        v_vars.append(reaction.id)
        rev_vars.append(reaction.reverse_id)  
    return(v_vars,rev_vars)


#################################################################################
### Variables and objective function: CasADI object
def setVariables(model,fpkmDic):
    v = vertcat() # saves the total of variables of the model. Used to """nlp['x']"""
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

#################################################################################
### Define a sumV
def getSumV(v):
    for i in range(v.shape[0]): # VARIABLES
        name = v[i]
        if i == 0:
            sumVi = name
        else:
            sumVi += name     
    return(sumVi)

#################################################################################
### Creating constraints
def createConstraints(model,k,v_dic,sumVi):
    g = vertcat()
    lbg,ubg=[],[]
    ##############################################################
    ## Gets the name of the forward/reverse variables
    v_vars, rev_vars = getFowardReverse(model)
    ##############################################################
    ## Defines constraints
    for met in model.metabolites:
        ##########################################################
        ## Gets constraint for a one metabolite
        constraint = str(met.constraint.expression).replace('+ ','+').replace('- ','-')
        ##########################################################
        ## Reconstruct the constraint as a CasADI object
        for i, field in enumerate(constraint.split()):
            if i == 0:
                tmp_constraint = eval(field)
            else:
                tmp_constraint += eval(field)
                
        ##########################################################
        ## Adds constraint to CasADI
        g = vertcat(g,tmp_constraint)
        lbg.append(0)
        ubg.append(0)
    ##############################################################
    ## SumV constraint
    g = vertcat(g,sumVi)
    lbg.append( k )
    ubg.append( k )
    
    return(ubg,lbg,g)

#################################################################################
### OPTIMIZATION
def optPheFlux(model,fpkmDic,k,init_time):
    ##############################################################
    ## Sets variables, sumV and constraints
    v,v_dic,lbx,ubx,f = setVariables(model,fpkmDic)
    sumVi = getSumV(v)
    ubg,lbg,g = createConstraints(model,k,v_dic,sumVi)    
    print('')
    ##############################################################
    # Non-linear programming
    nlp = {}     # NLP declaration
    nlp['x']=  v # variables
    nlp['f'] = f # objective function
    nlp['g'] = g # constraints
    ##############################################################
    # Create solver instance
    options={"ipopt":{"print_level":3}}
    F = nlpsol('F','ipopt',nlp,options)
    ##############################################################
    # Solve the problem using a guess
    fba_primal = getPrimalValues(model)
    x0=[]
    for i in range(v.shape[0]): # VARIABLES
        x0.append(fba_primal[str(v[i])])       
    ##############################################################
    ## Solver
    start = time.time()
    sol=F(x0=x0,ubg=ubg,lbg=lbg,lbx=lbx,ubx=ubx)
    final = time.time()
    total_time = final - init_time
    optimization_time = final - start
    status = F.stats()['return_status']
    success = F.stats()['success']
    ##############################################################
    ## Save data as Pandas Series
    PheFlux = sol['x']
    PheFlux_fluxes = {}
    for num, i in enumerate (range(0, v.shape[0] , 2)):
        name = str(v[i])
        reaction_flux = ( PheFlux[i] - PheFlux[i+1] ) # (forward - reverse)
        PheFlux_fluxes[name] =  float(reaction_flux)
    PheFlux_fluxes = pd.Series(PheFlux_fluxes)

    return(PheFlux_fluxes,optimization_time,total_time,status,success, lbx, ubx)

#################################################################################
### Table of times and variable numbers for networks
def recordTable(record ,condition, lbx, ubx, time, status):   
    variables = 0
    for i in range(len(lbx)):
        if lbx[i] != ubx[i]:
            variables += 1
    
    if record.shape == (0,0):
        record = pd.DataFrame(columns=['Condition', 'N° variables', 'Time', 'Status'])
        
    record.loc[record.shape[0]] = [condition, variables, time, status]
    return (record)

#################################################################################
### print the time
def actual_time():
    now = datetime.now(timezone.utc)
    return now.isoformat()

