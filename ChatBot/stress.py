import requests
import time
import threading
import statistics
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置
BASE_URL = "http://127.0.0.1:5003"  # 修改为你的服务地址

# 测试问题库
TEST_MESSAGES = [
    "老板拖欠工资3个月怎么办？",
    "民间借贷8万不还，有借条，怎么起诉？",
    "离婚财产分割，婚后房产怎么分？",
    "工伤怎么认定？公司不赔怎么办？",
    "被诈骗了5万，报警能追回吗？",
    "劳动合同没签，能要双倍工资吗？",
    "交通事故对方全责不赔钱怎么办？",
    "取保候审是什么意思？要多久？",
    "家暴怎么申请人身保护令？",
    "买二手房卖家违约不卖了怎么办？",
    "公司违法辞退，怎么要赔偿金？",
    "借条怎么写才有法律效力？",
    "被朋友骗了钱怎么报警？",
    "租房押金不退怎么办？",
    "楼上漏水不修怎么维权？"
]


class VisualStressTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()

    def test_single_request(self, user_msg, request_id, mode="normal"):
        """测试单个请求"""
        start_time = time.time()
        url = f"{self.base_url}/chat" if mode == "normal" else f"{self.base_url}/chat-pro"

        payload = {
            "msg": user_msg,
            "context": []
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                return {
                    "id": request_id,
                    "success": True,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "reply_length": len(data.get("reply", "")),
                    "risk_level": data.get("risk_level", "unknown"),
                    "scene": data.get("scene", "unknown"),
                    "error": None
                }
            else:
                return {
                    "id": request_id,
                    "success": False,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {
                "id": request_id,
                "success": False,
                "response_time": 60.0,
                "error": "Timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "id": request_id,
                "success": False,
                "response_time": time.time() - start_time,
                "error": "ConnectionError - 服务未启动"
            }
        except Exception as e:
            return {
                "id": request_id,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)[:50]
            }

    def run_test(self, concurrency=10, total_requests=50, mode="normal", show_progress=True):
        """
        运行压力测试

        参数:
        - concurrency: 并发数
        - total_requests: 总请求数
        - mode: normal 或 pro
        - show_progress: 是否显示进度
        """
        print("\n" + "=" * 70)
        print("🚀 压力测试启动".center(68))
        print("=" * 70)
        print(f"📍 服务地址: {self.base_url}")
        print(f"🎯 测试模式: {'专业模式' if mode == 'pro' else '普通模式'}")
        print(f"⚡ 并发数: {concurrency}")
        print(f"📊 总请求数: {total_requests}")
        print(f"📝 测试问题数: {len(TEST_MESSAGES)}")
        print("=" * 70 + "\n")

        # 准备测试消息（循环使用）
        messages = [TEST_MESSAGES[i % len(TEST_MESSAGES)] for i in range(total_requests)]

        self.results = []
        self.progress = 0

        start_time = time.time()

        # 使用线程池
        threads = []

        for i in range(total_requests):
            # 控制并发数
            while len([t for t in threads if t.is_alive()]) >= concurrency:
                time.sleep(0.05)
                threads = [t for t in threads if t.is_alive()]

            t = threading.Thread(
                target=self._worker,
                args=(i, messages[i], mode)
            )
            threads.append(t)
            t.start()

            if show_progress:
                self._print_progress(i + 1, total_requests)

        # 等待所有线程完成
        for t in threads:
            t.join()

        end_time = time.time()
        total_duration = end_time - start_time

        if show_progress:
            print()  # 换行

        # 统计结果
        stats = self._calculate_stats(total_duration)

        return stats

    def _worker(self, request_id, user_msg, mode):
        """工作线程"""
        result = self.test_single_request(user_msg, request_id, mode)
        with self.lock:
            self.results.append(result)
            self.progress += 1

    def _print_progress(self, current, total):
        """打印进度条"""
        percent = current / total * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f'\r进度: |{bar}| {current}/{total} ({percent:.1f}%)')
        sys.stdout.flush()

    def _calculate_stats(self, total_duration):
        """计算统计数据"""
        success_results = [r for r in self.results if r["success"]]
        failed_results = [r for r in self.results if not r["success"]]

        response_times = [r["response_time"] for r in success_results]
        response_times_all = [r["response_time"] for r in self.results]

        stats = {
            "total_requests": len(self.results),
            "success_count": len(success_results),
            "failed_count": len(failed_results),
            "success_rate": len(success_results) / len(self.results) * 100 if self.results else 0,
            "total_duration": total_duration,
            "qps": len(self.results) / total_duration if total_duration > 0 else 0,
            "response_times": response_times,
            "response_times_all": response_times_all,
            "errors": {}
        }

        # 错误统计
        for r in failed_results:
            error = r.get("error", "Unknown")
            stats["errors"][error] = stats["errors"].get(error, 0) + 1

        # 响应时间统计
        if response_times:
            stats["avg_response_time"] = statistics.mean(response_times)
            stats["median_response_time"] = statistics.median(response_times)
            stats["min_response_time"] = min(response_times)
            stats["max_response_time"] = max(response_times)
            if len(response_times) > 1:
                stats["std_response_time"] = statistics.stdev(response_times)
            else:
                stats["std_response_time"] = 0

            sorted_times = sorted(response_times)
            stats["p50"] = sorted_times[int(len(sorted_times) * 0.50)]
            stats["p75"] = sorted_times[int(len(sorted_times) * 0.75)]
            stats["p90"] = sorted_times[int(len(sorted_times) * 0.90)]
            stats["p95"] = sorted_times[int(len(sorted_times) * 0.95)]
            stats["p99"] = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            stats["avg_response_time"] = 0
            stats["median_response_time"] = 0
            stats["min_response_time"] = 0
            stats["max_response_time"] = 0
            stats["std_response_time"] = 0
            stats["p50"] = stats["p75"] = stats["p90"] = stats["p95"] = stats["p99"] = 0

        return stats

    def print_report(self, stats):
        """打印测试报告"""
        print("\n" + "=" * 70)
        print("📊 压力测试报告".center(68))
        print("=" * 70)

        print(f"\n📈 请求统计:")
        print(f"   总请求数: {stats['total_requests']}")
        print(f"   成功请求: {stats['success_count']} ✅")
        print(f"   失败请求: {stats['failed_count']} ❌")
        print(f"   成功率: {stats['success_rate']:.2f}%")
        print(f"   总耗时: {stats['total_duration']:.2f} 秒")
        print(f"   QPS: {stats['qps']:.2f} 请求/秒")

        if stats['success_count'] > 0:
            print(f"\n⏱️ 响应时间统计 (秒):")
            print(f"   平均响应时间: {stats['avg_response_time']:.3f}s")
            print(f"   中位数响应时间: {stats['median_response_time']:.3f}s")
            print(f"   最小响应时间: {stats['min_response_time']:.3f}s")
            print(f"   最大响应时间: {stats['max_response_time']:.3f}s")
            print(f"   标准差: {stats['std_response_time']:.3f}s")
            print(f"   P50响应时间: {stats['p50']:.3f}s")
            print(f"   P75响应时间: {stats['p75']:.3f}s")
            print(f"   P90响应时间: {stats['p90']:.3f}s")
            print(f"   P95响应时间: {stats['p95']:.3f}s")
            print(f"   P99响应时间: {stats['p99']:.3f}s")

        if stats["errors"]:
            print(f"\n❌ 错误类型分布:")
            for error, count in stats["errors"].items():
                print(f"   {error}: {count}次 ({count / stats['total_requests'] * 100:.1f}%)")

        # 性能评级
        print(f"\n🎯 性能评级:")
        if stats["success_rate"] >= 99 and stats["avg_response_time"] < 2:
            rating = "⭐⭐⭐⭐⭐ 卓越 - 服务表现极佳"
        elif stats["success_rate"] >= 95 and stats["avg_response_time"] < 5:
            rating = "⭐⭐⭐⭐ 良好 - 服务表现稳定"
        elif stats["success_rate"] >= 90:
            rating = "⭐⭐⭐ 合格 - 服务基本可用"
        elif stats["success_rate"] >= 80:
            rating = "⭐⭐ 需改进 - 建议优化"
        else:
            rating = "⭐ 较差 - 需要紧急优化"
        print(f"   {rating}")

        print("\n" + "=" * 70)

        # 健康度建议
        print("\n💡 优化建议:")
        if stats["avg_response_time"] > 5:
            print("   ⚠️ 平均响应时间较长 (>5s)，建议检查API性能和网络")
        if stats["success_rate"] < 95:
            print("   ⚠️ 成功率偏低 (<95%)，建议检查服务稳定性")
        if stats["p95"] > 10:
            print("   ⚠️ P95响应时间过长 (>10s)，存在明显性能瓶颈")
        if stats["success_rate"] >= 99 and stats["avg_response_time"] < 2:
            print("   ✅ 服务表现优秀，可以支持更高并发")

    def draw_charts(self, stats):
        """绘制可视化图表（ 4个核心图表）"""
        if stats['success_count'] == 0:
            print("没有成功的请求，无法绘制图表")
            return

        # 创建2x2的子图布局
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'法律咨询系统压力测试报告\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                     fontsize=16, fontweight='bold')

        response_times = stats['response_times']

        # 图表1: 响应时间分布直方图
        ax1 = axes[0, 0]
        ax1.hist(response_times, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        ax1.axvline(stats['avg_response_time'], color='red', linestyle='--',
                    linewidth=2, label=f'平均: {stats["avg_response_time"]:.2f}s')
        ax1.axvline(stats['median_response_time'], color='orange', linestyle='--',
                    linewidth=2, label=f'中位数: {stats["median_response_time"]:.2f}s')
        ax1.set_xlabel('响应时间 (秒)')
        ax1.set_ylabel('请求数量')
        ax1.set_title('响应时间分布')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 图表2: 响应时间变化趋势
        ax2 = axes[0, 1]
        ax2.plot(range(1, len(response_times) + 1), response_times, 'o-', markersize=3,
                 linewidth=1, color='green', alpha=0.6)
        ax2.axhline(stats['avg_response_time'], color='red', linestyle='--',
                    linewidth=1, label=f'平均: {stats["avg_response_time"]:.2f}s')
        ax2.fill_between(range(1, len(response_times) + 1), response_times, stats['avg_response_time'],
                         alpha=0.2, color='red')
        ax2.set_xlabel('请求序号 (按时间顺序)')
        ax2.set_ylabel('响应时间 (秒)')
        ax2.set_title('响应时间变化趋势')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 图表3: 成功率饼图
        ax3 = axes[1, 0]
        colors = ['#2ecc71', '#e74c3c']
        labels = [f'成功\n{stats["success_count"]}次', f'失败\n{stats["failed_count"]}次']
        ax3.pie([stats['success_count'], stats['failed_count']], labels=labels,
                autopct='%1.1f%%', colors=colors, startangle=90)
        ax3.set_title(f'请求成功率: {stats["success_rate"]:.1f}%')

        # 图表4: 百分位数条形图
        ax4 = axes[1, 1]
        percentiles = ['P50', 'P75', 'P90', 'P95', 'P99']
        values = [stats['p50'], stats['p75'], stats['p90'], stats['p95'], stats['p99']]
        bars = ax4.bar(percentiles, values, color='coral', edgecolor='black')
        ax4.set_ylabel('响应时间 (秒)')
        ax4.set_title('响应时间百分位数')
        for bar, val in zip(bars, values):
            ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f'{val:.2f}s', ha='center', va='bottom', fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        # 保存图片
        filename = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n📸 图表已保存: {filename}")

        # 显示图片
        plt.show()

        return filename


def main():
    """主函数 - 交互式菜单"""
    print("\n" + "🏛️" * 20)
    print("   法律咨询系统压力测试工具")
    print("🏛️" * 20)

    # 检查服务是否可用
    tester = VisualStressTester()

    print("\n检查服务连接...")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ 服务连接正常")
    except:
        print(f"❌ 无法连接到服务: {BASE_URL}")
        print("请确保先启动法律咨询系统: python app.py")
        return

    while True:
        print("\n" + "-" * 50)
        print("请选择测试模式:")
        print("1. 🚀 快速测试 (10并发, 50请求)")
        print("2. ⚡ 轻度压力 (5并发, 30请求)")
        print("3. 🔥 中度压力 (15并发, 100请求)")
        print("4. 💪 重度压力 (30并发, 200请求)")
        print("5. 🎯 自定义测试")
        print("0. ❌ 退出")
        print("-" * 50)

        choice = input("请输入选项 (0-5): ").strip()

        if choice == "0":
            print("感谢使用，再见！")
            break
        elif choice == "1":
            concurrency, total = 10, 50
            mode = input("测试模式 (1=普通模式, 2=专业模式, 默认1): ").strip()
            mode = "pro" if mode == "2" else "normal"
            stats = tester.run_test(concurrency, total, mode)
            tester.print_report(stats)
            tester.draw_charts(stats)
        elif choice == "2":
            concurrency, total = 5, 30
            mode = input("测试模式 (1=普通模式, 2=专业模式, 默认1): ").strip()
            mode = "pro" if mode == "2" else "normal"
            stats = tester.run_test(concurrency, total, mode)
            tester.print_report(stats)
            tester.draw_charts(stats)
        elif choice == "3":
            concurrency, total = 15, 100
            mode = input("测试模式 (1=普通模式, 2=专业模式, 默认1): ").strip()
            mode = "pro" if mode == "2" else "normal"
            stats = tester.run_test(concurrency, total, mode)
            tester.print_report(stats)
            tester.draw_charts(stats)
        elif choice == "4":
            concurrency, total = 30, 200
            mode = input("测试模式 (1=普通模式, 2=专业模式, 默认1): ").strip()
            mode = "pro" if mode == "2" else "normal"
            stats = tester.run_test(concurrency, total, mode)
            tester.print_report(stats)
            tester.draw_charts(stats)
        elif choice == "5":
            try:
                concurrency = int(input("请输入并发数 (建议 1-50): ").strip())
                total = int(input("请输入总请求数: ").strip())
                mode = input("测试模式 (1=普通模式, 2=专业模式, 默认1): ").strip()
                mode = "pro" if mode == "2" else "normal"
                stats = tester.run_test(concurrency, total, mode)
                tester.print_report(stats)
                tester.draw_charts(stats)
            except ValueError:
                print("请输入有效的数字！")
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()