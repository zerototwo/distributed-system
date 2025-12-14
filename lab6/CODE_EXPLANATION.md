# Climate Analysis Code Explanation

## Overview

This Spark application analyzes NOAA GSOD (Global Surface Summary of the Day) climate data using RDD-based transformations and aggregations.

## Code Structure

### 1. Data Structures

```python
ClimateRecord = namedtuple('ClimateRecord', [
    'station_id', 'date', 'year', 'month', 'season',
    'temp_avg', 'temp_max', 'temp_min',
    'precipitation', 'wind_speed_avg', 'wind_gust_max',
    'fog', 'rain', 'snow', 'hail', 'thunder', 'tornado'
])
```

**Purpose**: Defines the structure for cleaned climate data records.

### 2. Helper Functions

#### `parse_date(date_str)`
- **Input**: Date string in format 'YYYY-MM-DD'
- **Output**: (year, month, season)
- **Purpose**: Extracts year, month, and determines season (Winter/Spring/Summer/Autumn)

#### `parse_frshtt(frshtt_str)`
- **Input**: 6-character FRSHTT string
- **Output**: Tuple of 6 boolean flags (fog, rain, snow, hail, thunder, tornado)
- **Purpose**: Parses extreme weather event indicators

#### `clean_numeric(value_str, invalid_value=9999.9)`
- **Input**: String representation of a number
- **Output**: Float or None
- **Purpose**: Converts string to float, filters out invalid values (9999.9)

#### `parse_record(line)`
- **Input**: CSV line string
- **Output**: ClimateRecord or None
- **Purpose**: Parses a CSV record into a structured ClimateRecord object

### 3. Main Processing Pipeline

#### Step 1: Data Loading
```python
raw_rdd = sc.textFile(f"{input_dir}/*.csv")
header = raw_rdd.first()
data_rdd = raw_rdd.filter(lambda line: line != header)
```
- Loads all CSV files from input directory
- Filters out the header row

#### Step 2: Data Cleaning
```python
records_rdd = data_rdd.map(parse_record).filter(lambda x: x is not None)
```
- Parses each line into ClimateRecord
- Filters out invalid records

#### Step 3: Monthly Average Temperatures
```python
monthly_temp = records_rdd.filter(lambda r: r.temp_avg is not None)
    .map(lambda r: ((r.station_id, r.year, r.month), (r.temp_avg, 1)))
    .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
    .map(lambda x: (x[0], x[1][0] / x[1][1]))
```
- **Key**: (station_id, year, month)
- **Value**: Average temperature
- **Method**: Map-Reduce pattern with sum and count

#### Step 4: Yearly Average Temperatures
- Similar to Step 3, but grouped by (station_id, year)

#### Step 5: Temperature Trends
- Uses linear regression to calculate warming/cooling trends per station
- Formula: slope = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)

#### Step 6: Seasonal Precipitation
- Groups by (station_id, season)
- Calculates average precipitation per season

#### Step 7: Maximum Daily Temperatures
- Finds the highest daily maximum temperature for each station
- Identifies global maximum

#### Step 8: Extreme Events Detection
- **Extreme Heat**: temp_max > 35°C
- **High Wind**: wind_speed_avg > 20 m/s or wind_gust_max > 25 m/s
- **Extreme Weather**: Any FRSHTT flag is set

#### Step 9: Summary Statistics
- Hottest year (highest average yearly temperature)
- Wettest station (highest total precipitation)
- Highest wind gust station

## Key RDD Operations Used

1. **textFile()**: Loads text files into RDD
2. **map()**: Transforms each element
3. **filter()**: Filters elements based on condition
4. **reduceByKey()**: Aggregates values by key
5. **groupByKey()**: Groups values by key
6. **saveAsTextFile()**: Saves RDD to files

## Data Flow

```
CSV Files → textFile() → Parse → Clean → Transform → Aggregate → Save
```

## Output Files

All results are saved as text files in the output directory:
- `monthly_avg_temperature/`
- `yearly_avg_temperature/`
- `temperature_trends/`
- `seasonal_precipitation/`
- `max_daily_temperatures/`
- `extreme_heat_events/`
- `high_wind_events/`
- `extreme_weather_events/`
- `summary_statistics/`

## How to Explain This Code

### For Beginners:
1. Start with the overall goal: analyze climate data
2. Explain the data structure (ClimateRecord)
3. Walk through the helper functions
4. Explain the main pipeline step by step
5. Show how RDD operations work together

### For Technical Audience:
1. Emphasize the RDD-based approach (vs DataFrame)
2. Explain the Map-Reduce pattern
3. Discuss performance considerations
4. Highlight the aggregation strategies
5. Explain the linear regression implementation

### Key Points to Highlight:
- **Distributed Processing**: Spark processes data in parallel
- **Lazy Evaluation**: Operations are not executed until an action is called
- **Fault Tolerance**: RDDs can recover from node failures
- **Scalability**: Can handle large datasets across clusters

