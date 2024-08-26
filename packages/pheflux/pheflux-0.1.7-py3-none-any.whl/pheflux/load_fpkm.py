##############################################################################
### Loading FPKM data
"""
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
"""

import polars as pl

def load_fpkm(
    fpkm:pl.DataFrame,
):

    
    fpkm = fpkm.with_columns(
        pl.col("Gene_ID").map_elements(
            lambda x: f"G_{x}", return_dtype=pl.Utf8).alias("Gene_ID")
    )
    
    fpkm = fpkm.unique(subset=["Gene_ID"], keep='last')
    
    expression = "Expression"

    
    percentile_95 = fpkm[expression].quantile(0.95)
    #filtered_df = fpkm.filter(pl.col(expression) <= percentile_95)

    filtered_df = fpkm.with_columns(
        pl.col(expression).map_elements(lambda x: min(x, percentile_95),
                                        return_dtype=pl.Float64
                                        ).alias(expression)
    )    

    return filtered_df
