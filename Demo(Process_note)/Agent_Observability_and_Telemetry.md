---
up: "[[MOC_01_Machine_Learning]]"
source: "[[06_finish/AI/(重要) Agent Quality]]"
note_type: "mechanism"
topic:
  - agent_infrastructure
  - observability
keywords:
  - Observability
  - Logs
  - Traces
  - Metrics
  - OpenTelemetry
  - Span
summary: "解析 AI Agent 可觀測性的核心三支柱，透過記錄完整決策軌跡與因果關係，實現深度除錯與系統效能監控。"
---

# 建立 Agent 可觀測性三支柱與高風險攔截機制

## 📌 核心概念與痛點 (Core Concept & Pain Points)
在傳統軟體工程中，系統行為通常是決定性的（Deterministic），類似於固定路線的送貨卡車（Delivery truck），只需依賴「監控（Monitoring）」來確認服務是否中斷（Crash 就是 Fail）。然而，AI Agent 具備非決定性（Non-determinism），其運作更像是 F1 賽車，必須在動態環境中做出細緻判斷。

由於 Agent 的失敗往往是「表面成功」的隱性失效（Insidious failures）——例如 API 回傳 `200 OK` 且輸出看似合理，但實際上發生了幻覺或邏輯漂移——單純的終端輸出檢查已無法建立信任。因此，系統必須導入「可觀測性（Observability）」。如果說監控是看「餐點有沒有準時出菜」，可觀測性就是「把廚房透明化」，讓開發者能夠追問「為什麼這一步會這樣做」，從而捕捉完整的決策軌跡（Trajectory）。

## ⚙️ 系統架構與運作機制 (Architecture & Mechanisms)
可觀測性的實作依賴於底層的三大支柱（Logs、Traces、Metrics），並搭配針對高風險操作的攔截工作流（Interruption Workflow）：

1. **Logs（事實的原子記錄）**
   - **定義**：原子事件的時間戳日記，建議採用結構化的 JSON 格式。
   - **內容**：必須包含 Prompt / Response、中間推理過程、Tool 的 Input / Output / Error，以及內部狀態的變化。

2. **Traces（因果故事線）**
   - **定義**：將分散的 Logs 串聯成端到端（End-to-End）的故事線，揭露「為什麼會出錯」的因果關係。
   - **機制**：在分散式系統的標準（如 OpenTelemetry）下，Trace 代表「一個任務的完整故事」，而 Span 則是故事裡的「一個章節」（例如一次 LLM Call 或一次 Tool Call）。透過 `Trace ID` 與 `Span ID` 的 Context propagation，系統能跨元件追蹤同一條請求的決策路徑，這對於 Multi-step Agent 的除錯不可或缺。

3. **Metrics（聚合總覽）**
   - **定義**：並非新的資料型態，而是由 Logs 與 Traces 聚合計算出的總體健康分數。
   - **分類**：
     - **System Metrics（面向 SRE / Ops）**：包含 Latency（如 $P_{50}, P_{99}$ 分位數，更能反映尖峰壓力）、Error rate、Tokens per task、API cost、Task completion rate、Tool usage frequency。
     - **Quality Metrics（面向 DS / PM / AgentOps）**：包含 Correctness、Trajectory adherence、Safety、Helpfulness / Relevance（通常需要依賴 Golden set 或 LLM-as-a-Judge 來計算）。

4. **高風險攔截機制（Interruption Workflow / HITL）**
   - 針對高風險動作（如 `execute_payment`、發送敏感 Email、刪除資料庫等），系統必須實作 Human-in-the-Loop (HITL) 攔截。
   - **運作方式**：Agent 在執行該 Tool 前必須暫停（Pause），將當下的 Context 與擬定執行的參數送交人類審批（Approve / Reject），確保安全把關。

## 🔬 技術細節與深度推導 (Deep Dive)
- **OpenTelemetry 標準化**：可觀測性框架應遵循 OpenTelemetry 標準，將 Signals（Traces / Metrics / Logs）標準化。透過注入並傳遞 `Trace ID`，即使 Agent 呼叫了外部的 RAG 檢索服務或多個子 Agent，所有的 Span 都能精確對齊到同一條因果鏈上。
- **動態採樣策略（Dynamic Sampling）**：高粒度的全記錄（100% Tracing）非常昂貴且會增加系統延遲。實務上應採取動態採樣：
  - 成功的請求：僅抽樣記錄 10% 的 Trace。
  - 失敗或發生 Exception 的請求：強制記錄 100% 的 Trace，以確保有足夠的除錯燃料。
- **Guardrails 外掛架構（Plugin Architecture）**：
  - 安全機制應實作為 Before / After Callbacks。
  - **輸入端（Before）**：掃描並阻擋 Prompt Injection（防止攻擊者將惡意指令偽裝成正常輸入）。
  - **輸出端（After）**：掃描並過濾 PII（個人識別資訊，如身分證、信用卡號）外洩，確保機制可重用且可分層測試。

## ⚡ Trade-offs 與邊界條件 (Trade-offs & Limits)
- **成本與延遲**：過度詳細的 Logs 與 Traces 會導致儲存成本飆升，並拖慢系統的推理速度。必須依賴動態採樣來平衡可見度與效能。
- **資料隱私風險**：將所有 Prompt 與 Response 存入 Log 系統，等同於將使用者的敏感資料（PII）複製一份。若未在寫入前落實資料清洗（Data Scrubbing），將引發嚴重的合規與資安風險。
- **Metrics 的局限性**：System Metrics 無法反映回答的「真實價值」；即使 $P_{99}$ Latency 極低且 Error rate 為 0，Agent 仍可能快速地給出完全錯誤的幻覺內容。

## 🔗 相關知識連結 (Connections)
- [[AI_Agent_Application_and_Domain_Specific_Challenges]]：垂直領域的高風險應用對於準確度與可控性要求極高，直接呼應了實作 Interruption Workflow 與嚴格可觀測性的必要性。
- [[Agent_Tool_Design_and_Security_Patterns]]：Agent 工具設計需注重語義清晰與輸出精簡，並透過 Tool Retrieval 與外部治理層防禦 Confused Deputy 等越權風險。
- [[AI_Agent_Core_Mechanism_and_ReAct_Pattern]]：解析 AI Agent 有別於傳統 LLM 的主動執行機制與 Think-Act-Observe (ReAct) 核心循環。
- [[AgentOps_Evaluation_and_Interoperability]]：說明 Agent 系統的互操作性協議（A2A/MCP/x402）與透過雙指標驅動迭代的 AgentOps 評估機制。
- [[AgentOps_Production_Gap_and_Core_Pillars]]：論述 AI Agent 從原型到上線的特有挑戰，並確立 AgentOps 治理與自動化評估、部署、可觀測性三大支柱。
- [[Agent_Production_Operations_and_Security]]：解析 Agent 的漸進式部署策略、SAIF 多層安全防禦架構，以及結合可觀測性與斷路器的運行期維運機制。

## 🧠 關鍵問題反思 (Active Recall)
- 若一個 Multi-step Agent 在最終輸出給出了錯誤答案，你會如何利用 Trace ID 與 Span ID 來定位是 RAG 檢索失敗、Tool 呼叫參數錯誤，還是 LLM 的邏輯推導錯誤？
- 在設計一個負責自動退款的 Customer Service Agent 時，你會如何規劃其 Logging 策略與 Interruption Workflow，以兼顧營運效率與資金安全？
