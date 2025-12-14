import asyncio
import aiohttp
import time

BASE_URL = "http://127.0.0.1:16600/api/v4/futures/{settle}/order_book"

# ===== 配置 =====
SETTLE = "usdt"

CONTRACTS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "XRP_USDT", "ADA_USDT"]

LIMIT = 201
VIP = 5
INTERVAL = "0.01"

CONCURRENCY = 3000
TOTAL_ROUNDS = 1000

# ===== 全局计数器 =====
count_504 = 0
count_timeout = 0
count_ok = 0
count_fail = 0


async def fetch(session, url):
    global count_504, count_timeout, count_ok, count_fail

    try:
        async with session.get(url, timeout=5) as resp:
            await resp.read()
            if resp.status == 200:
                count_ok += 1
            elif resp.status == 504:
                count_504 += 1
                print(f"[504] 当前累计：{count_504}")
            else:
                count_fail += 1
            return
    except asyncio.TimeoutError:
        count_timeout += 1
        print(f"[超时] 当前累计：{count_timeout}")
    except:
        count_fail += 1


async def main():
    urls = [
        f"{BASE_URL.format(settle=SETTLE)}"
        f"?limit={LIMIT}&contract={c}&vip={VIP}&interval={INTERVAL}"
        for c in CONTRACTS
    ]

    connector = aiohttp.TCPConnector(limit=0)

    print(f"[启动] 并发={CONCURRENCY}, 币种={len(urls)}, 计划={TOTAL_ROUNDS} 轮\n")

    async with aiohttp.ClientSession(connector=connector) as session:
        for _ in range(TOTAL_ROUNDS):
            tasks = [fetch(session, urls[i % len(urls)]) for i in range(CONCURRENCY)]
            await asyncio.gather(*tasks)

    # ===== 完成 =====
    print("\n========== 压测完成 (汇总统计) ==========")
    print(f"成功请求: {count_ok}")
    print(f"失败请求: {count_fail}")
    print(f"504 超时: {count_504}")
    print(f"连接/请求超时: {count_timeout}")
    print("=========================================")


if __name__ == "__main__":
    asyncio.run(main())