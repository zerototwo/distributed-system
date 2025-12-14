"""
Spark RDD Climate Data Processing Application
Analyze NOAA GSOD global climate dataset

Main Features:
1. Data loading and cleaning
2. Monthly and yearly average temperatures per station
3. Long-term temperature trends
4. Seasonal precipitation averages
5. Stations with highest daily maximum temperatures
6. Extreme event detection
7. Summary statistics
"""

import sys
import csv
from datetime import datetime
from pyspark import SparkContext, SparkConf
from collections import namedtuple

# Define data record structure
ClimateRecord = namedtuple('ClimateRecord', [
    'station_id', 'date', 'year', 'month', 'season',
    'temp_avg', 'temp_max', 'temp_min',
    'precipitation', 'wind_speed_avg', 'wind_gust_max',
    'fog', 'rain', 'snow', 'hail', 'thunder', 'tornado'
])


def parse_date(date_str):
    """Parse date string and extract year, month, and season"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.year
        month = date_obj.month
        
        # Determine season: 12,1,2=Winter, 3,4,5=Spring, 6,7,8=Summer, 9,10,11=Autumn
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Autumn'
        
        return year, month, season
    except:
        return None, None, None


def parse_frshtt(frshtt_str):
    """Parse FRSHTT field and extract extreme event flags
    FRSHTT is a 6-character string: Fog, Rain, Snow, Hail, Thunder, Tornado
    """
    if not frshtt_str or len(frshtt_str) < 6:
        return (False, False, False, False, False, False)
    
    try:
        flags = [int(frshtt_str[i]) for i in range(6)]
        return tuple(flag == 1 for flag in flags)
    except:
        return (False, False, False, False, False, False)


def clean_numeric(value_str, invalid_value=9999.9):
    """Clean numeric fields, convert invalid values (9999.9) to None"""
    try:
        # Remove whitespace
        value_str = value_str.strip()
        if not value_str or value_str == '':
            return None
        
        value = float(value_str)
        # Check if value is invalid
        if abs(value - invalid_value) < 0.1:
            return None
        return value
    except:
        return None


def parse_record(line):
    """Parse CSV record line"""
    try:
        # Use CSV reader to parse quoted fields
        reader = csv.reader([line])
        fields = next(reader)
        
        if len(fields) < 28:
            return None
        
        # Extract fields
        station_id = fields[0].strip('"')
        date_str = fields[1].strip('"')
        temp_avg = clean_numeric(fields[6])
        temp_max = clean_numeric(fields[20])
        temp_min = clean_numeric(fields[22])
        precipitation = clean_numeric(fields[24])
        wind_speed_avg = clean_numeric(fields[16])
        wind_gust_max = clean_numeric(fields[19])
        frshtt = fields[27].strip('"')
        
        # Parse date
        year, month, season = parse_date(date_str)
        if year is None:
            return None
        
        # Parse extreme events
        fog, rain, snow, hail, thunder, tornado = parse_frshtt(frshtt)
        
        # Create record (only records with valid data)
        if temp_avg is None and temp_max is None and temp_min is None:
            return None
        
        return ClimateRecord(
            station_id=station_id,
            date=date_str,
            year=year,
            month=month,
            season=season,
            temp_avg=temp_avg,
            temp_max=temp_max,
            temp_min=temp_min,
            precipitation=precipitation if precipitation is not None else 0.0,
            wind_speed_avg=wind_speed_avg,
            wind_gust_max=wind_gust_max,
            fog=fog,
            rain=rain,
            snow=snow,
            hail=hail,
            thunder=thunder,
            tornado=tornado
        )
    except Exception as e:
        return None


def save_rdd_to_file(rdd, output_path):
    """Save RDD to file"""
    # Collect data and write to file
    results = rdd.collect()
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in results:
            f.write(str(item) + '\n')


def main():
    if len(sys.argv) < 3:
        print("Usage: python climate_analysis.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create SparkContext
    conf = SparkConf().setAppName("Climate-Data-Analysis")
    sc = SparkContext(conf=conf)
    
    print("=" * 60)
    print("Spark Climate Data Analysis Application")
    print("=" * 60)
    
    # ========== 1. Data Loading ==========
    print("\n[1] Loading data from:", input_dir)
    raw_rdd = sc.textFile(f"{input_dir}/*.csv")
    
    # Skip CSV header
    header = raw_rdd.first()
    data_rdd = raw_rdd.filter(lambda line: line != header)
    
    print(f"Total lines (excluding header): {data_rdd.count()}")
    
    # ========== 2. Data Cleaning and Transformation ==========
    print("\n[2] Parsing and cleaning records...")
    records_rdd = data_rdd.map(parse_record).filter(lambda x: x is not None)
    
    total_records = records_rdd.count()
    print(f"Valid records after cleaning: {total_records}")
    
    # ========== 3. Monthly Average Temperatures per Station ==========
    print("\n[3] Computing monthly average temperatures per station...")
    monthly_temp = records_rdd.filter(lambda r: r.temp_avg is not None) \
        .map(lambda r: ((r.station_id, r.year, r.month), (r.temp_avg, 1))) \
        .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])) \
        .map(lambda x: (x[0], x[1][0] / x[1][1]))
    
    monthly_output = monthly_temp.map(lambda x: f"{x[0][0]},{x[0][1]},{x[0][2]},{x[1]:.2f}")
    monthly_output.coalesce(1).saveAsTextFile(f"{output_dir}/monthly_avg_temperature")
    print(f"Monthly average temperatures saved to: {output_dir}/monthly_avg_temperature")
    
    # ========== 4. Yearly Average Temperatures per Station ==========
    print("\n[4] Computing yearly average temperatures per station...")
    yearly_temp = records_rdd.filter(lambda r: r.temp_avg is not None) \
        .map(lambda r: ((r.station_id, r.year), (r.temp_avg, 1))) \
        .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])) \
        .map(lambda x: (x[0], x[1][0] / x[1][1]))
    
    yearly_output = yearly_temp.map(lambda x: f"{x[0][0]},{x[0][1]},{x[1]:.2f}")
    yearly_output.coalesce(1).saveAsTextFile(f"{output_dir}/yearly_avg_temperature")
    print(f"Yearly average temperatures saved to: {output_dir}/yearly_avg_temperature")
    
    # ========== 5. Long-term Temperature Trends per Station ==========
    print("\n[5] Computing long-term temperature trends per station...")
    # Calculate yearly average temperature for each station, then compute trend (simple linear regression slope)
    station_yearly = yearly_temp.map(lambda x: (x[0][0], (x[0][1], x[1]))) \
        .groupByKey() \
        .mapValues(lambda years: sorted(list(years), key=lambda y: y[0]))
    
    def calculate_trend(years_data):
        """Calculate temperature trend (simple linear regression)"""
        if len(years_data) < 2:
            return None
        n = len(years_data)
        years = [y[0] for y in years_data]
        temps = [y[1] for y in years_data]
        
        sum_x = sum(years)
        sum_y = sum(temps)
        sum_xy = sum(years[i] * temps[i] for i in range(n))
        sum_x2 = sum(y * y for y in years)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:
            return None
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    trends = station_yearly.mapValues(calculate_trend) \
        .filter(lambda x: x[1] is not None) \
        .map(lambda x: (x[0], x[1], "warming" if x[1] > 0 else "cooling"))
    
    trends_output = trends.map(lambda x: f"{x[0]},{x[1]:.4f},{x[2]}")
    trends_output.coalesce(1).saveAsTextFile(f"{output_dir}/temperature_trends")
    print(f"Temperature trends saved to: {output_dir}/temperature_trends")
    
    # ========== 6. Seasonal Precipitation Averages ==========
    print("\n[6] Computing seasonal precipitation averages...")
    seasonal_precip = records_rdd.filter(lambda r: r.precipitation is not None and r.precipitation > 0) \
        .map(lambda r: ((r.station_id, r.season), (r.precipitation, 1))) \
        .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])) \
        .map(lambda x: (x[0], x[1][0] / x[1][1]))
    
    seasonal_output = seasonal_precip.map(lambda x: f"{x[0][0]},{x[0][1]},{x[1]:.2f}")
    seasonal_output.coalesce(1).saveAsTextFile(f"{output_dir}/seasonal_precipitation")
    print(f"Seasonal precipitation averages saved to: {output_dir}/seasonal_precipitation")
    
    # ========== 7. Stations with Highest Daily Maximum Temperatures ==========
    print("\n[7] Finding stations with highest daily maximum temperatures...")
    max_temps = records_rdd.filter(lambda r: r.temp_max is not None) \
        .map(lambda r: (r.station_id, (r.temp_max, r.date))) \
        .reduceByKey(lambda a, b: a if a[0] > b[0] else b)
    
    # Find global maximum temperature
    global_max = max_temps.map(lambda x: (x[1][0], (x[0], x[1][0], x[1][1]))) \
        .max()
    
    max_temp_output = max_temps.map(lambda x: f"{x[0]},{x[1][0]:.2f},{x[1][1]}")
    max_temp_output.coalesce(1).saveAsTextFile(f"{output_dir}/max_daily_temperatures")
    print(f"Maximum daily temperatures saved to: {output_dir}/max_daily_temperatures")
    print(f"Global maximum: Station {global_max[1][0]}, Temp: {global_max[1][1]:.2f}°C, Date: {global_max[1][2]}")
    
    # ========== 8. Extreme Event Detection ==========
    print("\n[8] Detecting extreme events...")
    
    # Extreme heat (temperature > 35°C)
    extreme_heat = records_rdd.filter(lambda r: r.temp_max is not None and r.temp_max > 35) \
        .map(lambda r: (r.station_id, r.date, r.temp_max))
    
    extreme_heat_output = extreme_heat.map(lambda x: f"{x[0]},{x[1]},{x[2]:.2f}")
    extreme_heat_output.coalesce(1).saveAsTextFile(f"{output_dir}/extreme_heat_events")
    print(f"Extreme heat events saved to: {output_dir}/extreme_heat_events")
    
    # High wind days (MXSPD > 20 m/s or GUST > 25 m/s)
    high_wind = records_rdd.filter(lambda r: 
        (r.wind_speed_avg is not None and r.wind_speed_avg > 20) or
        (r.wind_gust_max is not None and r.wind_gust_max > 25)) \
        .map(lambda r: (r.station_id, r.date, r.wind_speed_avg or 0, r.wind_gust_max or 0))
    
    high_wind_output = high_wind.map(lambda x: f"{x[0]},{x[1]},{x[2]:.2f},{x[3]:.2f}")
    high_wind_output.coalesce(1).saveAsTextFile(f"{output_dir}/high_wind_events")
    print(f"High wind events saved to: {output_dir}/high_wind_events")
    
    # Extreme weather events (FRSHTT)
    extreme_weather = records_rdd.filter(lambda r: 
        r.fog or r.rain or r.snow or r.hail or r.thunder or r.tornado) \
        .map(lambda r: (r.station_id, r.date, 
             int(r.fog), int(r.rain), int(r.snow), 
             int(r.hail), int(r.thunder), int(r.tornado)))
    
    extreme_weather_output = extreme_weather.map(lambda x: 
        f"{x[0]},{x[1]},{x[2]},{x[3]},{x[4]},{x[5]},{x[6]},{x[7]}")
    extreme_weather_output.coalesce(1).saveAsTextFile(f"{output_dir}/extreme_weather_events")
    print(f"Extreme weather events saved to: {output_dir}/extreme_weather_events")
    
    # ========== 9. Summary Statistics ==========
    print("\n[9] Computing summary statistics...")
    
    # Hottest year (based on yearly average temperature)
    hottest_year = yearly_temp.map(lambda x: (x[0][1], (x[1], 1))) \
        .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1])) \
        .map(lambda x: (x[0], x[1][0] / x[1][1])) \
        .max(key=lambda x: x[1])
    
    # Wettest station (based on total precipitation)
    wettest_station = records_rdd.filter(lambda r: r.precipitation is not None) \
        .map(lambda r: (r.station_id, r.precipitation)) \
        .reduceByKey(lambda a, b: a + b) \
        .max(key=lambda x: x[1])
    
    # Station with highest wind gust
    max_wind_station = records_rdd.filter(lambda r: r.wind_gust_max is not None) \
        .map(lambda r: (r.station_id, r.wind_gust_max, r.date)) \
        .max(key=lambda x: x[1])
    
    # Save summary statistics
    summary_lines = [
        f"Hottest Year: {hottest_year[0]}, Average Temperature: {hottest_year[1]:.2f}°C",
        f"Wettest Station: {wettest_station[0]}, Total Precipitation: {wettest_station[1]:.2f} mm",
        f"Highest Wind Gust: Station {max_wind_station[0]}, Speed: {max_wind_station[1]:.2f} m/s, Date: {max_wind_station[2]}"
    ]
    
    summary_rdd = sc.parallelize(summary_lines)
    summary_rdd.coalesce(1).saveAsTextFile(f"{output_dir}/summary_statistics")
    print(f"Summary statistics saved to: {output_dir}/summary_statistics")
    
    print("\n" + "=" * 60)
    print("Summary Statistics:")
    print("=" * 60)
    for line in summary_lines:
        print(line)
    print("=" * 60)
    
    # Stop SparkContext
    sc.stop()
    print("\n✓ Analysis completed successfully!")


if __name__ == "__main__":
    main()

