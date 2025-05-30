import pandas as pd
import os
import unicodedata
import re

def remove_accents(text):
    """Quita tildes y signos diacríticos."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(text))
        if not unicodedata.combining(c)
    )

def normalize_text(s):
    """
    Elimina acentos, pasa a minúsculas, reemplaza todo no letra/dígito por espacio
    y colapsa espacios múltiples.
    """
    s = remove_accents(s).lower()
    s = re.sub(r'[^a-z0-9]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def pregunta_01():
    # 1. Leer CSV y descartar la columna índice
    df = pd.read_csv(
        'files/input/solicitudes_de_credito.csv',
        sep=';',
        index_col=0
    )

    # 2. Normalizar nombres de columna
    df.columns = (
        df.columns
          .map(remove_accents)
          .str.lower()
          .str.strip()
          .str.replace(' ', '_')
          .str.replace('-', '_')
    )

    # 3. Normalizar texto en columnas clave
    text_cols = [
        'sexo',
        'tipo_de_emprendimiento',
        'idea_negocio',
        'barrio',
        'linea_credito'
    ]
    for col in text_cols:
        df[col] = df[col].astype(str).map(normalize_text)

    # 4. Filtrar registros inválidos o vacíos
    df = df[
        df['barrio'].ne('') &
        df['barrio'].ne('nan') &
        df['sexo'].isin(['masculino', 'femenino']) &
        df['tipo_de_emprendimiento'].isin([
            'comercio', 'servicio',
            'industria', 'agropecuaria'
        ])
    ]

    # 5. Parseo flexible de fechas
    fechas = pd.to_datetime(
        df['fecha_de_beneficio'],
        dayfirst=True,
        errors='coerce'
    )
    mask_na = fechas.isna()
    fechas2 = pd.to_datetime(
        df.loc[mask_na, 'fecha_de_beneficio'],
        dayfirst=False,
        errors='coerce'
    )
    fechas[mask_na] = fechas2
    df['fecha_de_beneficio'] = fechas
    df = df.dropna(subset=['fecha_de_beneficio'])

    # 6. Limpieza y conversión de monto
    df['monto_del_credito'] = (
        df['monto_del_credito']
          .astype(str)
          .str.replace(r'[\$\s,]', '', regex=True)
    )
    df['monto_del_credito'] = pd.to_numeric(
        df['monto_del_credito'],
        errors='coerce'
    )
    df = df.dropna(subset=['monto_del_credito'])

    # 7. Eliminar duplicados
    df = df.drop_duplicates()

    # 8. Guardar resultado sin índice
    os.makedirs('files/output', exist_ok=True)
    df.to_csv(
        'files/output/solicitudes_de_credito.csv',
        sep=';',
        index=False
    )

if __name__ == '__main__':
    pregunta_01()
