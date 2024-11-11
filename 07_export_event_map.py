import csv
import argparse
import folium
import pandas as pd


def save_to_csv(output_file, processed_events):
    """將處理後的事件資料儲存至輸出檔案"""
    with open(output_file, mode='w', newline='', encoding='utf-8') as out_file:
        fieldnames = ['name', 'longitude', 'latitude', 'description']
        csv_writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for event in processed_events:
            csv_writer.writerow(event)


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -I 輸入檔案 -O 輸出檔案

輸出地圖

選項:
  -h, --help            顯示此幫助訊息並退出
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出檔案
        """
        print(help_message, file=file)


def main():
    """主函數，負責解析命令行參數並執行各處理函數"""
    parser = CustomArgumentParser(description="輸出地圖")
    parser.add_argument('-I', '--input', required=True, help="輸入檔案")
    parser.add_argument('-O', '--output', required=True, help="輸出檔案")

    args = parser.parse_args()

    # 載入 CSV 檔案
    csv_data = pd.read_csv(args.input)

    # 初始化地圖，將中心設置為平均座標
    avg_lat = csv_data['latitude'].mean()
    avg_lon = csv_data['longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)

    # 迭代 CSV 中的每一行並添加帶有標籤的標記
    for index, row in csv_data.iterrows():
        # 設定標記，popup 顯示描述，tooltip 顯示地點名稱
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['description'],
            tooltip=row['name']
        ).add_to(m)

    # 將地圖儲存為 HTML 檔案
    m.save(args.output)


if __name__ == "__main__":
    main()
