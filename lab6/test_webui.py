import time
from pyspark import SparkContext, SparkConf

if __name__ == "__main__":
    conf = SparkConf().setAppName("Spark-WebUI-Test")
    sc = SparkContext(conf=conf)
    
    print("=" * 50)
    print("Spark Web UI 已启动！")
    print(f"访问地址: http://localhost:4040")
    print("=" * 50)
    print("\n程序将运行 60 秒，请在此期间访问 Web UI...")
    print("按 Ctrl+C 可以提前结束\n")
    
    # 执行一些操作以便在 Web UI 中看到
    rdd = sc.parallelize(range(1000))
    result = rdd.map(lambda x: x * 2).filter(lambda x: x > 100).collect()
    
    print(f"处理了 {len(result)} 个元素")
    print("\n等待 60 秒... (可以访问 http://localhost:4040 查看 Web UI)")
    
    try:
        time.sleep(60)  # 保持运行 60 秒
    except KeyboardInterrupt:
        print("\n程序被中断")
    
    sc.stop()
    print("Spark 已停止，Web UI 已关闭")

