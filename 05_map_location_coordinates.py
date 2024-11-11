import pandas as pd
import googlemaps
import argparse
import os


def load_database_file(database_file_path):
    """
    加載本地數據庫文件，返回包含地名、搜尋關鍵地名、建議地名、緯度和經度的 DataFrame。
    如果數據庫文件不存在或為空，則返回一個空的 DataFrame。
    """
    if os.path.exists(database_file_path):
        try:
            return pd.read_csv(database_file_path, sep='|')
        except pd.errors.EmptyDataError:
            # 如果文件為空，返回一個空的 DataFrame
            return pd.DataFrame(columns=['地名', '搜尋關鍵地名', '建議地名', '緯度', '經度'])
    else:
        # 如果文件不存在，返回一個空的 DataFrame
        return pd.DataFrame(columns=['地名', '搜尋關鍵地名', '建議地名', '緯度', '經度'])


def save_database_to_file(database_file_path, database):
    """
    將數據庫內容保存到指定的 CSV 文件，使用 '|' 作為分隔符。
    """
    database.to_csv(database_file_path, index=False, sep='|',
                    columns=['地名', '搜尋關鍵地名', '建議地名', '緯度', '經度'])


def fetch_place_suggestion(gmaps_client, query):
    """
    使用 Google Place Autocomplete API 獲取地點建議，只返回最接近的建議。
    """
    suggestions = gmaps_client.places_autocomplete(query)
    if suggestions:
        return suggestions[0]['description']
    return None


def fetch_geolocation(gmaps_client, place_name):
    """
    根據地名獲取其經緯度，若找不到返回 (None, None)。
    """
    geocode_result = gmaps_client.geocode(place_name)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return (location['lat'], location['lng'])
    return (None, None)


def main(api_key, input_csv, output_csv, query_prefix, database_file_path):
    # 初始化 Google Maps 客戶端
    gmaps_client = googlemaps.Client(key=api_key)

    # 加載或初始化數據庫
    database = load_database_file(database_file_path)

    # 加載輸入 CSV 文件
    input_data = pd.read_csv(input_csv)

    # 增加新列，用於儲存查詢結果
    input_data['搜尋關鍵地名'] = ''
    input_data['建議地名'] = ''
    input_data['緯度'] = ''
    input_data['經度'] = ''

    # API 調用次數計數器
    api_call_counter = 0

    # 處理每一筆地名資料
    for index, row in input_data.iterrows():
        if pd.isna( row['地名']):
            continue

        full_query_name = query_prefix + str(row['地名'])

        # 檢查地名是否已存在於數據庫
        database_row = database[database['地名'] == row['地名']]
        if not database_row.empty:
            # 若地名已存在，使用數據庫中的數據
            input_data.at[index, '搜尋關鍵地名'] = database_row.iloc[0]['搜尋關鍵地名']
            input_data.at[index, '建議地名'] = database_row.iloc[0]['建議地名']
            input_data.at[index, '緯度'] = database_row.iloc[0]['緯度']
            input_data.at[index, '經度'] = database_row.iloc[0]['經度']
        else:
            # 若地名不存在於數據庫，調用 API 獲取建議地名及其經緯度
            suggested_place = fetch_place_suggestion(
                gmaps_client, full_query_name)
            if suggested_place:
                lat, lng = fetch_geolocation(gmaps_client, suggested_place)
                input_data.at[index, '搜尋關鍵地名'] = full_query_name
                input_data.at[index, '建議地名'] = suggested_place
                input_data.at[index, '緯度'] = lat
                input_data.at[index, '經度'] = lng

                # 將新資料添加至數據庫
                new_record = pd.DataFrame({
                    '地名': [row['地名']],
                    '搜尋關鍵地名': [full_query_name],
                    '建議地名': [suggested_place],
                    '緯度': [lat],
                    '經度': [lng]
                })
                database = pd.concat([database, new_record], ignore_index=True)

                # 增加 API 調用次數
                api_call_counter += 1

    # 移除建議地名為空的行
    input_data = input_data[input_data['建議地名'] != '']

    # 保存更新後的數據庫
    save_database_to_file(database_file_path, database)

    # 將結果保存到輸出 CSV 文件，使用 '|' 作為分隔符
    input_data.to_csv(output_csv, index=False, sep='|', columns=[
                      '地名', '搜尋關鍵地名', '建議地名', '緯度', '經度'])

    # 顯示 API 調用次數
    print(f"API 調用次數: {api_call_counter}")


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -K 金鑰 -P 地名查詢前綴 -D 地名數據庫檔案 -I 輸入檔案 -O 輸出檔案

使用 Google Maps API 獲取地名建議和經緯度

選項:
  -h, --help            顯示此幫助訊息並退出
  -K KEY, --key KEY     Google Maps API 金鑰
  -P REGION, --prefix REGION
                        地名查詢前綴
  -D DATABASE, --database DATABASE
                        地名數據庫檔案
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出檔案
        """
        print(help_message, file=file)


if __name__ == "__main__":
    parser = CustomArgumentParser(
        description='使用 Google Maps API 獲取地名建議和經緯度')
    parser.add_argument('-K', '--key', required=True,
                        help='Google Maps API 金鑰')
    parser.add_argument('-P', '--prefix', required=False,
                        default='', help='地名查詢前綴')
    parser.add_argument('-D', '--database', required=True, help='數據庫 CSV 檔案路徑')
    parser.add_argument('-I', '--input', required=True, help='輸入檔案')
    parser.add_argument('-O', '--output', required=True, help='輸出檔案')

    args = parser.parse_args()

    # 調用 main 函數並傳入參數
    main(args.key, args.input, args.output, args.prefix, args.database)
