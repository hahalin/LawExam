## C# MVC → Java Spring Boot 轉換建議

### 概念對應表（直接映射）

| C# MVC | Spring Boot | 說明 |
|--------|-------------|------|
| `Controller` | `@RestController` | 完全相同概念 |
| `[HttpGet]` / `[HttpPost]` | `@GetMapping` / `@PostMapping` | 路由標註 |
| `IActionResult` | `ResponseEntity<T>` | 回傳型別 |
| `[FromBody]` | `@RequestBody` | 接收請求本體 |
| `DbContext` | `JpaRepository` | 資料存取層 |
| `appsettings.json` | `application.properties` / `application.yml` | 設定檔 |
| `Startup.cs` / `Program.cs` | `@SpringBootApplication` + `@Bean` | 應用程式進入點 |
| `Middleware` | `Filter` / `Interceptor` | 請求攔截 |
| `[Authorize]` | `@PreAuthorize` | 權限控制 |
| `IServiceCollection` DI | `@Autowired` / `@Bean` | 依賴注入 |

---

### 最需要調整的心態

#### 1. 分層架構更嚴格
```
C# MVC:  Controller → Service (選配) → DB
Spring:  Controller → Service → Repository → Entity  ← 強制分層
```

#### 2. 標註（Annotation）取代 Attribute
```csharp
// C#
[Required]
[StringLength(100)]
public string Name { get; set; }
```
```java
// Java
@NotNull
@Size(max = 100)
private String name;
```

#### 3. Lombok 取代自動屬性
```csharp
// C# 自動屬性
public string Name { get; set; }
```
```java
// Java + Lombok（必學）
@Data           // getter + setter + toString + equals
@Builder        // Builder 模式
@NoArgsConstructor
@AllArgsConstructor
private String name;
```

#### 4. 沒有 LINQ，改用 Stream API
```csharp
// C# LINQ
var result = list.Where(x => x.Age > 18).Select(x => x.Name).ToList();
```
```java
// Java Stream
List<String> result = list.stream()
    .filter(x -> x.getAge() > 18)
    .map(x -> x.getName())
    .collect(Collectors.toList());
```

---

### 學習優先順序

```
第一週：Java 基礎語法差異（泛型、Stream、Optional）
         ↓
第二週：Spring Boot 專案結構 + @Component/@Service/@Repository
         ↓
第三週：JPA/Hibernate（對應 Entity Framework）
         ↓
第四週：Spring Security（對應 [Authorize]）
         ↓
第五週：Maven / Gradle（對應 NuGet + .csproj）
```

---

### 實用工具對應

| 用途 | C# | Java |
|------|----|------|
| 套件管理 | NuGet | Maven / Gradle |
| 測試 | xUnit / NUnit | JUnit 5 + Mockito |
| Mapper | AutoMapper | MapStruct |
| 日誌 | Serilog / NLog | SLF4J + Logback |
| API 文件 | Swagger (Swashbuckle) | SpringDoc (OpenAPI) |
| Lint | Roslyn Analyzer | Checkstyle / SpotBugs |

---

### 最大心智負擔（預先準備）

1. **泛型型別擦除**：Java 執行期不保留泛型型別，有時需繞路處理
2. **checked exception**：Java 強迫處理例外，C# 沒有這概念
3. **`null` 處理**：Java 沒有 `?.` 操作符，需用 `Optional` 或手動判斷
4. **Build 速度**：Maven 第一次下載依賴很慢，要有心理準備

---

### 最快上手路徑

