import polars as pl
from collections import namedtuple
from rich import print

"""
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

"""

HumanGene = namedtuple("HumanGene", ["hid", "Gene_ID"])


def reload_fpkmh_sapiens(
        fpkm:pl.DataFrame, 
        model:pl.DataFrame):
    """
    Match genes that exists on 'fpkm'

    caso excepcional
    """
    genes = [HumanGene(f"G_{gene.id}", f"G_{gene.name}") for gene in model.genes]
    hg_dataframe = pl.DataFrame(genes)
    joined_df = fpkm.join(hg_dataframe, on="Gene_ID", how="inner")
    df = joined_df.drop('Gene_ID')
    df = df.rename({"hid":"Gene_ID"})
    return df
