# from stc
from pathlib import Path
import time

# contrib
import numpy as np
import typer
from rich import print
import polars as pl

# local
from item import OrganismItem
from measure_time import MeasureTime
from read_settings import read_file, Settings
from utils import actual_time
from load_fpkm import load_fpkm
from reload_fpkmh_sapiens import reload_fpkmh_sapiens
from update_model import update_model
from opt_phe_flux import opt_phe_flux
from save_rules import save_rules
from record import record_table
import pandas as pd
import random
import string
import ujson
app = typer.Typer()

#################################################################################
########################             PHEFLUX             ########################
#################################################################################
"""
def getFluxes(
        inputFileName: Path, 
        processDir: str, 
        prefix_log: str, 
        verbosity: bool)->list[Pheflux]:
    processStart = time.time()
    # Table of results
    record = pd.DataFrame()
    shuffle=False
    shuffledFPKM = pd.DataFrame()
    #################################################################################
    ### Load "InputData" file
    inputData=pd.read_csv(inputFileName,sep="\t", lineterminator='\n', na_filter=False)
    nRows,nCols=inputData.shape

    shuffle=False
    opt_time, t_time = [], []
    for i in range(nRows):
        ##############################################################
        ## Load information from InputData
        condition    = inputData.loc[i]["Condition"]
        geneExpFile  = inputData.loc[i]["GeneExpFile"]
        mediumFile   = inputData.loc[i]["Medium"]
        network      = inputData.loc[i]["Network"]
        organism     = inputData.loc[i]["Organism"]

        ##############################################################
        ## Messages in terminal
        atime = actuallyTime()
        print (atime, 'Condition ejecuted:', organism, '-', condition)

        ##############################################################
        # Metabolic network
        if verbosity:
            atime = actuallyTime()
            print (atime,"Loading metabolic model:", network.split("/")[-1].split(".")[0])
        model_default = cobra.io.read_sbml_model(network)
        fpkm = pd.read_csv(geneExpFile,sep="\t", lineterminator='\n')

        init_time = time.time()
        ##############################################################
        # FPKM data
        if verbosity:
            atime = actuallyTime()
            print(atime, "Loading transcriptomic data...")
        # Load FPKM data
        fpkmDic,shuffledFPKM = loadFPKM(fpkm,condition,shuffle,shuffledFPKM)
        # Reload FPKM data for Hsapiens and load culture medium
        if organism == 'Homo_sapiens':
            fpkmDic = reloadFPKMHsapiens(fpkmDic, model_default)

        ##############################################################
        # Update model: Add R_, open bounds, and set carbon source
        if verbosity:
            atime = actuallyTime()
            print(atime, "Updating metabolic model...")
        model = updateModel(model_default,mediumFile)

        ##############################################################
        # Compute flux predictions
        if verbosity:
            atime = actuallyTime()
            print(atime, "Running pheflux...")
        k = 1000
        fluxes,optimization_time,total_time,status,success,lbx,ubx = optPheFlux(model,fpkmDic,k,init_time)

        ##############################################################
        # Save results: fluxes and summary table
        print(" ")
        if verbosity:
            atime = actuallyTime()
            print(atime, "Saving metabolic fluxes...")
        # fluxes
        resultsFile = processDir+'/'+organism+"_"+condition+'_'+status+'.fluxes.csv'
        fluxes.to_csv(resultsFile, sep='\t')
        # summary table
        record = recordTable(record,condition,lbx,ubx,total_time,status)
        
        ##############################################################
        ## Messages in terminal
        opt_time.append(optimization_time)
        t_time.append(total_time)
        atime = actuallyTime()
        print(atime, organism, '-', condition, "... is processed.")

        print ('\n',' o '.center(80, '='),'\n')

    ##############################################################
    # Save summary table
    code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(4))
    recordFile = processDir+'/'+prefix_log+'_record_'+code.upper()+'.log.csv'
    record.to_csv(recordFile, sep='\t', index=False)

    #########################################################################################
    processFinish = time.time()
    processTime = processFinish - processStart
    print ('Average time per optimization:', np.mean(opt_time), 's')
    print ('Average time per condition:', np.mean(t_time), 's')
    print ('Total process time:', processTime/60, 'min', '--> ~', (processTime/3600), 'h')
    
    return fluxes

"""

