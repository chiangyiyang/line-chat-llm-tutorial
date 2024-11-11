import argparse
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from matplotlib.dates import DateFormatter, MonthLocator

# 設置中文字型以正確顯示標籤，請根據你的系統安裝的字體進行調整
matplotlib.rc('font', family='Microsoft JhengHei')


def plot_event_occurrences(input_file, output_file, title):
    # 讀取數據
    data = pd.read_csv(input_file, sep=',', encoding='utf-8')

    # 將日期字符串轉換為日期對象
    data['日期'] = pd.to_datetime(data['日期'])

    # 定義事件類型到英文的映射
    event_type_mapping = {
        '落石': 'Rockfall',
        '停電': 'Power Outage'
    }

    # 將事件類型轉換為英文
    data['事件類型英文'] = data['事件類型'].map(event_type_mapping)

    # 為不同的事件類型分配不同的顏色
    colors = {
        'Rockfall': 'red',
        'Power Outage': 'blue'
    }

    # 繪製散點圖，不同事件類型用不同顏色表示，並將標題和圖例調整為英文
    plt.figure(figsize=(12, 6))
    for event_type, color in colors.items():
        subset = data[data['事件類型英文'] == event_type]
        y_position = 1 if event_type == 'Rockfall' else 0.5  # 設定Y軸位置
        plt.scatter(subset['日期'], [y_position] * len(subset),
                    c=color, label=event_type, alpha=0.6, s=50, edgecolor='k')

    # 設置日期格式器和定位器
    plt.gca().xaxis.set_major_locator(MonthLocator())
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m'))

    # 設置標題
    plt.title(title, fontsize=13, fontweight='bold')
    plt.ylim(0, 1.5)  # 設定Y軸尺度為0到1.5
    plt.yticks([1, 0.5], ['落石', '停電'], fontsize=13,
               fontweight='bold')  # 設定Y軸刻度和標籤
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存圖表
    plt.savefig(output_file, dpi=300)

    plt.show()


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -I 輸入檔案 -O 輸出圖表 [-T 標題]

繪製事件發生圖表

選項:
  -h, --help            顯示此幫助訊息並退出
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出圖表
  -T TITLE, --title TITLE
                        圖表標題
        """
        print(help_message, file=file)


if __name__ == "__main__":
    # 設置命令行參數解析
    parser = CustomArgumentParser(description="繪製事件發生圖表")
    parser.add_argument('-I', '--input', type=str,
                        required=True, help='輸入檔案')
    parser.add_argument('-O', '--output', type=str,
                        required=True, help='輸出圖表')
    parser.add_argument('-T', '--title', type=str,
                        default="事件發生頻率", help='圖表標題')

    args = parser.parse_args()

    # 調用繪圖函數
    plot_event_occurrences(args.input, args.output, args.title)
