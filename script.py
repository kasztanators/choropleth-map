import json
import ssl
from urllib.request import urlopen

import folium
import pandas as pd
from sklearn.cluster import KMeans

ssl._create_default_https_context = ssl._create_unverified_context


def load_data():
    data = {
        'voivo_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'name': ['slaskie', 'opolskie', 'wielkopolskie', 'zachodniopomorskie', 'swietokrzyskie', 'kujawsko-pomorskie',
                 'podlaskie', 'dolnoslaskie', 'podkarpackie', 'malopolskie', 'pomorskie', 'warminsko-mazurskie',
                 'lodzkie', 'mazowieckie', 'lubelskie', 'lubuskie'],
        'population': [4576834, 996011, 3475323, 1710482, 1257179, 2086210, 1188800, 2904207, 2127657, 3372618,
                       2307710, 1439675, 2493603, 5349114, 2139726, 1018075],
        'num_cities': [71, 35, 109, 64, 31, 52, 40, 91, 50, 61, 42, 49, 44, 85, 42, 42]
    }
    table = pd.DataFrame(data)
    return table


def load_geojson():
    with urlopen(
            'https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-medium.geojson') as response:
        geojson_voivodeships = json.load(response)
    return geojson_voivodeships


def apply_kmeans_clustering(voivodeships, k):
    X = voivodeships[['population']]
    kmeans = KMeans(n_clusters=k, random_state=42)
    voivodeships['cluster'] = kmeans.fit_predict(X)

    return voivodeships


def create_choropleth_map(voivodeships, geojson_voivodeships):
    m = folium.Map(location=[52, 19], zoom_start=6, tiles="CartoDB positron")

    choropleth_layer = folium.Choropleth(
        geo_data=geojson_voivodeships,
        name='choropleth',
        data=voivodeships,
        columns=['voivo_id', 'cluster'],
        key_on='feature.properties.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.8,
        legend_name='Cluster',
        highlight=True,
    ).add_to(m)

    for idx, row in voivodeships.iterrows():
        folium.GeoJson(
            geojson_voivodeships['features'][idx],
            name=row['name'],
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'transparent',
            },
            highlight_function=lambda x: {
                'fillColor': '#ffffff',
                'color': '#000000',
                'weight': 3,
            },
            tooltip=f"Voivodeships: {row['name']}<br>Population: {row['population']}<br>Number of Cities: {row['num_cities']}"
        ).add_to(m)

    return m


if __name__ == "__main__":
    voivodeships_data = load_data()
    geojson_data = load_geojson()
    voivodeships_data = apply_kmeans_clustering(voivodeships_data, k=3)
    choropleth_map = create_choropleth_map(voivodeships_data, geojson_data)
    choropleth_map.save("poland_choropleth_map.html")
