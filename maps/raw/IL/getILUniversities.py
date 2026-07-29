import osmnx as ox
import geopandas as gpd

tags = {
    "amenity": "university"
}

gdf = ox.features_from_place(
    "Illinois, USA",
    tags=tags
)

# Keep only polygons/multipolygons (campus boundaries)
gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

gdf.to_file("illinois_university_campuses.geojson", driver="GeoJSON")