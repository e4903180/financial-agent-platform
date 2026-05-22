# 財務顧問 Agent 平台開發計畫書 (V2) - 金融特化版

## 1. 專案願景與目標
建構一個具備「精確財務數值計算」與「真實財報法規檢索」能力的繁體中文金融特化 Agent。透過 Kaggle 資料集在地化、Self-Instruct 工具標籤合成以及 QLoRA 微調，結合 Advanced RAG (BGE-Reranker)，實現商用級別、低幻覺的金融問答機器人。

---

## 2. 核心技術架構 (Technical Architecture)
### 2.1 系統流程
1. **意圖判斷與檢索**：User Query -> RAG (ChromaDB + BGE-Reranker) -> Context。
2. **大模型推理**：Fine-tuned LLM (Llama-3-8B) 判斷是否需要計算 -> 輸出 Tool-Calling JSON。
3. **工具執行**：Executor 執行 `python_calculator_tool` 或 `yfinance_api_tool`。
4. **答案整合**：將工具結果與檢索內容整合為最終回答。

### 2.2 目錄結構調整 (依據最新規範)
```text
financial-agent-platform/
├── data/
│   ├── raw/                  # Kaggle 原始資料 (financial-q-and-a-10k)
│   ├── processed/            # 在地化處理後的繁中數據
│   └── secure_sft_data.json  # 5,000 條工具調用微調資料集
├── src/
│   ├── data_pipeline/        # 數據處理與合成 (translate.py, synthesizer.py)
│   ├── rag/                  # 檢索模組 (indexer.py, retriever.py 含 BGE-Reranker)
│   ├── train/                # QLoRA 微調 (LLaMA-Factory)
│   ├── agent/                # 執行引擎 (router.py, model_factory.py)
│   └── tools/                # 外部工具 (calculator.py, yfinance_tool.py)
├── evaluation/               # 自動化評估 (Ragas, rag_eval_set.json)
├── tests/                    # 單元測試
└── requirements.txt
```

---

## 3. 分階段實作藍圖 (Roadmap V2)

### 第一階段：數據管線與在地化 (Data Pipeline & Localization)
*   **目標**：將美股財報數據轉化為高品質繁體中文微調數據。
*   **關鍵任務**：
    *   撰寫 `translate.py`：將 Kaggle 數據在地化，對齊台灣金融術語。
    *   撰寫 `synthesizer.py`：利用 Self-Instruct 合成「思考連鎖 (CoT) + 工具調用」標籤。
*   **驗證點**：完成 5,000 條 `secure_sft_data.json` 且格式正確。

### 第二階段：Advanced RAG 檢索增強 (Advanced RAG)
*   **目標**：降低數據碎片的語義遺失，提升檢索精準度。
*   **關鍵任務**：
    *   實作 **Markdown Table 切片策略**，保留表頭語義。
    *   整合 **BGE-Reranker** 進行二次重排評分。
*   **驗證點**：RAG 檢索出的 Context 忠實度 (Faithfulness) 通過基準測試。

### 第三階段：QLoRA 微調與模型訓練 (Fine-Tuning)
*   **目標**：訓練具備 Tool-Calling 能力的金融專用模型。
*   **關鍵任務**：
    *   使用 `LLaMA-Factory` 配置 QLoRA 參數 (Rank 16, Alpha 32)。
    *   針對所有線性層進行微調，優化 Tool-Calling JSON 輸出穩定性。
*   **驗證點**：模型在測試集上的 Tool-Calling 準確率 (Accuracy) 與格式正確率。

### 第四階段：工具鏈整合與 Ragas 評估 (Integration & Eval)
*   **目標**：完整系統整合並進行商業級自動化評估。
*   **關鍵任務**：
    *   整合 `calculator.py` (Python 沙盒) 與 `yfinance_tool.py`。
    *   使用 **Ragas** 框架計算 Faithfulness 與 Answer Relevance。
    *   建立 Gradio 介面。
*   **驗證點**：系統整體 Faithfulness 指標 > 90%。

---

## 4. 變更記錄 (Change Log)
*   **V1 -> V2**：
    *   新增 `data_pipeline` 模組，專注於 Kaggle 數據翻譯與合成。
    *   RAG 模組強化：引入 Markdown Table 策略與 BGE-Reranker。
    *   微調方向明確：轉向 **Tool-Calling (JSON)** 而非僅僅是 SQL。
    *   新增 `evaluation` 模組，引入 Ragas 評估框架。
