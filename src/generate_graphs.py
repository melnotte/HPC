from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import pandas as pd
from elasticsearch import Elasticsearch

# Load environment variables from .env file
load_dotenv()

# Conectar con Elasticsearch using environment variables
es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    basic_auth=(os.getenv("ELASTIC_USER"), os.getenv("ELASTIC_PASSWORD"))
)

# Recuperar los datos de Elasticsearch
def get_data_from_elasticsearch():
    query = {
        "size": 1000,  # Obtener los primeros 1000 documentos
        "_source": ["Video", "Video views", "Category", "Likes", "Dislikes", "published"]
    }
    response = es.search(index="youtube_videos", body=query)
    data = [hit["_source"] for hit in response["hits"]["hits"]]
    return pd.DataFrame(data)

df = get_data_from_elasticsearch()

# Limpiar los nombres de las columnas
df.columns = df.columns.str.strip()

# Asegurarse de que las columnas 'Video' y 'Category' no tengan valores nulos
df['Video'] = df['Video'].fillna('Desconocido')
df['Category'] = df['Category'].fillna('Sin Categoría')

# Limpiar los datos y asegurarnos de que las columnas estén en formato adecuado
df['Dislikes'] = pd.to_numeric(df['Dislikes'], errors='coerce').fillna(0).astype(int)
df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0).astype(int)
df['Video views'] = pd.to_numeric(df['Video views'], errors='coerce').fillna(0).astype(float)

# Convertir 'published' a texto (sin decimales)
df['published'] = df['published'].astype(int).astype(str)

# Función para truncar nombres largos de videos
def truncate_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length-3] + '...'

# Top 10 videos con más vistas (scaled to billions)
top_videos = df.nlargest(10, 'Video views')
plt.figure(figsize=(12, 8))
plt.bar(top_videos['Video'].apply(truncate_text), top_videos['Video views'] / 1e9)  # Scale to billions
plt.title('Top 10 Videos con Más Vistas')
plt.ylabel('Vistas (en miles de millones)')
plt.xlabel('Video')
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.gca().set_yticklabels([f'{y:.1f}' for y in plt.gca().get_yticks()])  # Format ticks
plt.tight_layout()
plt.savefig('top_10_videos.png', bbox_inches='tight')
plt.show()

# Categorías con más likes (scaled to millions)
category_likes = df.groupby('Category')['Likes'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 8))
category_likes.plot(kind='bar', y=category_likes / 1e6)  # Scale to millions
plt.title('Top 10 Categorías con Más Likes')
plt.xlabel('Categoría')
plt.ylabel('Likes (en millones)')
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.gca().set_yticklabels([f'{y:.1f}' for y in plt.gca().get_yticks()])  # Format ticks
plt.tight_layout()
plt.savefig('categories_likes.png', bbox_inches='tight')
plt.show()

# Categorías con más dislikes (scaled to thousands)
category_dislikes = df.groupby('Category')['Dislikes'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 8))
category_dislikes.plot(kind='bar', y=category_dislikes / 1e3, color='red')  # Scale to thousands
plt.title('Top 10 Categorías con Más Dislikes')
plt.xlabel('Categoría')
plt.ylabel('Dislikes (en miles)')
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.gca().set_yticklabels([f'{y:.1f}' for y in plt.gca().get_yticks()])  # Format ticks
plt.tight_layout()
plt.savefig('categories_dislikes.png', bbox_inches='tight')
plt.show()

# Año vs cantidad de videos publicados (no scaling needed)
videos_per_year = df['published'].value_counts().sort_index()
plt.figure(figsize=(14, 8))
plt.plot(videos_per_year.index, videos_per_year.values, marker='o')
plt.title('Cantidad de Videos Publicados por Año')
plt.xlabel('Año')
plt.ylabel('Cantidad de Videos')
plt.xticks(videos_per_year.index, videos_per_year.index, rotation=45, ha="right", fontsize=9)
plt.grid(True)
plt.tight_layout()
plt.savefig('videos_per_year.png', bbox_inches='tight')
plt.show()

# Vistas por año (already scaled to billions)
views_per_year = df.groupby('published')['Video views'].sum().sort_index()
plt.figure(figsize=(14, 8))
plt.plot(views_per_year.index, views_per_year.values / 1e9, marker='o', color='teal')  # Scale to billions
plt.title('Total de Vistas por Año de Publicación')
plt.xlabel('Año')
plt.ylabel('Total de Vistas (en miles de millones)')
plt.gca().set_yticklabels([f'{y:.1f}' for y in plt.gca().get_yticks()])  # Format ticks
plt.xticks(views_per_year.index, views_per_year.index, rotation=45, ha="right", fontsize=9)
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig('views_per_year.png', bbox_inches='tight')
plt.show()