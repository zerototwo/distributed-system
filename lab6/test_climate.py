"""
快速测试脚本：使用少量数据验证功能
"""
import subprocess
import sys
import os

# 创建测试数据目录
test_dir = "test_data_2025"
output_dir = "test_output"

if not os.path.exists(test_dir):
    os.makedirs(test_dir)
    print(f"创建测试目录: {test_dir}")
    
    # 复制前 10 个文件用于测试
    import shutil
    csv_files = sorted([f for f in os.listdir("2025") if f.endswith(".csv")])[:10]
    for f in csv_files:
        shutil.copy(f"2025/{f}", f"{test_dir}/{f}")
    print(f"已复制 {len(csv_files)} 个文件用于测试")

# 运行分析
print(f"\n运行气候分析（测试模式）...")
print(f"输入目录: {test_dir}")
print(f"输出目录: {output_dir}\n")

result = subprocess.run(
    ["python", "climate_analysis.py", test_dir, output_dir],
    cwd="/Users/lupeipei/PycharmProjects/PythonProject/lab6"
)

sys.exit(result.returncode)

