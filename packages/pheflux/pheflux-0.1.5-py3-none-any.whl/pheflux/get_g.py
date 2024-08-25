import polars as pl
import ply.yacc as yacc
from gene_rule_parser import (
    ExpressionParser, 
    tree_analysis, 
    Gene, 
    distribute_rules)

##############################################################################
### Obtains expression value 'g' for each reaction, based on the gene-protein-rule
def get_expression_value(
        tree:yacc.LRParser,
        fpkm:pl.DataFrame)->float:

    """
    Input:
        tree (str): Gene-protein tree parsed.
        fpkmDic (dict): Dictionary with gene expression values.
    
    Output:
        float: Sum of minimum expression values for each subrule in the gene-protein rule.
    """
    return tree_analysis(tree, fpkm)
