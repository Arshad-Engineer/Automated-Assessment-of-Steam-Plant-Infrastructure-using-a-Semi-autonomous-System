import gpsd
import folium
import time

def get_gps_coordinates():
    try:
        gpsd.connect()
        packet = gpsd.get_current()

        if packet.mode >= 2:
            return packet.lat, packet.lon
        else:
            print("Waiting for GPS fix...")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def display_on_map(map_obj, latitude, longitude):
    folium.Marker([latitude, longitude], popup="Current Location").add_to(map_obj)

def update_map_view(map_obj, data_points):
    # Calculate the bounding box that encompasses all data points
    lats, lons = zip(*data_points)
    bounds = [(min(lats), min(lons)), (max(lats), max(lons))]

    # Fit the map to the bounding box
    map_obj.fit_bounds(bounds)

if __name__ == "__main__":
    data_points = []  # List to store all data points

    try:
        while True:
            coordinates = get_gps_coordinates()

            if coordinates:
                latitude, longitude = coordinates
                print(f"Latitude: {latitude}, Longitude: {longitude}")
                data_points.append((latitude, longitude))

                my_map = folium.Map(location=[latitude, longitude], zoom_start=15)
                display_on_map(my_map, latitude, longitude)
                update_map_view(my_map, data_points)
                my_map.save("current_location_map.html")

            time.sleep(5)
    except KeyboardInterrupt:
        print("Program terminated by user.")
