import os
import json
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

# 載入環境變數
load_dotenv(os.path.join(os.path.dirname(__file__), "../../config/secret.env"))

class ToolCallingSynthesizer:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.7) # 稍微增加隨機性以增加資料多樣性
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位金融 AI 訓練專家。你的任務是將金融問答對轉化為「思考連鎖 (CoT) + 工具調用 (Tool-Calling)」的訓練格式。

規則：
1. 分析問題是否需要數值計算。
2. 如果需要，輸出必須包含 "Thinking:" 欄位說明計算邏輯，以及 "Action: `python_calculator_tool`" 和 "Arguments: {{'code_expr': '...'}}"。
3. 即使不需要計算，也要保持 CoT 的思考過程。
4. 輸出必須是純 JSON 格式。

範例格式：
{{
  "instruction": "請計算該公司 2024 年的毛利率變化。",
  "input": "2024年營收2,000萬，成本1,200萬；2023年營收1,500萬，成本800萬。",
  "output": "Thinking: 計算毛利率需要公式（營收-成本）/營收。我需要調用計算機分別計算兩年數據再進行對比。\\nAction: `python_calculator_tool`\\nArguments: {{\"code_expr\": \"margin_24 = (2000-1200)/2000; margin_23 = (1500-800)/1500; print(f'2024: {{margin_24:.2%}}, 2023: {{margin_23:.2%}}')\"}}"
}}"""),
            ("human", "Question: {question}\nContext: {context}\nAnswer: {answer}")
        ])
        self.chain = self.prompt | self.llm

    def synthesize_item(self, item):
        """合成單條訓練數據"""
        try:
            response = self.chain.invoke({
                "question": item['question'],
                "context": item['context'],
                "answer": item['answer']
            })
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"合成失敗: {e}")
            return None

def main():
    input_path = "data/processed/financial_qa_tw.json"
    output_path = "data/processed/secure_sft_data.json"
    
    if not os.path.exists(input_path):
        logger.warning(f"找不到已翻譯檔案: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    logger.info(f"開始合成數據: {len(data)} 條紀錄")

    synthesizer = ToolCallingSynthesizer()
    sft_data = []

    for item in tqdm(data):
        sft_item = synthesizer.synthesize_item(item)
        if sft_item:
            sft_data.append(sft_item)
        
        # 存檔
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sft_data, f, ensure_ascii=False, indent=2)

    logger.success(f"合成完成！已存至 {output_path}")

if __name__ == "__main__":
    main()
