from pathlib import Path

from pydantic import BaseModel
from pydantic import validator
from pydantic.dataclasses import dataclass

from typing import ClassVar, List, TypeVar, Optional,Any
from cobra.core.model import Model as SBMLModel
import polars as pl
import cobra
from concurrent.futures import ThreadPoolExecutor, as_completed

# Organism->Condition
@dataclass(config=dict(arbitrary_types_allowed=True))
class OrganismItem:
    organism: str
    condition:str
    gene_exp_file:Path
    medium:Path
    network:Path

    gene_exp_data: Optional[pl.DataFrame] = None
    medium_data: Optional[pl.DataFrame] = None
    network_data: Optional[SBMLModel] = None  # Assuming SBML data as cobra.Model

    allowed_gene_exp_extensions: ClassVar[List[str]] = ['.csv', '.txt']
    allowed_medium_extensions: ClassVar[List[str]] = ['.csv']
    allowed_network_extensions: ClassVar[List[str]] = ['.xml']


    def activate(self):
        # Start reading files in parallel
        self.future_to_file = {
            'gene_exp_file': None,
            'medium': None,
            'network': None
        }
        with ThreadPoolExecutor() as executor:
            self.future_to_file['gene_exp_file'] = executor.submit(self.read_gene_file)
            self.future_to_file['medium'] = executor.submit(self.read_medium_file)
            self.future_to_file['network'] = executor.submit(self.read_network_file)
        
        self.wait_for_files()


    def wait_for_files(self):
        """
        Espera hasta que todos los archivos hayan sido leídos.
        """
        for file_type, future in self.future_to_file.items():
            try:
                data = future.result()
                if file_type == 'gene_exp_file':
                    self.gene_exp_data = data
                elif file_type == 'medium':
                    self.medium_data = data
                elif file_type == 'network':
                    self.network_data = data
            except Exception as exc:
                print(f"{file_type} generated an exception: {exc}")

    @validator('gene_exp_file')
    def check_gene_exp_file(cls, value: Path) -> Path:
        if value.suffix not in cls.allowed_gene_exp_extensions:
            raise ValueError(f'gene_exp_file must have one of the following extensions: {cls.allowed_gene_exp_extensions}')
        if not value.exists():
            raise ValueError(f'gene_exp_file path does not exist: {value}')
        return value
    @validator('medium')
    def check_medium(cls, value: Path) -> Path:
        if value.suffix not in cls.allowed_medium_extensions:
            raise ValueError(f'medium must have one of the following extensions: {cls.allowed_medium_extensions}')
        if not value.exists():
            raise ValueError(f'medium path does not exist: {value}')
        return value

    @validator('network')
    def check_network(cls, value: Path) -> Path:
        if value.suffix not in cls.allowed_network_extensions:
            raise ValueError(f'network must have one of the following extensions: {cls.allowed_network_extensions}')
        if not value.exists():
            raise ValueError(f'network path does not exist: {value}')
        return value


    def read_gene_file(self) -> pl.DataFrame|None:
        """
        Lee el archivo gene_exp_file basado en su extensión y retorna un DataFrame de Polars.
        """
        try:
            if self.gene_exp_file.suffix in self.allowed_gene_exp_extensions:
                df = pl.read_csv(self.gene_exp_file, separator='\t')
                return df
        except Exception as e:
            print(f"Error al leer gene_exp_file: {e}")
        return None

    def read_medium_file(self) -> pl.DataFrame|None:
        """
        Lee el archivo medium basado en su extensión y retorna un DataFrame de Polars.
        """
        try:
            if self.medium.suffix in self.allowed_medium_extensions:
                df = pl.read_csv(self.medium, separator='\t')
                return df
        except Exception as e:
            print(f"Error al leer medium: {e}")
        return None

    def read_network_file(self) -> SBMLModel|None:
        """
        Lee el archivo network basado en su extensión y retorna un objeto cobra.Model.
        """
        try:
            if self.network.suffix in self.allowed_network_extensions:
                model = cobra.io.read_sbml_model(self.network)
                return model
        except Exception as e:
            print(f"Error al leer network: {e}")
        return None
