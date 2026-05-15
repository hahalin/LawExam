# 全聯面談準備 — 建議回答

> 職缺：C# 軟體工程師（承攬駐點大直）
> 發案公司：越世實業 → 甲方：全聯福利中心
> 月薪：80,000 ~ 100,000

---

## 一、技術問題

### Q1：講一下你最近做的專案，架構怎麼設計的？

目前在世界先進半導體駐點，主導 VB6 桌面程式轉換為 Web 應用。後端用 Spring Boot + JPA 對接 Oracle，前端用 Angular + PrimeNG。架構是前後端分離，API 採 RESTful 設計，搭配 Oracle Stored Procedure 處理複雜商業邏輯。之前在長榮航空做地勤排班系統，後端是 ASP.NET WebAPI，ORM 同時用 Dapper 跟 Entity Framework，前端是 ReactJS + Tailwind。

> **追問：有沒有 .NET Core 經驗？**
> 之前用的是 ASP.NET MVC 和 WebAPI（.NET Framework），.NET Core 的 DI、Middleware pipeline、Configuration 這些概念我都有研究，實際上架構觀念是相通的，上手不會有問題。

---

### Q2：Entity Framework 跟 Dapper 差異？什麼場景用哪個？

在長榮排班系統裡兩個都有用。EF 適合 CRUD 為主的場景，用 Code First 或 DB First 快速建模，開發效率高，Change Tracking 方便。Dapper 適合效能敏感或 SQL 複雜的場景，像排班系統裡有些跨多表的統計查詢，用 Dapper 寫原生 SQL 效能好很多，也比較好調校。

實務上我會混搭 — 簡單 CRUD 用 EF，複雜報表查詢用 Dapper。

---

### Q3：寫 API 時怎麼處理驗證、錯誤回傳？

驗證分兩層 — Model 層用 Data Annotation（`[Required]`、`[StringLength]`）做基本欄位驗證，商業邏輯驗證放在 Service 層。錯誤回傳統一用 middleware 或 filter 攔截，回傳一致的 JSON 格式，包含 error code 和 message，避免直接把 exception stack trace 丟給前端。HTTP status code 也會區分 400（參數錯）、404（找不到）、500（系統錯誤）。

---

### Q4：SQL 效能不好怎麼排查？

我在 Oracle 跟 SQL Server 都有處理過效能問題。基本步驟是先看 Execution Plan，找出 Full Table Scan 或 Nested Loop 的瓶頸。常見處理方式包括加適當的 Index、改寫子查詢為 JOIN、避免 SELECT *、用 EXISTS 取代 IN。在 Oracle 還會看 AWR Report 抓 Top SQL。之前在世界先進做 VB6 轉換時，就處理過 ORA-01000 cursor leak 的問題，是因為 connection/statement 沒有正確 close。

---

### Q5：微服務之間怎麼溝通？

我目前的專案是單體架構，但對微服務的概念有深入了解。同步通訊用 REST API 或 gRPC，適合需要即時回應的場景。非同步用 Message Queue（像 Kafka 或 RabbitMQ），適合解耦、削峰的場景，例如訂單建立後發事件通知庫存服務。

非同步通訊要注意的是 at-least-once delivery 的問題，消費端要做冪等處理，避免重複消費造成資料錯誤。

---

### Q6：DDD、CQRS 有了解嗎？

有研究過概念。DDD 的核心是用 Bounded Context 劃分領域邊界，每個 Context 有自己的 Ubiquitous Language，避免不同業務領域的模型互相污染。CQRS 是把讀寫分離，Command 端負責寫入和驗證商業規則，Query 端可以用 denormalized 的 view 或獨立 DB 來最佳化查詢效能。

實務上我目前還沒有在正式專案中完整實作 DDD，但在做 VB6 轉 Web 時，有把不同 Form 的商業邏輯拆成獨立的 Service module，概念上類似 Bounded Context 的劃分。

