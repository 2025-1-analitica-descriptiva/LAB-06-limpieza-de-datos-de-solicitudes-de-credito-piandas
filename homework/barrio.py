import pandas as pd
import unicodedata
import re
from difflib import get_close_matches

# --- Funciones de limpieza y normalización ---
def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', str(text))
        if not unicodedata.combining(c)
    )

def normalize_text(s):
    s = remove_accents(s).lower()
    s = re.sub(r'[^a-z0-9]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def clean_barrio(s):
    if pd.isna(s):
        return None
    orig = str(s)
    s = normalize_text(orig)
    s = re.sub(r'\bbarrio\b', '', s)
    s = re.sub(r'\bno\.?\s*\d+\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    cleaned = s or None
    return cleaned

# --- Lista CANONICAL (incluye los más frecuentes no mapeados) ---
CANONICAL = [
    'robledo', 'manrique central', 'san javier', 'aranjuez',
    'buenos aires', 'belen', 'popular', 'cabecera san cristobal',
    'castilla', 'enciso', 'santa cruz', 'campo valdes',
    'santo domingo savio', 'cabecera san antonio', 'caicedo',
    'manrique oriental', 'doce de octubre', 'la milagrosa',
    'moravia', 'villa hermosa',
    'el salvador', 'andalucia', 'pedregal', 'guayabal', '20 de julio',
    'belencito',      # +96
    'la floresta',    # +95
    'playon de los',  # +89
    'granizal'        # +83
]


def match_barrio(name):
    if pd.isna(name):
        return None
    nm = normalize_text(name)
    tokens = set(nm.split())

    # Preparar tokens de cada canonical
    canon_tokens = [set(normalize_text(c).split()) for c in CANONICAL]

    # 1) token subset: si todos los tokens del canonical están en el nombre
    for canon, ctoks in zip(CANONICAL, canon_tokens):
        if ctoks and ctoks.issubset(tokens):
            return canon

    # 2) match parcial por proporción de tokens compartidos
    best, best_score = name, 0
    for canon, ctoks in zip(CANONICAL, canon_tokens):
        shared = len(tokens & ctoks)
        score = shared / len(ctoks) if ctoks else 0
        if score > best_score:
            best_score, best = score, canon
    if best_score >= 0.6:
        return best

    # 3) si no hay match suficiente, dejamos el original
    return name
# --- Cargar y procesar barrio ---
df = pd.read_csv('files/input/solicitudes_de_credito.csv', sep=';', index_col=0)

df['barrio'] = df['barrio'].apply(clean_barrio)
print("\nDEBUG top-20 barrios limpios (antes de mapear):")
print(df['barrio'].value_counts().head(20).to_dict())
df['barrio_limpio'] = df['barrio']
df['barrio_mapeado'] = df['barrio_limpio'].map(match_barrio)

# --- Comparación con los conteos esperados ---
expected_top20 = [990, 483, 423, 383, 376, 372, 361, 348, 328, 308,
                  270, 255, 255, 247, 234, 232, 231, 202, 174, 170]

actual_top20 = df['barrio_mapeado'] \
    .value_counts() \
    .reindex(CANONICAL, fill_value=0) \
    .tolist()[:20]

print("\nDEBUG barrio_top20:")
print("  Expected:", expected_top20)
print("  Actual:  ", actual_top20)
mismatches = [
    (i, actual_top20[i], expected_top20[i])
    for i in range(len(expected_top20))
    if actual_top20[i] != expected_top20[i]
]
if mismatches:
    print("  Mismatches at positions:", mismatches)
else:
    print("  ✅ Matches expected up to compared length.")
