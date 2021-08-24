from surfpy.buoystation import BuoyStation
import sys

import surfpy

if __name__ == '__main__':
    # https://hopewaves.app/
    # https://maps.ngdc.noaa.gov/viewers/bathymetry/
    # https://www.ndbc.noaa.gov/

    ri_wave_location = surfpy.Location(
        33.15414533992888, -117.35156627349792, name='Carlsbad North')
    ri_wave_location.depth = 6
    ri_wave_location.angle = 225
    ri_wave_location.slope = 0.02

    buoy = BuoyStation('46224', ri_wave_location)
    buoy_data = buoy.fetch_meteorological_reading(1)

    print('Fetching GFS Wave Data')
    wave_model = surfpy.wavemodel.us_west_coast_gfs_wave_model(
        3)  # hour interval to query (3 = every 3 hours)
    # end index is how many intervals/forecasts to query
    wave_grib_data = wave_model.fetch_grib_datas(0, 3)

    raw_wave_data = wave_model.parse_grib_datas(
        ri_wave_location, wave_grib_data)
    if raw_wave_data:
        data = wave_model.to_buoy_data(raw_wave_data)
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(1)

    print('Fetching local weather data')
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(ri_wave_location)
    surfpy.merge_wave_weather_data(data, weather_data)

    for dat in data:
        dat.water_temperature = buoy_data[0].water_temperature
        dat.solve_breaking_wave_heights(ri_wave_location)
        dat.change_units(surfpy.units.Units.english)
    json_data = surfpy.serialize(data)
    with open('forecast.json', 'w') as outfile:
        outfile.write(json_data)
