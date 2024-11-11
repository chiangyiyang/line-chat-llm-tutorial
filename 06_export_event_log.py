import csv
import argparse


def load_place_data(database_file):
    """載入地點資料庫，將每個地名和對應的建議地名及經緯度資訊儲存到字典中"""
    place_data = {}
    with open(database_file, mode='r', encoding='utf-8') as db_file:
        csv_reader = csv.DictReader(db_file, delimiter='|')
        for row in csv_reader:
            # 將整行資料儲存，以便地名和建議地名的使用
            place_data[row['地名']] = {
                'original_name': row['地名'],
                'suggested_name': row['建議地名'],
                'latitude': row['緯度'],
                'longitude': row['經度']
            }
    return place_data


def process_event_data(input_file, place_data):
    """處理輸入檔案，依據地點名稱匹配資料庫中的地名並組合事件資訊"""
    processed_events = []
    with open(input_file, mode='r', encoding='utf-8') as in_file:
        csv_reader = csv.DictReader(in_file)
        for row in csv_reader:
            event_type = row['事件類型']
            event_date = row['日期']
            location = row['地點']
            additional_info = row['額外說明']

            # 確認地點是否在地點資料庫中
            if location in place_data:
                place_info = place_data[location]
                combined_description = f"{event_date}_{event_type}_{location}_{additional_info}"
                processed_events.append({
                    'name': place_info['original_name'],  # 使用地名（原始名稱）
                    'longitude': place_info['longitude'],
                    'latitude': place_info['latitude'],
                    'description': combined_description
                })
    return processed_events


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
        help_message = f"""使用方法: {self.prog} [-h] -D 地名數據庫檔案 -I 輸入檔案 -O 輸出檔案

使用地點資料庫，查詢輸入檔案中事件地點座標，並輸出存檔

選項:
  -h, --help            顯示此幫助訊息並退出
  -D DATABASE, --database DATABASE
                        地名數據庫檔案
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出檔案
        """
        print(help_message, file=file)


def main():
    """主函數，負責解析命令行參數並執行各處理函數"""
    parser = CustomArgumentParser(description="使用地名數據庫檔案，查詢輸入檔案中事件地點座標，並輸出存檔")
    parser.add_argument('-D', '--database', required=True, help="地名數據庫檔案")
    parser.add_argument('-I', '--input', required=True, help="輸入檔案")
    parser.add_argument('-O', '--output', required=True, help="輸出檔案")

    args = parser.parse_args()

    place_data = load_place_data(args.database)
    processed_events = process_event_data(args.input, place_data)
    save_to_csv(args.output, processed_events)


if __name__ == "__main__":
    main()
