import polars as pl
import numpy as np
from cobra.core.reaction import Reaction
from cobra.core.model import Model as SBMLModel
from collections import namedtuple
from pheflux.boolean_vector_rule import boolean_vector_rule
from pheflux.get_g import get_expression_value
from gene_rule_parser import (ExpressionParser, tree_analysis)
from collections import namedtuple
from pydantic.dataclasses import dataclass
from functools import lru_cache
##############################################################################
## Obtains a median value of the expression of genes associated with
## metabolism
import ujson
from pathlib import Path

@dataclass(config=dict(arbitrary_types_allowed=True))
class GenMetab:
    reaction_ids:dict[str,Reaction]
    rules:dict[str, float]
    booleans:dict[str,dict[str, bool]]

    @property
    def mean(self)->float:
        return float(np.mean(list(self.rules.values())))


    def get(self, rule:str)->float:
        return self.rules.get(rule, self.mean)

    def get_id(self, rule:str)->str:
        return self.reaction_ids.get(rule)


BIAS = 1e-8
def get_gene_expression(
        parser:ExpressionParser,
        model:SBMLModel,
        fpkm:pl.DataFrame
)->GenMetab:
    """
    Input:
        model (cobra.Model): Metabolic model.
        fpkmDic (dict): Dictionary with gene expression values.
    
    Output:
        tuple: Median value of gene expressions, and list of gene expressions for metabolic reactions.
    """
    g_metab = {} # gene expression of reactions partakin in the
    # metabolism
    #parser = ExpressionParser()
    rules_cache = {}
    genes_values = {}
    booleans = {}
    reaction_ids = {}

   
    
    for i, reaction in enumerate(model.reactions):
        ##########################################################
        ## Gets the GPR and a boolean list with known or unknown genes
        rule = reaction.gene_reaction_rule.strip()
        if rule!='':
            reaction_ids[rule] = reaction
            check_bool = rules_cache.get(rule, False)

            if not check_bool:
                tokens = parser.tokenize(rule)
                rule_booleans = boolean_vector_rule(tokens, fpkm)
                booleans[rule] = rule_booleans
                rules_cache[rule] = all(rule_booleans.values()) and len(rule_booleans)>0
            ##########################################################
            ## Gets the expression value 'g'
            ## for every exists rule, add g
            check_bool = rules_cache.get(rule, False)
            if check_bool: # get 'g' for reaction with GPR.
                if rule not in genes_values:
                    rule_tree = parser.parse(rule)
                    g = get_expression_value(rule_tree, fpkm)
                    genes_values[rule] = g
                else:
                    g = genes_values[rule]
                g_metab[rule]=g+BIAS
    return GenMetab(reaction_ids, g_metab, booleans)
