import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

# 載入環境變數
load_dotenv(os.path.join(os.path.dirname(__file__), "../../config/secret.env"))

class FinancialTranslator:
    def __init__(self, model_name="gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位專業的金融翻譯專家，擅長將美股財報 (10-K) 的內容翻譯為台灣習慣的繁體中文金融用語。
請遵循以下術語對齊規則：
- Revenue -> 營業收入 / 營收
- Gross Margin -> 毛利率
- Net Income -> 淨利
- Operating Expenses -> 營業費用
- Assets -> 資產
- Liabilities -> 負債
- Equity -> 股東權益
- Cash Flow -> 現金流量
- Ticker -> 股票代碼

請將輸入的 JSON 格式數據中的 'question', 'answer', 'context' 欄位翻譯成繁體中文。
保持其餘欄位如 'ticker', 'filing' 不變。
輸出格式必須與輸入格式一致。"""),
            ("human", "{json_data}")
        ])
        self.chain = self.prompt | self.llm

    def translate_batch(self, df_batch):
        """處理小批量的數據翻譯"""
        json_str = df_batch.to_json(orient="records", force_ascii=False)
        try:
            response = self.chain.invoke({"json_data": json_str})
            # 簡單清理可能的 Markdown 標記
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            
            translated_data = pd.read_json(content)
            return translated_data
        except Exception as e:
            logger.error(f"翻譯批次失敗: {e}")
            return None

def main():
    raw_path = "data/raw/financial-q-and-a-10k.csv"
    output_path = "data/processed/financial_qa_tw.json"
    
    if not os.path.exists(raw_path):
        logger.warning(f"找不到原始檔案: {raw_path}。請確保資料已放入該目錄。")
        return

    df = pd.read_csv(raw_path)
    logger.info(f"讀取原始數據: {len(df)} 條紀錄")

    translator = FinancialTranslator()
    processed_dfs = []
    
    batch_size = 5  # 為了穩定性與 API 限制，使用小批量
    
    for i in tqdm(range(0, len(df), batch_size)):
        batch = df.iloc[i:i+batch_size]
        translated_batch = translator.translate_batch(batch)
        if translated_batch is not None:
            processed_dfs.append(translated_batch)
        
        # 每處理 10 個批次存檔一次，防止中斷
        if (i // batch_size) % 10 == 0:
            temp_df = pd.concat(processed_dfs)
            temp_df.to_json(output_path, orient="records", force_ascii=False, indent=2)

    final_df = pd.concat(processed_dfs)
    final_df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    logger.success(f"翻譯完成！已存至 {output_path}")

if __name__ == "__main__":
    main()
