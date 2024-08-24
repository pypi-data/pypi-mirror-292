from cobra.core.model import Model as SBMLModel
import json
from pathlib import Path

BASE  = Path(__file__).parent.parent.resolve() 

def save_rules(model:SBMLModel, name:str):
    rules = set()
    for i, reaction in enumerate(model.reactions):
        rule = reaction.gene_reaction_rule.strip()
        rules.add(rule)

    txt = json.dumps(list(rules))
    p = BASE / f"{name}_rules.json"
    p.write_text(txt)
