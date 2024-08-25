import polars as pl
import ply.lex as lex

def boolean_vector_rule(
        tokens:list[lex.LexToken],
        fpkm:pl.DataFrame
)->list[bool]:
    """
    Input:
        rule (str): Gene-protein rule as a string.
        fpkmDic (dict): Dictionary with gene expression values.
    
    Output:
        list: List of boolean values indicating if the FPKM values for the genes are known.
    """
    try:
        # set(tokens) saves repetition 
        genes_bools = {}
        gen_tokens = {t for t in tokens if t.type=="GENE"}
        for token in gen_tokens:
            key = f"G_{token.value.upper()}"
            genes_bools[key] = fpkm["Gene_ID"].is_in([key]).any() 
        return genes_bools
    except Exception as e:
        raise e
