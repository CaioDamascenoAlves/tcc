"""
Drive Data Loader: carrega dados do Google Drive.

Substitui carregamento de arquivos locais por download do Google Drive.
Cache local para evitar downloads repetidos.
"""

import pandas as pd
import json
import requests
from pathlib import Path
from typing import Dict, Optional
import hashlib
import os


class DriveDataLoader:
    """
    Carregador de dados do Google Drive com cache local.
    
    Usa o arquivo drive_files.json para mapear caminhos para URLs do Drive.
    Mantém cache local em .cache/ para evitar downloads repetidos.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Tenta encontrar raiz do projeto (onde está drive_files.json)
            current = Path(__file__).parent
            while current != current.parent:
                if (current / 'drive_files.json').exists():
                    project_root = current
                    break
                current = current.parent
            
            if project_root is None:
                raise FileNotFoundError(
                    "Não foi possível encontrar drive_files.json. "
                    "Execute upload_to_drive.py primeiro."
                )
        
        self.project_root = Path(project_root)
        self.cache_dir = self.project_root / '.cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Carrega mapeamento
        mapping_file = self.project_root / 'drive_files.json'
        if not mapping_file.exists():
            raise FileNotFoundError(
                f"{mapping_file} não encontrado! "
                "Execute upload_to_drive.py para criar o mapeamento."
            )
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            self.drive_mapping = json.load(f)
    
    def _get_cache_path(self, relative_path: str) -> Path:
        """Retorna caminho do arquivo em cache."""
        # Usa hash do caminho para evitar problemas com diretórios
        path_hash = hashlib.md5(relative_path.encode()).hexdigest()
        cache_file = self.cache_dir / f"{path_hash}.csv"
        return cache_file
    
    def _download_file(self, url: str, cache_path: Path) -> None:
        """Baixa arquivo do Google Drive."""
        print(f"Baixando do Drive: {cache_path.name}...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salva em cache
        with open(cache_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Download completo")
    
    def load_csv(self, relative_path: str, force_download: bool = False) -> pd.DataFrame:
        """
        Carrega CSV do Google Drive (com cache).
        
        Args:
            relative_path: Caminho relativo ao results/ (ex: 'networks/swimming_men.csv')
            force_download: Se True, força novo download ignorando cache
        
        Returns:
            DataFrame do pandas
        """
        # Normaliza path (Windows vs Linux)
        relative_path = relative_path.replace('\\', '/')
        
        if relative_path not in self.drive_mapping:
            raise FileNotFoundError(
                f"Arquivo '{relative_path}' não encontrado no mapeamento do Drive.\n"
                f"Arquivos disponíveis:\n" + 
                "\n".join(f"  - {p}" for p in sorted(self.drive_mapping.keys()))
            )
        
        cache_path = self._get_cache_path(relative_path)
        
        # Verifica se precisa baixar
        if force_download or not cache_path.exists():
            url = self.drive_mapping[relative_path]['download_url']
            self._download_file(url, cache_path)
        
        # Carrega do cache
        return pd.read_csv(cache_path)
    
    def clear_cache(self) -> None:
        """Remove todos os arquivos em cache."""
        for file in self.cache_dir.glob('*.csv'):
            file.unlink()
        print(f"Cache limpo ({self.cache_dir})")
    
    def get_available_files(self) -> list:
        """Retorna lista de arquivos disponíveis no Drive."""
        return sorted(self.drive_mapping.keys())
    
    def get_file_info(self, relative_path: str) -> Dict:
        """Retorna informações sobre um arquivo."""
        relative_path = relative_path.replace('\\', '/')
        return self.drive_mapping.get(relative_path)


# Exemplo de uso
if __name__ == '__main__':
    # Teste básico
    loader = DriveDataLoader()
    
    print("Arquivos disponíveis:")
    for file in loader.get_available_files()[:5]:
        print(f"  - {file}")
    
    # Testa carregamento
    print("\nTestando carregamento...")
    df = loader.load_csv('networks/consolidated_athletes.csv')
    print(f"Carregado: {len(df)} linhas, {len(df.columns)} colunas")