def get_fluxes(
        settings:Settings
):
    """
    Input:
        inputFileName (str): File name with input data.
        processDir (str): Directory for saving process files.
        prefix_log (str): Prefix for log files.
        verbosity (bool): Flag to control verbosity of the process.
    
    Output:
        Series: Series with fluxes.
    """
    processDir = "process"

    fluxes = None
    process_start = time.time()
    shuffle=False
    shuffled_fpkm = pl.DataFrame()
    record = pl.DataFrame()

    opt_time, t_time = [], []

    # operate this
    for item in settings.organisms:
        item.activate()
        condition    = item.condition
        prefix_log   = str(condition) 

        geneExpFile  = item.gene_exp_file
        mediumFile   = item.medium
        medium_data  = item.medium_data
        network      = item.network
        organism     = item.organism

        ##############################################################
        ## Messages in terminal
        atime = actual_time()
        print(atime, 'Condition ejecuted:', organism, '-', condition)
        ##############################################################
        # Metabolic network
        if settings.verbosity:
            atime = actual_time()
            print (atime,"Loading metabolic model:", network.stem)
        model_default = item.network_data
        fpkm = item.gene_exp_data

        print("Model")
        print(model_default)
        print("____")
        init_time = time.time()
        ##############################################################
        # FPKM data
        if settings.verbosity:
            atime = actual_time()
            print(atime, "Loading transcriptomic data...")
        # Load FPKM data
        # fpkmDic,shuffled_fpkm = load_fpkm(
        #     fpkm,
        #     condition,
        #     shuffle,
        #     shuffled_fpkm)
        fpkm_filtered = load_fpkm(fpkm)


        # # Reload FPKM data for Hsapiens and load culture medium
        # if organism == 'Homo_sapiens':
        #     fpkmDic = reloadFPKMHsapiens(fpkmDic, model_default)
        if organism.lower() == 'homo_sapiens':
            fpkm_filtered = reload_fpkmh_sapiens(fpkm_filtered, model_default)
            print(fpkm_filtered)

        ##############################################################
        # Update model: Add R_, open bounds, and set carbon source
        if settings.verbosity:
            atime = actual_time()
            print(atime, "Updating metabolic model...")
        model = update_model(model_default, medium_data)


        ##############################################################
        # Compute flux predictions
        if settings.verbosity:
            atime = actual_time()
            print(atime, "Running pheflux...")
        k = 1000

        # in case to save rules to create some tests:
        #save_rules(model, organism)
        # checked here()

        fluxes,optimization_time,total_time,status,success,lbx,ubx = opt_phe_flux(model,fpkm_filtered,init_time, k)

        ##############################################################
        # Save results: fluxes and summary table
        print(" ")
        if settings.verbosity:
            atime = actual_time()
            print(atime, "Saving metabolic fluxes...")
        # fluxes
        resultsFile = f"{processDir}/{organism}_{condition}_{status}.fluxes.csv"
        fluxes.write_csv(resultsFile, separator=';')
        # summary table
        record = record_table(record,condition,lbx,ubx,total_time,status)
        
        ##############################################################
        ## Messages in terminal
        opt_time.append(optimization_time)
        t_time.append(total_time)
        atime = actual_time()
        print(atime, organism, '-', condition, "... is processed.")

        print ('\n',' o '.center(80, '='),'\n')



    ##############################################################
    # Save summary table
    code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(4)).upper()
    recordFile = f"{processDir}/{prefix_log}_record_{code}.log.csv"
    record.write_csv(recordFile, separator=';')

    process_end = time.time()

    measure_time = MeasureTime(
        start_time=process_start,
        end_time=process_end,
        opt_time=opt_time,
        t_time=t_time
    )
    report_json = measure_time.generate_report()
    print(report_json)

    return fluxes, report_json



@app.command()
def run(settings_path:Path):
    if settings_path.exists():
        settings = read_file(settings_path)
        print(settings)
        get_fluxes(settings)
    else:
        print(f"The settings path doesn't exists {settings_path}")

if __name__=="__main__":
    app()
