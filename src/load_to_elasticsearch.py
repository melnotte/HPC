from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import pandas as pd
import uuid

# Conexión a Elastic Cloud usando cloud_id y autenticación básica
es = Elasticsearch(
    cloud_id="youtube-cluster:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDJkMDY2ODM3YjE1NjQ1Mjk4MjQxZWNlNmZkZmQ5YjA1JDQ0OTc5OTY2ODc3YjRkOTJiNDkyYjQyZjQzMGRmNDFl",
    basic_auth=("elastic", "WaOcJu9kiG1bcajFni3VWEUL")
)

# Verificar la conexión
if es.ping():
    print("Conexión a Elastic Cloud exitosa")
else:
    print("Error al conectar a Elastic Cloud")
    exit(1)

# Cargar el dataset con UTF-8 encoding
try:
    df = pd.read_csv('../data/youtube_data.csv', encoding='utf-8')
except Exception as e:
    print(f"Error al cargar el dataset: {e}")
    exit(1)

# Inspeccionar el dataset
print("Dataset preview:")
print(df.head())
print("\nColumn data types:")
print(df.dtypes)
print("\nColumn names:")
print(df.columns)
print("\nNaN values:")
print(df.isna().sum())

# Limpiar los datos
try:
    # Remove commas and convert to float
    df['Video views'] = df['Video views'].astype(str).replace({',': ''}, regex=True).astype(float)
    df['Likes'] = df['Likes'].astype(str).replace({',': ''}, regex=True).astype(float)
    df['Dislikes'] = df['Dislikes'].astype(str).replace({',': ''}, regex=True).astype(float)

    # Fill NaN values
    df['Likes'] = df['Likes'].fillna(0)
    df['Dislikes'] = df['Dislikes'].fillna(0)
    df['Category'] = df['Category'].fillna('Sin Categoría')

    # Ensure other fields are properly typed
    df['rank'] = df['rank'].astype(int)
    df['Video'] = df['Video'].astype(str)
    df['published'] = df['published'].astype(int)
except Exception as e:
    print(f"Error al limpiar los datos: {e}")
    exit(1)

# Validar datos
if df[['Video views', 'Likes', 'Dislikes']].isna().any().any():
    print("Error: Hay valores NaN en las columnas numéricas después de la limpieza")
    exit(1)

# Preparar los datos para ser cargados en Elasticsearch
def generate_actions(df):
    for _, row in df.iterrows():
        yield {
            "_op_type": "index",
            "_index": "youtube_videos",
            "_id": str(uuid.uuid4()),  # Generate unique ID for each document
            "_source": row.to_dict()
        }

# Crear índice si no existe
if not es.indices.exists(index="youtube_videos"):
    es.indices.create(index="youtube_videos", body={
        "mappings": {
            "dynamic": "true",  # Allow dynamic mapping for unknown fields
            "properties": {
                "rank": {"type": "integer"},
                "Video": {"type": "text"},
                "Video views": {"type": "float"},
                "Likes": {"type": "float"},
                "Dislikes": {"type": "float"},
                "Category": {"type": "keyword"},
                "published": {"type": "integer"}
            }
        }
    })

# Print current index mappings
mappings = es.indices.get_mapping(index="youtube_videos")
print("Current index mappings:")
print(mappings)

# Test writing a single document
try:
    test_doc = {
        "rank": 1,
        "Video": "Test Video",
        "Video views": 1000.0,
        "Likes": 50.0,
        "Dislikes": 5.0,
        "Category": "Test",
        "published": 2023
    }
    es.index(index="youtube_videos", body=test_doc)
    print("Test document indexed successfully")
except Exception as e:
    print(f"Error indexing test document: {e}")
    exit(1)

# Cargar datos en Elasticsearch con streaming_bulk
success_count = 0
failed_docs = []
for ok, result in streaming_bulk(es, generate_actions(df), raise_on_error=False, chunk_size=100):
    if ok:
        success_count += 1
    else:
        failed_docs.append(result)

print(f"Datos cargados en Elasticsearch: {success_count} documentos exitosos")
if failed_docs:
    print(f"Errores al indexar {len(failed_docs)} documentos:")
    for i, error in enumerate(failed_docs[:5], 1):  # Print first 5 errors
        print(f"Error {i}: {error}")
else:
    print("Todos los documentos se indexaron correctamente")