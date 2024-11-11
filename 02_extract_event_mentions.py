import argparse
import os
import json
import google.generativeai as genai
import openai


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file=None):
        # 自訂顯示的幫助訊息
        help_message = f"""使用方法: {self.prog} [-h] -K 金鑰 -L 大語言模型 -S 系統設定檔 -H 對話記錄檔案 -I 輸入檔案 -O 輸出檔案 -P API供應商{{google或openai}}

使用大語言模型處理對話記錄

選項:
  -h, --help            顯示此幫助訊息並退出
  -K KEY, --key KEY     API 金鑰
  -L LLM, --llm LLM     大語言模型的名稱 (例如 'gemini-1.5-pro' 或 'gpt-4o')
  -S SYSTEM, --system SYSTEM
                        系統設定檔 (JSON 格式)
  -H HISTORY, --history HISTORY
                        對話記錄檔案 (JSON 格式)
  -I INPUT, --input INPUT
                        輸入檔案
  -O OUTPUT, --output OUTPUT
                        輸出檔案
  -P {{google,openai}}, --provider {{google,openai}}
                        選擇使用的 API 供應商 ('google' 或 'openai')
        """
        print(help_message, file=file)


def main():
    # 使用 CustomArgumentParser 處理命令列參數
    parser = CustomArgumentParser(description="使用大語言模型處理對話記錄")

    # 添加命令列選項
    parser.add_argument("-K", "--key", required=True, help="API 金鑰")
    parser.add_argument("-L", "--llm", required=True,
                        help="處理的模型名稱 (例如 'gemini-1.5-pro' 或 'gpt-4o')")
    parser.add_argument("-S", "--system", required=True,
                        help="系統設定檔 (JSON 格式)")
    parser.add_argument("-H", "--history", required=True,
                        help="對話記錄檔案 (JSON 格式)")
    parser.add_argument("-I", "--input", required=True, help="輸入檔案")
    parser.add_argument("-O", "--output", required=True, help="輸出的檔案")
    parser.add_argument("-P", "--provider", required=True,
                        choices=['google', 'openai'], help="選擇使用的 API 供應商 ('google' 或 'openai')")

    args = parser.parse_args()

    # 讀取系統設定檔 (JSON 格式)
    with open(args.system, "r", encoding="utf-8") as system_file:
        system_config = json.load(system_file)
        system_instruction = system_config.get("instruction", "")



    # 讀取對話歷史 (JSON 格式)
    with open(args.history, "r", encoding="utf-8") as history_file:
        history = json.load(history_file)  # 假設 history 是 JSON 格式

    # 讀取輸入檔案 (純文字格式)
    with open(args.input, "r", encoding="utf-8") as input_file:
        message = input_file.read()

    # 根據不同的 API 供應商進行對話
    if args.provider == 'google':
        # 使用 Google API 的處理方式
        genai.configure(api_key=args.key)

        # 設定模型配置
        generation_config = {
            "temperature": system_config.get("temperature", 1),
            "top_p": system_config.get("top_p", 0.95),
            "top_k": system_config.get("top_k", 64),
            "max_output_tokens": system_config.get("max_output_tokens", 8192),
            "response_mime_type": system_config.get("response_mime_type", "text/plain")
        }

        model = genai.GenerativeModel(
            model_name=args.llm,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )

        # 開始對話
        chat_session = model.start_chat(history=history)

        # 送出訊息並取得回應
        response = chat_session.send_message({
            "role": "user",
            "parts": [message]
        })

        generated_message = response.text

    elif args.provider == 'openai':
        # 使用 OpenAI API 的處理方式
        client = openai.OpenAI(api_key=args.key)

        msg_list = [{"role": "system", "content": system_instruction}
                    ] + history + [{"role": "user", "content": message}]
        
        # 設定模型配置
        generation_config = {
            "temperature": system_config.get("temperature", 1),
            "top_p": system_config.get("top_p", 0.95),
            "top_k": system_config.get("top_k", 64),
            "max_output_tokens": system_config.get("max_output_tokens", 8192),
            "response_mime_type": system_config.get("response_mime_type", "text/plain"),
            "frequency_penalty": system_config.get("frequency_penalty", 0),
            "presence_penalty": system_config.get("presence_penalty", 0),
            "response_format": system_config.get("response_format", {"type": "text"})
        }        

        # 開始對話
        response = client.chat.completions.create(
            model=args.llm,
            messages=msg_list,
            temperature=generation_config["temperature"],
            max_tokens=generation_config["max_output_tokens"],
            top_p=generation_config["top_p"],
            frequency_penalty=generation_config["frequency_penalty"],
            presence_penalty=generation_config["presence_penalty"],
            response_format=generation_config["response_format"]
        )

        generated_message = response.choices[0].message.content

    # 將回應保存至輸出檔案
    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(generated_message)

    print(f"\n\r回應已儲存至 {args.output}")


if __name__ == "__main__":
    main()
