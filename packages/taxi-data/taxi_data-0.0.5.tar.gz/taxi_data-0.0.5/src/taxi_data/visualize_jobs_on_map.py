import folium, webbrowser
from pathlib import Path
from typing import Final as Constant
from folium.plugins import HeatMap
from make_gps_jobs import make_gps_jobs

HTML_FILE_NAME: Constant[Path] = "gps_jobs_map.html"

def visualize_jobs_on_map(gps_jobs):
    # Create a map centered around the average coordinates
    avg_lat = sum(job.meter_on_gps.latitude for job in gps_jobs if job.meter_on_gps) / len(gps_jobs)
    avg_lon = sum(job.meter_on_gps.longitude for job in gps_jobs if job.meter_on_gps) / len(gps_jobs)
    my_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    for job in gps_jobs:
        if job.meter_on_gps and job.meter_off_gps:
            # Plot the route
            folium.PolyLine(locations=[
                (job.meter_on_gps.latitude, job.meter_on_gps.longitude),
                (job.meter_off_gps.latitude, job.meter_off_gps.longitude)
            ], color="blue", weight=2.5, opacity=1).add_to(my_map)

            # Add markers
            folium.Marker([job.meter_on_gps.latitude, job.meter_on_gps.longitude], 
                          popup=f"Start: {job.pick_up_suburb}").add_to(my_map)
            folium.Marker([job.meter_off_gps.latitude, job.meter_off_gps.longitude], 
                          popup=f"End: {job.destination_suburb}").add_to(my_map)

    return my_map

def visualize_jobs_heatmap(gps_jobs):
    # Aggregate GPS coordinates
    heatmap_data = [
        [job.meter_on_gps.latitude, job.meter_on_gps.longitude]
        for job in gps_jobs if job.meter_on_gps
    ] + [
        [job.meter_off_gps.latitude, job.meter_off_gps.longitude]
        for job in gps_jobs if job.meter_off_gps
    ]
    
    # Create a map centered around the average coordinates
    avg_lat = sum(coord[0] for coord in heatmap_data) / len(heatmap_data)
    avg_lon = sum(coord[1] for coord in heatmap_data) / len(heatmap_data)
    my_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    
    # Add heatmap layer
    HeatMap(heatmap_data).add_to(my_map)
    
    return my_map

if __name__ == "__main__":
    # Example usage
    gps_jobs = make_gps_jobs(shift_date="23/07/2024")
    
    my_map = visualize_jobs_heatmap(gps_jobs)
    my_map.save(HTML_FILE_NAME)
    webbrowser.open_new_tab(HTML_FILE_NAME)
    