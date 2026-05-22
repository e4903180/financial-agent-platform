# 財務顧問 Agent 平台開發計畫書 (V1)

## 1. 專案願景與目標
建立一個企業級、遵循 MLOps 最佳實踐的金融諮詢 Agent 平台。本平台旨在結合結構化數據（Azure SQL）與非結構化文本（RAG），並透過 QLoRA 微調技術提升模型在金融領域的推理與 SQL 生成能力，同時確保系統具備高度的安全性（防注入）與解耦性。

---

## 2. 核心架構設計 (Architecture)
採用「離線訓練」與「即時推理」雙循環架構，確保開發、訓練與維運的生命週期完全分離。

### 2.1 目錄結構規範
```text
financial-agent-platform/
├── .azureml/                   # Azure ML 設定快取
├── config/                     # 全域設定 (YAML/JSON)
├── data/                       # 本地數據 (Raw/Processed/Training)
├── src/                        # 核心原始碼
│   ├── database/               # 資料底層 (Azure SQL, AI Search)
│   ├── train/                  # 雲端微調管線 (Azure ML SDK)
│   └── agent/                  # LangChain 執行引擎 (Router, Tools, Factory)
├── deploy/                     # AKS/Docker 部署設定
├── tests/                      # 單元與迴歸測試
└── requirements.txt            # 相依性清單
```

---

## 3. 分階段實作藍圖 (Implementation Roadmap)

### 第一階段：基礎設施與資料安全層 (Data Layer & Security)
*   **目標：** 建立安全的數據讀取通道，確保 RAG 數據品質。
*   **關鍵任務：**
    *   配置 `database_schema.json` 與資料庫連線池。
    *   實作 **SQL 注入防禦層**（Regex 稽核）。
    *   實作 PDF 轉 Markdown Table 的 ETL 流程並寫入 AI Search。
*   **驗證點 (Checkpoint 1)：**
    *   惡意 SQL 攔截測試百分之百成功。
    *   RAG 檢索出的表格 Markdown 格式無錯位。

### 第二階段：模型工廠與動態路由 (Model Factory & Infrastructure)
*   **目標：** 打通模型叫用通道，實現供應商解耦。
*   **關鍵任務：**
    *   開發 `ModelFactory` 支援 OpenAI 與 vLLM (HuggingFace)。
    *   部署基礎 vLLM 伺服器並載入基底模型（Llama-3-8B）。
*   **驗證點 (Checkpoint 2)：**
    *   實現一秒內無痛切換模型來源，格式保持一致。

### 第三階段：QLoRA 離線微調管線 (Fine-Tuning Pipeline)
*   **目標：** 透過金融特化數據提升模型專業度。
*   **關鍵任務：**
    *   準備 `data/training/` 金融問答對 JSON。
    *   撰寫 `submit_aml_job.py` 透過 Azure ML SDK 調度 A100 算力。
    *   實作輕量化 LoRA 權重動態掛載至 vLLM。
*   **驗證點 (Checkpoint 3)：**
    *   訓練 Loss 穩定下降，且 LoRA 權重可在毫秒級動態切換。

### 第四階段：Agent 工具鏈與業務邏輯 (Agent Core & Logic)
*   **目標：** 組裝「大腦」與「手腳」，實現 PwC 級別的金融諮詢服務。
*   **關鍵任務：**
    *   設計 **PwC 金融顧問人格** System Prompt。
    *   利用 **LCEL** 實作動態意圖路由（判斷走 SQL 還是 RAG）。
    *   整合 `sql_tool` 與 `rag_tool`。
*   **驗證點 (Checkpoint 4)：**
    *   意圖分流準確率達標。
    *   通過「越獄測試」，拒絕非業務相關問題。

---

## 4. 溝通機制與數據協議 (Communication Protocol)

### 4.1 訓練期 (Training)
*   本地腳本 -> Azure ML SDK -> 雲端 A100 (執行 `train_entrypoint.py`) -> 權重推送到私有庫。

### 4.2 推理期 (Runtime)
*   User -> Router (意圖判斷) -> Model Factory (取得 LLM) -> Tool Invocation (SQL/RAG) -> Driver (Azure SQL/Search) -> 回傳 Markdown 結果。

---

## 5. 技術堆棧 (Tech Stack)
*   **Orchestration:** LangChain (LCEL)
*   **LLM Serving:** vLLM, Azure OpenAI
*   **Training:** LLaMA-Factory, PEFT (QLoRA)
*   **Compute:** Azure ML (A100/H100)
*   **Data:** Azure SQL, Azure AI Search (Vector Store)
*   **Ops:** Docker, AKS, Azure DevOps

---

## 6. 後續行動計畫
1.  初始化 Git 儲存庫並建立目錄結構。
2.  建立 `requirements.txt`。
3.  開始執行第一階段：配置資料庫 Schema。
