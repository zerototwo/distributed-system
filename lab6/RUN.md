# 如何运行 climate_analysis.py

## 运行步骤

### 1. 激活虚拟环境
```bash
cd /Users/lupeipei/PycharmProjects/PythonProject
source .venv/bin/activate
cd lab6
```

### 2. 运行程序

**基本命令格式：**
```bash
python climate_analysis.py <输入目录> <输出目录>
```

**参数说明：**
- `<输入目录>`: 包含 CSV 文件的目录（例如：`2025`）
- `<输出目录>`: 保存分析结果的目录（例如：`output`）

### 3. 运行示例

#### 方法 1: 使用完整数据集（所有 11656 个文件）
```bash
python climate_analysis.py 2025 output
```
⚠️ **注意**: 这可能需要较长时间，因为要处理大量数据

#### 方法 2: 使用少量文件测试（推荐先测试）
```bash
# 先创建测试数据目录（只包含前 10 个文件）
mkdir -p test_data_2025
cp 2025/*.csv test_data_2025/ 2>/dev/null | head -10
# 或者手动选择几个文件
cp 2025/01001099999.csv test_data_2025/
cp 2025/01001499999.csv test_data_2025/

# 运行测试
python climate_analysis.py test_data_2025 test_output
```

### 4. 查看结果

程序运行完成后，结果会保存在输出目录中：

```
output/
├── monthly_avg_temperature/
│   └── part-00000
├── yearly_avg_temperature/
│   └── part-00000
├── temperature_trends/
│   └── part-00000
├── seasonal_precipitation/
│   └── part-00000
├── max_daily_temperatures/
│   └── part-00000
├── extreme_heat_events/
│   └── part-00000
├── high_wind_events/
│   └── part-00000
├── extreme_weather_events/
│   └── part-00000
└── summary_statistics/
    └── part-00000
```

### 5. 查看输出文件内容

```bash
# 查看摘要统计
cat output/summary_statistics/part-00000

# 查看每月平均温度
head -20 output/monthly_avg_temperature/part-00000

# 查看极端事件
head -20 output/extreme_heat_events/part-00000
```

## 程序输出说明

程序会输出以下信息：
1. 数据加载进度
2. 清洗后的有效记录数
3. 各种聚合计算的进度
4. 摘要统计结果

## 注意事项

1. **确保有足够的磁盘空间**：输出文件可能较大
2. **运行时间**：完整数据集可能需要几分钟到几十分钟
3. **Spark Web UI**：程序运行时可访问 http://localhost:4040 查看执行情况
4. **内存使用**：如果数据量很大，可能需要调整 Spark 内存配置

## 故障排除

如果遇到问题：
1. 检查输入目录是否存在且包含 CSV 文件
2. 确保输出目录可写
3. 检查 Java 环境是否正确配置
4. 查看错误日志信息