---

### Q7：有用過 AWS 嗎？

過去主要在地端環境開發，AWS 沒有正式的專案經驗。但對 container 化的概念有基本認知 — Docker image 打包、Registry 管理、K8s 部署的流程。CI/CD 方面，之前用 GitLab 做版本控管，了解 pipeline 建構、自動測試和部署的概念。

我的學習能力蠻快的，上手新的雲端工具對我來說不會是障礙。

---

## 二、非技術問題

### Q8：你能待多久？

我做專案習慣有頭有尾，之前在前進國際駐點都是一年以上的週期。我希望至少做完一個完整的 Sprint cycle，熟悉系統後能持續交付。只要專案有需要、合作順暢，我沒有時間上的限制。

---

### Q9：能配合加班嗎？

可以配合。我之前在半導體廠駐點也有過趕上線的經驗，理解專案有些階段會比較密集。想確認一下，全聯這邊通常是哪些時間點會比較忙？加班的頻率大概是？

---

### Q10：你習慣怎麼跟團隊協作？

我習慣主動溝通。每天 standup 報進度和 blocker，遇到規格不清的會直接找 PM 或 SA 確認，不會自己猜。程式碼會透過 PR review 確保品質。之前在世界先進，需求變動很快，我養成了先確認需求邊界再開始寫 code 的習慣，避免做白工。

---

### Q11：為什麼選擇承攬？

我過去十幾年大部分都是專案制的工作型態，習慣這種模式。好處是可以接觸不同產業的系統，像我做過半導體、航空、銀行、面板，每個領域的 domain knowledge 都不同，對我來說是很好的學習和累積。承攬讓我可以專注在技術交付上，這是我最擅長的事。

---

### Q12：你的技術棧主要是 C#，但現在在做 Spring Boot？

對，目前這個專案因為客戶端技術選型是 Spring Boot，所以我同時在寫 Java。但我的主力還是 C#，從 WebForm、MVC 到 WebAPI 都有完整經驗。語言只是工具，ASP.NET 跟 Spring Boot 在架構上非常類似 — Controller/Service/Repository 分層、DI 注入、ORM 映射，觀念都是相通的。回到 .NET Core 對我來說反而更熟悉。

---

## 三、你要主動問的問題

1. 「我會加入哪個產品線的團隊？」（電商 PXGo / POS / 會員 / 物流 / 供應鏈？）
2. 「目前這個系統是新建還是重構？技術債多嗎？」
3. 「團隊目前幾個人？承攬跟正職的比例？」
4. 「開發環境有什麼限制？能用自己的工具嗎？」
5. 「Sprint 週期多長？上線頻率？」

---

## 四、你的最大優勢

1. **11 年以上駐點經驗** — 做過半導體、航空、銀行、面板，甲方溝通零障礙
2. **C# + Angular + Oracle 全端** — 跟 JD 高度吻合
3. **VB6 轉 Web 的現代化遷移經驗** — 證明能處理 legacy 系統
4. **AI 輔助開發（Copilot Agent）** — 展現持續學習和效率意識

---

## 五、需要補強的點

| 弱項 | 應對策略 |
|---|---|
| .NET Core（vs .NET Framework） | 強調概念相通，上手快 |
| 微服務 / AWS / DDD | 誠實說沒實作過，但展現理解力 |
| Scrum / Jira | 了解流程，之前用類似方式管理 |

---

## 六、注意事項

- **不要跟全聯談薪資** — 薪資是你跟越世談的，全聯只負責技術把關
- **不要批評前公司或前專案**
- **不會的技術不要硬掰** — 說「這部分我沒實際做過，但我的理解是...」
- **不要強調想遠端** — 等進去穩定了再談
- **穿著** — polo 衫/襯衫 + 長褲，不用西裝
- **提早 10 分鐘到** — 確認全聯總部大直的正確地址和樓層
