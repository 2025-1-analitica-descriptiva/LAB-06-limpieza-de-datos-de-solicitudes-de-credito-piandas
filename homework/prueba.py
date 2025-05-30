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
    - Elimina acentos.
    - Pasa a minúsculas.
    - Reemplaza todo no letra/dígito por espacio.
    - Colapsa espacios múltiples.
    """
    s = remove_accents(s).lower()
    s = re.sub(r'[^a-z0-9]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def pregunta_01():
    # 1. Leer CSV y descartar la primera columna índice
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

    # 3. Normalizar texto (quita puntuación y unifica espacios) en columnas clave
    text_cols = ['sexo', 'tipo_de_emprendimiento', 'idea_negocio', 'barrio', 'linea_credito']

    for col in text_cols:
        df[col] = df[col].astype(str).map(normalize_text)

    df['barrio'] = df['barrio'].astype(str).map(normalize_text)

    # 3.1 Extraer el nombre base del barrio antes de " no"
    df = df[df['barrio'] != '']
    df = df[df['barrio'] != 'nan']
    
    # 4. Filtrar sólo las categorías válidas
    df = df[df['sexo'].isin(['masculino', 'femenino'])]
    df = df[df['tipo_de_emprendimiento'].isin([
        'comercio', 'servicio', 'industria', 'agropecuaria'
    ])]
    df = df[
        df['barrio'].notna()
    ]

    # 5. Parseo flexible de fecha (día/mes primero, luego mes/día)
    fechas = pd.to_datetime(df['fecha_de_beneficio'], dayfirst=True, errors='coerce')
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
    df['monto_del_credito'] = pd.to_numeric(df['monto_del_credito'], errors='coerce')
    df = df.dropna(subset=['monto_del_credito'])

    # 7. Eliminar duplicados al final (ya todo está limpio)
    df = df.drop_duplicates()


    # --- DEBUG: comparar conteos reales vs. esperados ---
    expected = {
        'sexo': [6617, 3589],
        'tipo_de_emprendimiento': [5636, 2205, 2201, 164],
        'idea_negocio': [
            1844, 1671, 983, 955, 584, 584, 273, 216, 164, 160,
            # … puedes listar solo los primeros 10 si es muy largo
        ],
        'barrio_top20': [990, 483, 423, 383, 376, 372, 361, 348, 328, 308,
                         270, 255, 255, 247, 234, 232, 231, 202, 174, 170]
    }

    actual = {
        'sexo': df['sexo'].value_counts().to_list(),
        'tipo_de_emprendimiento': df['tipo_de_emprendimiento'].value_counts().to_list(),
        'idea_negocio': df['idea_negocio'].value_counts().to_list()[:10],
        'barrio_top20': df['barrio'].value_counts().to_list()[:20]
    }

    for key in expected:
        exp = expected[key]
        act = actual[key]
        mismatches = [(i, act[i], exp[i]) for i in range(min(len(act), len(exp))) if act[i] != exp[i]]
        print(f"DEBUG {key}:")
        print("  Expected:", exp)
        print("  Actual:  ", act)
        if mismatches:
            print("  Mismatches at positions:", mismatches)
        else:
            print("  ✅ Matches expected up to compared length.")
        print()

    # 9. Guardar SIN índice para evitar 'Unnamed: 0'
    os.makedirs('files/output', exist_ok=True)
    df.to_csv(
        'files/output/solicitudes_de_credito.csv',
        sep=';',
        index=False
    )

if __name__ == '__main__':
    pregunta_01()