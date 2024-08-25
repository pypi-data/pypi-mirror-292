import tomllib
import yaml
from typing import Union, Any, Dict, List
from pathlib import Path
# local
from pheflux.item import OrganismItem
from pydantic import BaseModel, validator

class Settings(BaseModel):
    name: str
    author: str
    verbosity: bool    
    organisms: List[OrganismItem]


PATH_FIELDS = {"gene_exp_file","medium","network"}

def set_paths(base_path, item:Dict[str,str]):
    for field in PATH_FIELDS:
        value = item[field]
        item[field] = f"{base_path}/{value}"
    return item 

def read_file(file_path: Path) -> Settings|None:
    """
    Lee configuraciones desde un archivo TOML o YAML.
    
    :param file_path: Ruta del archivo de configuración como una instancia de Path.
    :return: Diccionario con las configuraciones, o None si no se pudo leer el archivo.
    """
    try:
        base_path = file_path.parent.parent.resolve()        
        if file_path.suffix == '.toml':
            with file_path.open('rb') as file:
                settings_dict = tomllib.load(file)
                result = [set_paths(base_path, r) for r in settings_dict.pop("input_data")]
                return Settings(organisms=[OrganismItem(**item) for
                                           item in result], **settings_dict)
        elif file_path.suffix in {'.yaml', '.yml'}:
            with file_path.open('r') as file:
                settings_dict = yaml.safe_load(file)
                result = [set_paths(base_path, r) for r in settings_dict.pop("input_data")]
                return Settings(organisms=[OrganismItem(**item) for
                                           item in result], **settings_dict)
        else:
            print("Formato de archivo no soportado. Use un archivo .toml o .yaml/.yml.")
            return None
    except (FileNotFoundError, yaml.YAMLError, tomllib.TOMLDecodeError) as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return None

