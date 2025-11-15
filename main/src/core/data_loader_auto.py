"""
Data Loader Automático: detecta se usa arquivos locais ou Google Drive.

Compatível com desenvolvimento local E produção no Streamlit Cloud.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import sys


def is_streamlit_cloud() -> bool:
    """Detecta se está rodando no Streamlit Cloud."""
    # Streamlit Cloud tem variáveis de ambiente específicas
    import os
    return (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('HOSTNAME', '').startswith('streamlit') or
        'streamlit' in os.getenv('HOME', '').lower()
    )


class AutoDataLoader:
    """
    Carregador de dados que se adapta ao ambiente:
    - Local: Usa arquivos em results/
    - Streamlit Cloud: Baixa do Google Drive
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Tenta encontrar raiz do projeto
            current = Path(__file__).parent
            while current != current.parent:
                if (current / 'results').exists() or (current / 'drive_files.json').exists():
                    project_root = current
                    break
                current = current.parent
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.use_drive = is_streamlit_cloud() or not (self.project_root / 'results').exists()
        
        if self.use_drive:
            print("Modo: Google Drive (Streamlit Cloud)")
            from core.drive_loader import DriveDataLoader
            self.loader = DriveDataLoader(self.project_root)
        else:
            print("Modo: Arquivos Locais")
            self.results_dir = self.project_root / 'results'
    
    def load_csv(self, relative_path: str) -> pd.DataFrame:
        """
        Carrega CSV automaticamente (local ou Drive).
        
        Args:
            relative_path: Caminho relativo ao results/ (ex: 'networks/swimming_men.csv')
        
        Returns:
            DataFrame do pandas
        """
        if self.use_drive:
            return self.loader.load_csv(relative_path)
        else:
            full_path = self.results_dir / relative_path
            if not full_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {full_path}")
            return pd.read_csv(full_path)
    
    def get_available_files(self) -> list:
        """Retorna lista de arquivos disponíveis."""
        if self.use_drive:
            return self.loader.get_available_files()
        else:
            import os
            files = []
            for root, dirs, filenames in os.walk(self.results_dir):
                for filename in filenames:
                    if filename.endswith('.csv'):
                        full_path = Path(root) / filename
                        relative = full_path.relative_to(self.results_dir)
                        files.append(str(relative).replace('\\', '/'))
            return sorted(files)


# Singleton global
_global_loader = None


def get_data_loader(project_root: Optional[Path] = None) -> AutoDataLoader:
    """Retorna instância singleton do data loader."""
    global _global_loader
    if _global_loader is None:
        _global_loader = AutoDataLoader(project_root)
    return _global_loader


# Exemplo de uso
if __name__ == '__main__':
    loader = get_data_loader()
    
    print(f"\nModo: {'Drive' if loader.use_drive else 'Local'}")
    print(f"\nArquivos disponíveis (primeiros 10):")
    for file in loader.get_available_files()[:10]:
        print(f"  - {file}")
