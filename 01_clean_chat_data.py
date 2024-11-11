import re
from collections import defaultdict
import argparse

class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -I 輸入檔案 -O 輸出檔案

從聊天記錄中提取並格式化事件資訊

選項:
  -h, --help            顯示此幫助訊息並退出
  -I INPUT, --input INPUT
                        包含聊天記錄的輸入檔案。
  -O OUTPUT, --output OUTPUT
                        儲存格式化事件摘要的輸出檔案。
        """
        print(help_message, file=file)

def parse_events(chat_content):
    """
    解析聊天內容，提取特定事件的日期和描述。
    回傳以日期和事件類型為索引的事件字典。
    """
    events_by_date = defaultdict(lambda: defaultdict(list))
    current_date = None
    target_event_types = ['落石', '停電']
    
    # 逐行處理聊天內容
    for line in chat_content.splitlines():
        # 檢查是否為日期行，例如：2024/11/08
        date_match = re.match(r'^(\d{4}/\d{2}/\d{2}),', line)
        if date_match:
            current_date = date_match.group(1)
        elif current_date:
            # 根據事件類型提取事件描述
            for event_type in target_event_types:
                if event_type in line:
                    event_details = re.sub(r'\d{2}:\d{2} (AM|PM)\t.*?\t', '', line).strip()
                    events_by_date[current_date][event_type].append(event_details)
    return events_by_date

def format_event_summary(events_by_date):
    """
    格式化事件字典，生成指定格式的事件摘要。
    """
    return '\n'.join(
        f"{date}，{event_type}，{'；'.join(details)}"
        for date, event_types in events_by_date.items()
        for event_type, details in event_types.items()
    )

def read_file(filepath):
    """讀取檔案內容並回傳字串。"""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filepath, content):
    """將字串內容寫入指定的檔案。"""
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    # 使用自訂的 ArgumentParser 類別
    parser = CustomArgumentParser(description="從聊天記錄中提取並格式化事件資訊。")
    parser.add_argument('-I', '--input', required=True, help='包含聊天記錄的輸入檔案。')
    parser.add_argument('-O', '--output', required=True, help='儲存格式化事件摘要的輸出檔案。')
    
    args = parser.parse_args()

    # 執行事件提取和格式化
    chat_content = read_file(args.input)
    events_by_date = parse_events(chat_content)
    formatted_event_summary = format_event_summary(events_by_date)

    # 將事件摘要寫入輸出檔案
    write_file(args.output, formatted_event_summary)
    print(f'事件摘要已儲存到 {args.output}')

if __name__ == "__main__":
    main()
