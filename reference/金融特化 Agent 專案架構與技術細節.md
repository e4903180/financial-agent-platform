# 檔案一：金融特化 Agent 專案架構與技術細節

本專案旨在建構一個具備「精確財務數值計算」與「真實財報法規檢索」能力的繁體中文金融特化 Agent。透過將 Kaggle 審計級美股財報問答資料集進行在地化翻譯、知識蒸餾與 Self-Instruct 工具標籤合成，構建出 5,000 條高質量的 Tool-Calling 微調資料集。最終利用 QLoRA 微調本地大模型，並與整合了 Reranker 的 RAG 系統對接，實現商用等級的金融問答機器人。

---

## 1. 專案系統架構圖 (System Architecture)

[使用者輸入 (User Query)]
       │
       ▼
┌────────────────────────────────────────────────────────┐
│               自主開發 RAG 檢索模組                     │
│ 1. Vector DB (ChromaDB): 檢索法規與財報文字             │
│ 2. BGE-Reranker: 對檢索出來的 Context 進行二次重排評分   │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼ (帶有 Context 的 Prompt)
┌────────────────────────────────────────────────────────┐
│       微調後的本地大模型 (Fine-tuned LLM via QLoRA)      │
│  - 基底模型: Llama-3-8B-Instruct 或 Taiwan-LLM          │
│  - 核心能力: 準確判斷是否需要計算，並輸出 Tool-Calling JSON │
└───────────────────────┬────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼ (需要數值計算)                 ▼ (純文字回答)
┌──────────────────────────────┐ ┌──────────────────────┐
│      工具執行器 (Executor)    │ │   直接生成最終解答   │
│ - python_calculator_tool     │ │   (Direct Response)  │
│ - yfinance_api_tool          │ └──────────────────────┘
└───────────────┬──────────────┘
                │
                ▼ (工具執行結果)
┌────────────────────────────────────────────────────────┐
│                 最終答案整合輸出 (Synthesis)            │
└────────────────────────────────────────────────────────┘

---

## 2. 專案目錄結構 (Directory Structure)

financial-agent-project/
├── data/
│   ├── raw/                  # Kaggle 原始資料集 (financial-q-and-a-10k)
│   ├── processed/            # 經翻譯、在地化處理後的繁體中文種子數據
│   └── secure_sft_data.json  # 最終合成的 5,000 條工具調用微調資料集
├── src/
│   ├── data_pipeline/        # 數據處理與合成管線
│   │   ├── translate.py      # 在地化與金融術語對齊腳本
│   │   └── synthesizer.py    # Self-Instruct 工具調用標籤合成生成器
│   ├── rag/                  # 檢索增強生成模組
│   │   ├── indexer.py        # 財報 Markdown 表格切片與向量化
│   │   └── retriever.py      # Vector DB 檢索 + BGE-Reranker 重排
│   ├── train/                # 模型的 QLoRA 微調配置
│   │   ├── llama_factory_config.yaml
│   │   └── train.sh          # 啟動微調的指令腳本
│   └── tools/                # Agent 可呼叫的外部工具
│       └── calculator.py     # Python 計算沙盒工具
├── evaluation/               # 系統自動化評估
│   ├── rag_eval_set.json     # 由 Kaggle 衍生出的黃金測試集
│   └── run_ragas_eval.py     # Ragas 框架評估腳本 (計算 Faithfulness 等)
├── app.py                    # Gradio 介面與系統整合主程式
└── README.md

---

## 3. 各核心模組細節實現方法

### A. 數據合成管線 (Data Pipeline)
1. 在地化對齊 (Localization)：讀取 Kaggle 的 `financial-q-and-a-10k`，利用強大模型 API 將 Context 與 Question 轉為繁體中文，並設定 Prompt 嚴格將美股會計術語轉譯為台灣習慣用語（如：Revenue -> 營業收入、Gross Margin -> 毛利率）。
2. 工具標籤合成 (Self-Instruct)：
   - 輸入：在地化財報文本 + 原生問答。
   - 轉譯機制：提示詞（Prompt）強制大模型不要給出直接解答，而是改寫為「思考連鎖（CoT）+ 工具調用代碼」。
   - 範例格式：
     {
       "instruction": "請計算該公司 2024 年的毛利率變化。",
       "input": "2024年營收2,000萬，成本1,200萬；2023年營收1,500萬，成本800萬。",
       "output": "Thinking: 計算毛利率需要公式（營收-成本）/營收。我需要調用計算機分別計算兩年數據再進行對比。\\nAction: `python_calculator_tool`\\nArguments: {\"code_expr\": \"margin_24 = (2000-1200)/2000; margin_23 = (1500-800)/1500; print(f'2024: {margin_24:.2%}, 2023: {margin_23:.2%}')\"}"
     }

### B. 知識檢索模組 (Advanced RAG)
1. 表格切片策略：由於財報包含大量數字表格，專案棄用傳統的純文字字數切片（Text Chunking），改採用將財報內的 HTML/CSV 表格完整轉換為 Markdown Table 格式，確保每一行數據在切片時都不會遺失其表頭（Header）語義。
2. 二次重排 (Reranking)：初階檢索使用 ChromaDB 計算 Cosine Similarity 撈出前 10 個最相關的文本塊；隨後引入 `BAAI/bge-reranker-large` 模型，針對這 10 個文本塊與使用者問題進行深度交互計算，重新篩選出最精確的 Top-3 文本塊送入模型，大幅降低幻覺發生率。

### C. QLoRA 模型微調 (Fine-Tuning)
1. 訓練框架：採用 `LLaMA-Factory` 開源微調框架。
2. 硬體與參數配置：
   - 基底模型：Llama-3-8B-Instruct 
   - 微調技術：QLoRA（4-bit 量化載入基底模型，降低顯存消耗）。
   - 目標模組：Target modules 設為所有線性層（q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj），確保微調質量。
   - 訓練參數：Epochs=3, Batch Size=4, Learning Rate=2e-4, LoRA Rank=16, Alpha=32。

### D. 自動化評估 (Evaluation via Ragas)
1. 評估資料集：從未參與訓練的 Kaggle 原生黃金標準答案中，隨機抽取 200 條作為 `rag_eval_set.json`。
2. 評估指標：
   - 忠實度 (Faithfulness)：檢查 Agent 輸出的答案中，所有宣稱的財務事實是否均能在 RAG 檢索到的 Context 中找到，用以杜絕數值幻覺（目標值 > 90%）。
   - 答案相關性 (Answer Relevance)：評估最終答案是否有精確切中使用者核心問題。

   