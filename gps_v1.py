import folium

def georeference_points(data_points):
    """
    Georeference data points on a map using Folium.

    Parameters:
    - data_points: A list of tuples, where each tuple contains (latitude, longitude, point_name).

    Returns:
    - folium.Map: An interactive map with georeferenced points.
    """
    # Create a map centered at the mean coordinates of the data points
    center_lat = sum(point[0] for point in data_points) / len(data_points)
    center_lon = sum(point[1] for point in data_points) / len(data_points)
    my_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Add markers for each data point
    for point in data_points:
        folium.Marker([point[0], point[1]], popup=point[2]).add_to(my_map)
    
    return my_map


def update_map_view(map_obj, data_points):
    # Calculate the bounding box that encompasses all data points
    lats, lons, loc_label = zip(*data_points)
    bounds = [(min(lats), min(lons)), (max(lats), max(lons))]

    # Fit the map to the bounding box
    map_obj.fit_bounds(bounds)

    return my_map

if __name__ == "__main__":
    # Example data points (replace with your GPS coordinates)
    data_points = [
        (37.7749, -122.4194, "San Francisco"),
        (34.0522, -118.2437, "Los Angeles"),
        (40.7128, -74.0060, "New York"),
    ]

    # Georeference the data points and save the map to an HTML file
    my_map = georeference_points(data_points)
    update_map_view(my_map, data_points)
    my_map.save("georeferenced_map.html")
