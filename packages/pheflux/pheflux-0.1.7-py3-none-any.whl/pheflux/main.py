# from std
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime,timezone
from typing import Optional
import random
import string
import time
import zipfile

# contrib
import polars as pl
import pandas as pd
import numpy as np
import typer
from rich import print
import ujson as json

# local
from pheflux.item import OrganismItem
from pheflux.measure_time import MeasureTime
from pheflux.read_settings import read_file, Settings
from pheflux.utils import actual_time
from pheflux.load_fpkm import load_fpkm
from pheflux.reload_fpkmh_sapiens import reload_fpkmh_sapiens
from pheflux.update_model import update_model
from pheflux.opt_phe_flux import opt_phe_flux
from pheflux.save_rules import save_rules
from pheflux.record import record_table

app = typer.Typer()

#################################################################################
########################             PHEFLUX             ########################
#################################################################################
"""
"""

@dataclass
class ResultItem:
    organism:str
    condition:str
    csv_file:Path|None = None

    def set_csv(self, csv_file:Path):
        if csv_file.exists():
            self.csv_file = csv_file

@dataclass
class ResultGroup:
    name:str
    log:Path 
    results:list[ResultItem] = field(default_factory=list)
    report:dict[str, float] = field(default_factory=dict)
    
    def add(self, item:ResultItem):
        self.results.append(item)


    def set_report(self, report:dict[str, float]):
        self.report = report
        

    def generate_zip(self, output_zip: Path):

        now = datetime.now(timezone.utc).isoformat()
        
        if not output_zip.is_dir():
            output_zip = output_zip.parent
        output_zip.mkdir(exist_ok=True, parents=True)
            

        output_zip = output_zip / f"{self.name}_{now}.zip"
        print(f"Zip output: {output_zip}")
        
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            # Add log file to the zip
            if self.log.exists():
                zipf.write(self.log, arcname=self.log.name)
            
            # Add each csv_file from ResultItem to the zip
            for result_item in self.results:
                if result_item.csv_file and result_item.csv_file.exists():
                    zipf.write(result_item.csv_file, arcname=result_item.csv_file.name)
            
            # Create a JSON file for the report and add it to the zip
            report_json_path = Path('report_time.json')
            with report_json_path.open('w') as json_file:
                json.dump(self.report, json_file)
            zipf.write(report_json_path, arcname=report_json_path.name)
            
            # Clean up the temporary report JSON
            report_json_path.unlink(missing_ok=True)
        return output_zip

    
def get_fluxes(
        settings:Settings, task_name:str=""
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
    prefix_log = 'log'
    
    fluxes = None
    process_start = time.time()
    shuffle=False
    shuffled_fpkm = pl.DataFrame()
    record = pl.DataFrame()

    opt_time, t_time = [], []
    code = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(4)).upper()
    
    recordFile = Path(f"{processDir}/{prefix_log}_record_{code}.log.csv")
    
    results_group = ResultGroup(task_name, recordFile)
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

        result_item = ResultItem(organism, condition)
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

        fluxes,optimization_time,total_time,status,success,lbx,ubx = opt_phe_flux(
            model,
            fpkm_filtered,
            init_time,
            k)

        ##############################################################
        # Save results: fluxes and summary table
        print(" ")
        if settings.verbosity:
            atime = actual_time()
            print(atime, "Saving metabolic fluxes...")
        # fluxes
        resultsFile = Path(f"{processDir}/{organism}_{condition}_{status}.fluxes.csv")
        result_item.set_csv(resultsFile)
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
        results_group.add(result_item)


    ##############################################################
    # Save summary table
    
    # create directory if necessary
    processPath = Path(processDir)
    processPath.mkdir(exist_ok=True, parents=True)
    record.write_csv(recordFile, separator=';')

    process_end = time.time()

    measure_time = MeasureTime(
        start_time=process_start,
        end_time=process_end,
        opt_time=opt_time,
        t_time=t_time
    )
    report_json = measure_time.generate_report()
    results_group.set_report(report_json)
    return fluxes, report_json, results_group



@app.command()
def run(settings_path:Path):
    if settings_path.exists():
        settings = read_file(settings_path)
        print(settings)
        fluxes, report, results = get_fluxes(settings, "test_pheflux")
        print(report)
        print(results)
        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True, parents=True)
        results.generate_zip(out_dir)
    else:
        print(f"The settings path doesn't exists {settings_path}")

if __name__=="__main__":
    app()
