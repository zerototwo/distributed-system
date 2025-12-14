# Lab 6 Report: Spark Climate Data Analysis

## 1. Executive Summary
Brief overview of the project and main findings.

## 2. Execution Details

### 2.1 Execution Mode
- **Execution Type**: Local / Cluster
- **Deployment Mode**: Client / Cluster
- **Spark Version**: 3.5.3
- **Environment**: 
  - Python: 3.10.12
  - Java: 11.0.28 (OpenJDK)
  - PySpark: 3.5.3

### 2.2 Spark Configuration
- **Master URL**: local[*] (or cluster URL if applicable)
- **Driver Memory**: (if customized)
- **Executor Memory**: (if customized)
- **Number of Cores**: (if customized)

### 2.3 Spark Driver Web UI Screenshots ⚠️ **REQUIRED - MUST INCLUDE**

**Access URL**: http://localhost:4040 (or 4041, 4042, etc. - check terminal output)

**Required Screenshots** (take these while the program is running):

1. **📸 SCREENSHOT 1: Jobs Page** ⭐ REQUIRED
   - Shows all jobs executed during the analysis
   - Include: Job status, duration, submission time
   - **When to take**: After program completes or at final state

2. **📸 SCREENSHOT 2: DAG Visualization** ⭐⭐ **MOST IMPORTANT - REQUIRED**
   - Complete execution plan showing all stages
   - Shows the entire data processing pipeline
   - **When to take**: At final state (before sc.stop())
   - **This is the most critical screenshot for the report**

3. **📸 SCREENSHOT 3: Stages Page** ⭐ REQUIRED
   - Breakdown of stages with task details
   - Shows: Input/Output sizes, Shuffle read/write
   - **When to take**: After complex operations (e.g., temperature trends)

4. **📸 SCREENSHOT 4: Executors Page** ⭐ REQUIRED
   - Executor status and resource utilization
   - Shows: Memory usage, active tasks
   - **When to take**: During execution or at final state

5. **📸 SCREENSHOT 5: Environment Page** (Optional but recommended)
   - Spark configuration and system properties
   - Shows: Spark version, configuration parameters

## 3. Implementation Details

### 3.1 Data Loading and Cleaning
- Describe how data is loaded from CSV files
- Explain data cleaning process (handling invalid values like 9999.9)
- Data validation steps

### 3.2 RDD Transformations Used
List and explain the RDD operations:
- `textFile()`: Loading data
- `map()`: Data transformation
- `filter()`: Data filtering
- `reduceByKey()`: Aggregations
- `groupByKey()`: Grouping operations
- `saveAsTextFile()`: Saving results

### 3.3 Aggregation Operations
Explain each aggregation:
1. Monthly average temperatures per station
2. Yearly average temperatures per station
3. Long-term temperature trends (linear regression)
4. Seasonal precipitation averages
5. Maximum daily temperatures
6. Extreme event detection

## 4. Results and Analysis

### 4.1 Temperature Trends
- **Discussion**: Analyze the temperature trends found in the data
- **Key Findings**: 
  - Which stations show warming trends?
  - Which stations show cooling trends?
  - Overall temperature patterns
- **Supporting Data**: Reference temperature_trends output
- **📸 Supporting Screenshot**: Include DAG Visualization showing temperature trend calculation stages

### 4.2 Seasonal Precipitation Patterns
- **Discussion**: Analyze seasonal precipitation patterns
- **Key Findings**:
  - Which seasons have highest precipitation?
  - Regional variations in precipitation
  - Comparison across stations
- **Supporting Data**: Reference seasonal_precipitation output
- **📸 Supporting Screenshot**: Include relevant stage from Stages page showing precipitation aggregation

### 4.3 Extreme Event Occurrences
- **Discussion**: Analyze extreme weather events
- **Key Findings**:
  - Frequency of extreme heat events
  - High wind event patterns
  - Extreme weather event distribution (fog, rain, snow, hail, thunder, tornado)
- **Supporting Data**: Reference extreme event output files
- **📸 Supporting Screenshot**: Include Jobs page showing extreme event detection jobs

### 4.4 Summary Statistics
- **Hottest Year**: [Year] with average temperature [X]°C
- **Wettest Station**: [Station ID] with total precipitation [X] mm
- **Highest Wind Gust**: Station [ID] with [X] m/s on [Date]

## 5. Performance Analysis

### 5.1 Execution Time
- Total execution time
- Time per aggregation operation
- Bottlenecks identified

### 5.2 Resource Utilization
- Memory usage
- CPU utilization
- Network I/O (if applicable)

## 6. Challenges and Solutions

### 6.1 Challenges Encountered
- Data quality issues
- Performance bottlenecks
- Technical difficulties

### 6.2 Solutions Implemented
- How challenges were addressed
- Optimizations applied

## 7. Conclusion

### 7.1 Key Achievements
- Summary of what was accomplished
- Main insights from the analysis

### 7.2 Future Improvements
- Potential optimizations
- Additional analyses that could be performed

## 8. Appendix

### 8.1 Code Documentation
- Reference to well-documented code
- Key functions explained

### 8.2 Output Files
- List of all output files generated
- Sample outputs included
- **📸 Screenshot**: Terminal output showing program execution

### 8.3 References
- Spark documentation references
- Dataset information (NOAA GSOD)

---

## 📸 Screenshot Checklist for Report Submission

**Required Screenshots** (Must include all):

- [ ] **Screenshot 1**: Spark Web UI - Jobs Page (showing all completed jobs)
- [ ] **Screenshot 2**: Spark Web UI - DAG Visualization (complete execution plan) ⭐⭐ **MOST IMPORTANT**
- [ ] **Screenshot 3**: Spark Web UI - Stages Page (showing stage breakdown)
- [ ] **Screenshot 4**: Spark Web UI - Executors Page (showing executor status)
- [ ] **Screenshot 5**: Terminal/Command Line (showing the command and execution)
- [ ] **Screenshot 6**: Sample Output Files (showing results)
- [ ] **Screenshot 7**: Environment Page (Spark configuration) - Optional but recommended

**Note**: 
- All screenshots should be clear and readable
- Include captions explaining what each screenshot shows
- DAG Visualization is the most critical screenshot for demonstrating the execution plan


