# 財務顧問 Agent 平台：專案開發日誌 (Project Log)

本文件記錄了專案開發過程中的重要操作、遇到的挑戰以及相應的解決方案。

---

## 📅 2026-05-22

### ✅ 重要操作記錄
1.  **專案初始化**：建立 `financial-agent-platform` 資料夾。
2.  **需求分析**：深入閱讀並分析了三份參考文件（專案結構、實踐流程、溝通機制），並制定了《計畫書 V1》。
3.  **腳手架建置 (Scaffolding)**：
    *   建立了完整的目錄架構（`config`, `data`, `src`, `deploy`, `tests`, `.azureml`）。
    *   初始化了所有核心模組的預留空檔案。
4.  **版本控制與雲端同步**：
    *   配置了 `.gitignore` 以保護敏感數據與環境變數。
    *   初始化本地 Git 儲存庫並完成 Initial Commit。
    *   使用 GitHub CLI (`gh`) 建立了遠端儲存庫 [e4903180/financial-agent-platform](https://github.com/e4903180/financial-agent-platform)。
    *   將儲存庫權限由私有 (Private) 更改為公開 (Public)。

---

### ⚠️ 遇到問題與解決方法

#### 1. PowerShell 腳本執行安全性限制 (Command Injection Blocked)
*   **問題描述**：嘗試使用一次性 PowerShell 腳本大量建立資料夾與檔案時，被系統安全機制攔截，提示 `Command injection detected`。
*   **解決方法**：將複雜的腳本拆解為簡單、明確的單一命令（如個別執行 `mkdir` 與 `New-Item`），確保操作符合安全規範且易於追蹤。

#### 2. GitHub CLI 權限更改命令錯誤
*   **問題描述**：執行 `gh repo edit` 更改公開性時，誤用了 `--confirm` 參數（該參數不存在於此版本）。
*   **解決方法**：查閱 CLI 說明後，更換為 `--accept-visibility-change-consequences` 參數成功完成權限變更。

---

## 📅 2026-05-22 (續)

### ✅ 重要操作記錄
6.  **計畫調整 (Plan V2)**：
    *   分析了《金融特化 Agent 專案架構與技術細節.md》，決定將重心轉向 **Tool-Calling** 與 **Advanced RAG**。
    *   更新 `PROJECT_PLAN_V2.md`，明確了 Kaggle 數據在地化、BGE-Reranker 與 Ragas 評估的實作路徑。
    *   調整目錄結構：新增 `data_pipeline`, `rag`, `tools` (頂層), `evaluation` 等目錄。
    *   更新 `requirements.txt`：加入 `chromadb`, `ragas`, `yfinance`, `gradio` 等關鍵套件。
7.  **第一階段：數據管線實作**：
    *   實作 `src/data_pipeline/translate.py`：利用 GPT-4o-mini 將 Kaggle 財報問答對翻譯為繁體中文，並確保金融術語對齊。
    *   實作 `src/data_pipeline/synthesizer.py`：利用 Self-Instruct 方法合成「Thinking (CoT) + Tool-Calling」訓練數據。
    *   建立測試用數據集 `data/raw/financial-q-and-a-10k.csv`。

---

### ⚠️ 遇到問題與解決方法

#### 3. 需求變更導致架構調整
*   **問題描述**：初始計畫 V1 較為泛用（偏向 SQL），而新參考文件要求精確的數值計算工具呼叫與高級檢索策略。
*   **解決方法**：立即更新計畫書為 V2，重新定義數據合成管線與評估標準，並同步調整檔案預留位置，確保後端實作不偏離最終業務目標。

---

### 🚀 目前進度總結
*   **當前階段**：計畫 V2 更新完成，環境與檔案結構已就緒。
*   **下一目標**：開始執行 V2 第一階段「數據管線與在地化」。
