import pandas as pd
import polars as pl

#################################################################################
### Table of times and variable numbers for networks
def record_table(record ,condition, lbx, ubx, time, status):   
    """
    Input:
        record (DataFrame): DataFrame with records of previous runs.
        condition (str): Condition name.
        lbx (list): List of lower bounds.
        ubx (list): List of upper bounds.
        time (float): Total time of the run.
        status (str): Status of the run.
    
    Output:
        DataFrame: Updated record DataFrame.
    """
    variables = 0
    for i in range(len(lbx)):
        if lbx[i] != ubx[i]:
            variables += 1
    
    if record.shape == (0,0):
        record = pl.DataFrame(schema={'Condition':str, 'N° variables':int, 'Time':float, 'Status':str})

    item = {
        "Condition":condition,
        "N° variables":variables,
        "Time":time,
        "Status":status
    }
    new_record = pl.DataFrame(item)
    record = pl.concat([record, new_record])
    return record