> 直接用 **Spring Initializr**（[start.spring.io](https://start.spring.io)）建一個專案，對照你熟悉的 C# MVC 專案一一找到對應的東西，學習曲線會大幅縮短。

你的 C# MVC 經驗非常值錢，Spring Boot 的分層設計哲學幾乎一樣，語法差異 1-2 週就能適應。

## AI 生成程式碼的管理與優化建議

### 核心問題認知

```
AI 生成的程式碼風險：
✅ 快速產出  但  ❌ 風格不一致
✅ 功能正確  但  ❌ 邊界條件可能遺漏
✅ 有結構    但  ❌ 技術債累積快
```

---

## 建議策略

### 1. 建立「Skills / 規範檔」作為 AI 的約束框架

> 這也是本專案 skills 的設計初衷

```
沒有規範  → AI 每次產出風格不同 → 難以維護
有規範    → AI 照規範產出       → 可預期、可審查
```

**做法：**
- 定義命名規範、分層規範、錯誤處理規範
- 每次 prompt 強制引用規範檔
- 規範版本控制在 Git 中

---

### 2. Code Review 分層檢查清單

#### 🔴 必查（功能正確性）
- [ ] 邊界條件（null、空陣列、負數）
- [ ] 例外處理是否完整
- [ ] SQL 是否有 N+1 問題
- [ ] 權限控制是否落實

#### 🟡 應查（可維護性）
- [ ] 命名是否語意清楚
- [ ] 方法是否單一職責（超過 30 行要懷疑）
- [ ] 是否有重複邏輯（DRY 原則）
- [ ] 魔法數字是否抽成常數

#### 🟢 建議查（效能優化）
- [ ] 查詢是否有適當 index
- [ ] 大量資料是否有分頁
- [ ] 是否有不必要的 API 呼叫

---

### 3. 工具鏈整合（自動化管理）

| 工具 | 用途 | 說明 |
|------|------|------|
| **SonarQube** / SonarLint | 靜態分析 | 偵測 bug、smell、漏洞 |
| **Checkstyle** | 風格一致性 | 強制命名/格式規範 |
| **SpotBugs** | Bug 偵測 | 空指針、資源洩漏 |
| **JaCoCo** | 測試覆蓋率 | 確保 AI 生成的邏輯有測試覆蓋 |
| **Git Pre-commit Hook** | 提交前把關 | 阻擋不符規範的程式碼進入 repo |

```bash
# CI Pipeline 建議流程
git push
  → Lint / Checkstyle
  → Unit Test + Coverage ≥ 80%
  → SonarQube 掃描
  → Build
  → Deploy
```

---

### 4. AI 生成程式碼的特定風險點

| 風險 | 症狀 | 對策 |
|------|------|------|
| **幻覺 API** | 呼叫不存在的方法 | 編譯期即可發現，確保 CI 有 build |
| **過度設計** | 產出複雜 abstract/factory | 規範中明訂「禁止過度抽象」 |
| **安全漏洞** | SQL injection、XSS | OWASP 掃描 + input validation 規範 |
| **測試不足** | 只有 happy path | 規範要求至少 3 情境（正常/異常/邊界） |
| **硬編碼** | 密碼/IP 寫死在程式碼 | Git secret scan（如 truffleHog） |

---

### 5. 客戶可見的管理儀表板建議

```
建議提供給客戶的可視化指標：

📊 程式碼品質分數   （SonarQube Dashboard）
📈 測試覆蓋率趨勢   （JaCoCo Report）
🐛 已知技術債列表   （SonarQube Issues）
🔒 安全漏洞數量     （Dependency Check）
📝 變更日誌         （Git Changelog）
```

---

### 6. 實際工作流建議

```
需求 → Claude Code 生成
         ↓
    開發者 Review（用清單）
         ↓
    SonarLint 本地掃描
         ↓
    git commit（pre-commit hook）
         ↓
    CI 自動掃描 + 測試
         ↓
    Tech Lead 最終審查
         ↓
    Merge & Deploy
```

---

### 一句話總結

> **AI 生成程式碼的品質管理，關鍵不在「限制 AI」，而在「建立可驗證的規範 + 自動化把關機制」**，讓人只需審查「AI 做對了嗎」而不是「AI 做了什麼」。
