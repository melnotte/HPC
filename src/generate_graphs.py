import matplotlib.pyplot as plt
import pandas as pd
from elasticsearch import Elasticsearch

# Conexión a Elastic Cloud usando cloud_id y autenticación básica
es = Elasticsearch(
    cloud_id="youtube-cluster:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDJkMDY2ODM3YjE1NjQ1Mjk4MjQxZWNlNmZkZmQ5YjA1JDQ0OTc5OTY2ODc3YjRkOTJiNDkyYjQyZjQzMGRmNDFl",
    basic_auth=("elastic", "WaOcJu9kiG1bcajFni3VWEUL")
)

# Recuperar los datos desde Elasticsearch
def get_data_from_elasticsearch():
    query = {
        "size": 1000,  # Obtener los primeros 1000 documentos
        "_source": ["published", "Video views", "Likes", "Dislikes", "Category"]
    }
    response = es.search(index="youtube_videos", body=query)
    data = [hit["_source"] for hit in response["hits"]["hits"]]
    return pd.DataFrame(data)

# Cargar los datos desde Elasticsearch
df = get_data_from_elasticsearch()

# Limpiar los datos
df['Video views'] = df['Video views'].astype(float)
df['Likes'] = df['Likes'].astype(float)
df['Dislikes'] = df['Dislikes'].astype(float)

# Agrupar los datos por año y obtener la suma de las vistas
df_grouped = df.groupby('published')['Video views'].sum().reset_index()

# Crear el gráfico de vistas por año
plt.figure(figsize=(10, 6))
plt.plot(df_grouped['published'], df_grouped['Video views'], marker='o')
plt.title('Vistas por Año')
plt.xlabel('Año')
plt.ylabel('Vistas Totales')
plt.grid(True)
plt.savefig('views_by_year.png')  # Guardar la imagen en el directorio
plt.show()
