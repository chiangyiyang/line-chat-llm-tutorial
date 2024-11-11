import csv
import argparse

# 處理CSV檔案以提取獨特地點名稱的函數
def extract_unique_places(input_csv, output_csv):
    unique_places = set()  # 使用集合儲存地點，避免重複

    # 讀取輸入的CSV檔案
    with open(input_csv, 'r', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile)
        next(csv_reader)  # 略過表頭列
        for row in csv_reader:
            place_field = row[2]  # 取得第三欄的'地點'欄位
            # 使用分號分割地點，並去除多餘的空格
            places = [place.strip() for place in place_field.split(';')]
            # 將地點加入集合中，避免重複
            unique_places.update(place for place in places if place)


    # 將獨特的地點名稱寫入輸出的CSV檔案
    with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['地名'])  # 寫入表頭
        for place in sorted(unique_places):  # 排序地點名稱以保持輸出的一致性
            csv_writer.writerow([place])

    print(f"轉換完成，請檢查輸出檔案：{output_csv}")


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -I 輸入檔案 -O 輸出檔案

去除輸入檔案中重複地點後，轉存為輸出檔案

選項:
  -h, --help            顯示此幫助訊息並退出
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出檔案
        """
        print(help_message, file=file)


# 主函數處理命令行參數解析
def main():
    parser = CustomArgumentParser(description="去除輸入檔案中重複地點後，轉存為輸出檔案")
    parser.add_argument('-I', '--input', required=True, help="輸入檔案")
    parser.add_argument('-O', '--output', required=True, help="輸出檔案")
    
    args = parser.parse_args()
    
    # 使用提供的參數呼叫處理函數
    extract_unique_places(args.input, args.output)

# 程式執行入口
if __name__ == "__main__":
    main()
