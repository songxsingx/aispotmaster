# AI-Spot-Master 自动化开发提示词手册

> **版本**: v1.0  
> **更新时间**: 2025-11-16  
> **适用项目**: AI-Spot-Master 现货交易系统  
> **配合文档**: PROJECT_SPEC.md

---

## 📖 使用说明

本文档包含完整的AI自动化开发提示词序列，从项目初始化到高级功能扩展的所有阶段。

**使用方法**：
1. 按照Phase顺序（0→1→2→3→4+）执行
2. 每个Phase完成后必须验收通过才能继续
3. 直接复制对应的提示词给AI使用
4. AI会严格按照PROJECT_SPEC.md规范自动化开发

---

## 🎯 Phase 0: 项目初始化（2小时）

```
你是一个专业的全栈开发工程师。现在要开始开发AI-Spot-Master项目。

项目位置：/Users/gria/nextrade/ai-spot-master
参考规范：/Users/gria/nextrade/ai-spot-master/PROJECT_SPEC.md

执行 Phase 0: 项目初始化

目标：
1. 后端能启动: http://localhost:8000/docs 能访问
2. 前端能启动: http://localhost:5173 能访问
3. 前端能调用后端: GET /api/health 返回200
4. 数据库初始化: database.db 文件存在

必需文件（仅限以下）：
- backend/main.py (50行，FastAPI入口)
- backend/config.py (30行，配置管理)
- backend/requirements.txt (10行，依赖列表)
- backend/data/database.db (SQLite文件)
- frontend/package.json
- frontend/vite.config.ts
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx (50行，主组件)
- frontend/src/api/client.ts (30行，API客户端)

验收标准：
- [ ] 创建虚拟环境并安装依赖
- [ ] 启动后端，检查日志无错误
- [ ] 启动前端，浏览器无报错
- [ ] 前端调用API，Network显示200

禁止：
- 不要写业务逻辑
- 不要设计数据库schema
- 不要写任何策略代码
- 不要创建超过10个文件

严格按照 PROJECT_SPEC.md 第23.2章 Phase 0 规范执行。

完成后报告：
1. 创建了哪些文件
2. 后端启动命令和访问地址
3. 前端启动命令和访问地址
4. 验收结果（4个检查点）
```

---

## 🎯 Phase 1: 第一笔交易（1天）

```
继续开发 Phase 1: 第一笔交易

前置条件：Phase 0 已完成 ✅

目标：
1. 后端能连接Gate.io测试网
2. 后端能查询余额: GET /api/balance 返回USDT余额
3. 后端能执行买入: POST /api/trade/buy 返回订单详情
4. 前端显示余额: 显示USDT和BTC余额
5. 前端能下单: 点击"买入BTC"按钮，看到订单成功
6. 数据库有记录: trades表有1条记录

新增文件（仅限以下）：
- backend/core/exchange.py (80行，Gate.io封装)
- backend/api/__init__.py
- backend/api/trade.py (60行，交易API)
- backend/data/init.sql (20行，建trades表)
- frontend/src/pages/Trading.tsx (100行，交易页面)
- frontend/src/components/Balance.tsx (40行，余额显示)
- frontend/src/components/TradeButton.tsx (50行，交易按钮)

环境变量要求：
需要在 .env 文件中配置：
GATE_API_KEY=你的API密钥
GATE_API_SECRET=你的API密钥
GATE_TESTNET=true

验收标准：
- [ ] Postman测试GET /api/balance成功
- [ ] Postman测试POST /api/trade/buy成功
- [ ] 浏览器能看到余额数字
- [ ] 点击按钮能看到成功提示
- [ ] SQLite数据库有新记录

参考代码：PROJECT_SPEC.md 第23.2章 Phase 1 的 exchange.py 示例

禁止：
- 不要实现多个策略
- 不要实现AI功能
- 不要做图表
- 不要优化UI样式

完成后执行：
1. Postman验证所有API
2. 浏览器完整操作流程
3. 检查数据库记录
4. Git提交（参考PROJECT_SPEC.md 23.7规范）
```

---

## 🎯 Phase 2: 简单策略（2天）

```
继续开发 Phase 2: 简单策略

前置条件：Phase 1 已完成 ✅

目标：
1. 后端有策略引擎: POST /api/traders 创建交易员
2. 策略能运行: POST /api/traders/{id}/start 启动后台任务
3. 策略能交易: 5分钟内自动执行至少1笔买入或卖出
4. 前端能控制: 启动/停止按钮能用
5. 前端能监控: 实时显示交易记录
6. 数据库有traders表: 保存交易员配置

新增文件（仅限以下）：
- backend/strategy/__init__.py
- backend/strategy/base.py (40行，策略基类)
- backend/strategy/grid.py (100行，网格策略)
- backend/core/trader.py (150行，交易员引擎)
- backend/api/trader.py (80行，交易员API)
- frontend/src/pages/Traders.tsx (150行，交易员管理)
- frontend/src/components/TraderCard.tsx (80行，交易员卡片)
- frontend/src/components/TradeHistory.tsx (60行，交易历史)

数据库要求：
需要创建 traders 表，参考 PROJECT_SPEC.md 第4章数据库设计

验收标准：
- [ ] Postman创建交易员成功
- [ ] Postman启动交易员成功
- [ ] 后端日志显示策略运行
- [ ] 5分钟内数据库有新交易记录
- [ ] 浏览器能看到交易记录更新

参考代码：PROJECT_SPEC.md 第23.2章 Phase 2 的 grid.py 示例

禁止：
- 不要实现多个策略
- 不要优化策略参数
- 不要做复杂的风控
- 不要集成AI

完成后执行：
1. 启动策略运行5分钟
2. 观察日志和数据库
3. 浏览器验证UI功能
4. Git提交
```

---

## 🎯 Phase 3: 基础AI决策（3天）

```
继续开发 Phase 3: 基础AI决策

前置条件：Phase 2 已完成 ✅

目标：
1. 后端能调用DeepSeek: POST /api/ai/decide 返回AI决策
2. AI能分析市场: 传入价格数据，返回buy/sell/wait
3. 交易员使用AI: 策略执行时调用AI接口
4. 前端显示AI思考: 显示AI的决策理由
5. 数据库记录决策: ai_decisions表保存每次决策

新增文件（仅限以下）：
- backend/ai/__init__.py
- backend/ai/client.py (60行，DeepSeek客户端)
- backend/ai/prompts.py (80行，提示词模板)
- backend/api/ai.py (50行，AI API)
- backend/data/migrations/002_ai_decisions.sql (创建ai_decisions表)
- frontend/src/components/AIDecision.tsx (70行，AI决策显示)

环境变量要求：
需要在 .env 文件添加：
DEEPSEEK_API_KEY=你的API密钥

验收标准：
- [ ] Postman测试AI决策接口成功
- [ ] AI返回的JSON格式正确 (action, reasoning, confidence)
- [ ] 交易员日志显示AI决策
- [ ] 浏览器能看到AI的理由
- [ ] 数据库有AI决策记录

参考代码：PROJECT_SPEC.md 第23.2章 Phase 3 的 client.py 和 prompts.py 示例

提示词模板要求：
参考 PROJECT_SPEC.md 第20章 AI决策可视化设计
必须返回JSON格式：
{
  "action": "buy" | "sell" | "wait",
  "reasoning": "分析理由（50字以内）",
  "confidence": 0.0-1.0
}

禁止：
- 不要实现本地AI（Ollama）
- 不要做AI学习功能
- 不要做复杂的提示词优化
- 不要做AI对比测试

完成后执行：
1. 测试AI决策准确性
2. 观察AI建议是否合理
3. 验证完整交易流程（市场数据→AI决策→执行交易→记录结果）
4. Git提交

MVP完成标志：
✅ 系统能自动交易
✅ 能连续运行24小时不崩溃
✅ 有真实的交易记录
✅ AI能做出合理决策
✅ 可以向朋友演示
```

---

## 🚀 Phase 4+: 高级功能扩展

### 功能选择指南

参考 PROJECT_SPEC.md 第23.3章功能映射表，按优先级选择：

| 优先级 | 功能 | 对应章节 | 预计耗时 | 商业价值 |
|-------|-----|---------|---------|----------|
| P0 | 多策略支持 | 第八章 8.2-8.4 | 3天 | ⭐⭐⭐⭐⭐ |
| P0 | 资金分配管理 | 第十章 | 2天 | ⭐⭐⭐⭐⭐ |
| P0 | 风险控制 | 第十一章 | 2天 | ⭐⭐⭐⭐⭐ |
| P1 | 本地AI（Ollama） | 第十七章 17.2 | 1天 | ⭐⭐⭐⭐ |
| P1 | AI容错架构 | 第十七章 17.3 | 2天 | ⭐⭐⭐⭐ |
| P1 | 多交易员管理 | 第十九章 19.3 | 2天 | ⭐⭐⭐⭐ |
| P2 | 多交易所支持 | 第十九章 19.2 | 3天 | ⭐⭐⭐⭐ |
| P2 | AI思考链路展示 | 第二十章 20.1 | 2天 | ⭐⭐⭐ |
| P2 | 自适应提示词 | 第二十章 20.2 | 3天 | ⭐⭐⭐⭐ |
| P2 | 多交易员对比 | 第二十一章 | 2天 | ⭐⭐⭐ |
| P3 | AI进化学习（简单版） | 第二十二章 22.2 | 3天 | ⭐⭐⭐⭐ |
| P3 | 性能监控 | 第十三章 | 2天 | ⭐⭐⭐ |
| P3 | 告警系统 | 第十三章 13.4 | 1天 | ⭐⭐⭐ |

---

## 📝 高级功能通用提示词模板

```
实现高级功能：[功能名称]

参考：PROJECT_SPEC.md 第[X]章
优先级：[P0/P1/P2/P3/P4]
预计耗时：[X]天

按照 PROJECT_SPEC.md 第23.8 标准流程执行：

Step 1: 定位功能
- 在第23.3功能映射表中找到对应章节
- 阅读该章节的详细设计
- 理解功能的核心目标和技术要求

Step 2: 评估难度
- 预估开发时间
- 确认依赖的功能是否已完成
- 检查是否有更简单的实现方式
- 评估技术风险

Step 3: 创建任务清单
文件清单：
- [ ] 列出需要创建的文件（新建，预估行数）
- [ ] 列出需要修改的文件（修改，+预估行数）

验收清单：
- [ ] Postman验证后端API
- [ ] 浏览器验证前端功能
- [ ] 数据库验证数据正确性
- [ ] 功能完整性验证
- [ ] 性能验证（如适用）

Step 4: 开发实现
- 参考 PROJECT_SPEC.md 对应章节代码示例
- 遵循第二章命名规范
- 遵循第三章代码规范
- 遵循第五章API设计规范

Step 5: 验收提交
- 按照23.5 DoD标准验收
- 按照23.7规范提交Git
- 更新相关文档

禁止：
- 不要跳过验证步骤
- 不要过度设计
- 不要创建不必要的文件
- 不要偏离PROJECT_SPEC.md的设计

完成后报告：
1. 创建/修改了哪些文件
2. 验收结果（所有检查点）
3. 遇到的问题和解决方案
4. Git提交信息
```

---

## 🔧 具体功能实施示例

### 示例1：多策略支持（P0优先级）

```
实现高级功能：多策略支持

参考：PROJECT_SPEC.md 第八章 8.2-8.4
优先级：P0
预计耗时：3天

前置条件：Phase 0-3 已完成 ✅

目标：
1. 实现趋势策略（基于MA均线）
2. 实现动量策略（基于RSI指标）
3. 交易员创建时可以选择策略类型
4. 不同策略的收益可以独立统计和对比

按照 PROJECT_SPEC.md 第23.8 标准流程执行：

Step 1: 定位功能
- 阅读第八章策略引擎设计
- 理解策略基类接口
- 理解策略工厂模式

Step 2: 评估难度
- 预估时间：3天
- 依赖：Phase 2（网格策略）已完成 ✅
- 简化方案：先实现基础版本，参数使用默认值

Step 3: 创建任务清单

文件清单：
- [ ] backend/strategy/trend.py (新建，120行，趋势策略)
- [ ] backend/strategy/momentum.py (新建，100行，动量策略)
- [ ] backend/strategy/factory.py (新建，50行，策略工厂)
- [ ] backend/api/trader.py (修改，+30行，支持策略选择)
- [ ] backend/data/migrations/003_strategy_type.sql (新建，添加策略类型字段)
- [ ] frontend/src/components/StrategySelector.tsx (新建，80行)
- [ ] frontend/src/pages/Traders.tsx (修改，+20行)

验收清单：
- [ ] Postman测试创建趋势策略交易员
- [ ] Postman测试创建动量策略交易员
- [ ] 前端能选择策略类型
- [ ] 数据库正确记录策略类型
- [ ] 不同策略有不同的交易逻辑
- [ ] 策略收益能独立统计

Step 4: 开发实现
参考 PROJECT_SPEC.md 第八章代码示例：
- 8.2.2 趋势策略实现
- 8.2.3 动量策略实现
- 8.1.1 策略基类接口

技术要点：
1. 所有策略必须继承BaseStrategy
2. 必须实现analyze()和execute()方法
3. 使用ccxt获取市场数据计算指标
4. 策略参数可配置化

Step 5: 验收提交
- DoD检查：代码质量、功能验证、文档更新、可演示
- Git提交信息：
```
Feature: 添加多策略支持（趋势+动量）

参考：PROJECT_SPEC.md 第八章

✅ 趋势策略实现（MA均线）
✅ 动量策略实现（RSI指标）
✅ 策略工厂模式
✅ 前端策略选择
✅ 策略类型持久化

Files:
- backend/strategy/trend.py
- backend/strategy/momentum.py
- backend/strategy/factory.py
- frontend/src/components/StrategySelector.tsx
```

禁止：
- 不要实现过于复杂的策略
- 不要过度优化参数
- 不要添加超过3种策略
```

---

### 示例2：Binance交易所支持（P2优先级）

```
实现高级功能：Binance交易所支持

参考：PROJECT_SPEC.md 第十九章 19.2
优先级：P2
预计耗时：3天

前置条件：Phase 0-3 已完成 ✅

目标：
1. 支持Binance现货交易
2. 交易员创建时可以选择交易所
3. 同一个交易员可以在多个交易所运行
4. 不同交易所的数据独立统计

按照 PROJECT_SPEC.md 第23.8 标准流程执行：

Step 1: 定位功能
- 阅读第十九章 19.2 交易所适配器模式
- 理解ExchangeAdapter抽象接口
- 理解工厂模式

Step 2: 评估难度
- 预估时间：3天
- 依赖：Phase 1（GateIO适配器）已完成 ✅
- 简化方案：复用GateIO的代码结构，只需修改API调用

Step 3: 创建任务清单

文件清单：
- [ ] backend/core/exchange/__init__.py (新建，包初始化)
- [ ] backend/core/exchange/base.py (新建，60行，抽象基类)
- [ ] backend/core/exchange/gateio.py (重构，移动现有代码)
- [ ] backend/core/exchange/binance.py (新建，100行，Binance适配器)
- [ ] backend/core/exchange/factory.py (新建，40行，工厂类)
- [ ] backend/api/trader.py (修改，+15行，支持交易所选择)
- [ ] backend/data/migrations/004_exchange_type.sql (新建)
- [ ] frontend/src/components/ExchangeSelector.tsx (新建，80行)

验收清单：
- [ ] Postman测试Binance余额查询
- [ ] Postman测试Binance市价买入
- [ ] Postman测试Binance市价卖出
- [ ] 前端能切换交易所
- [ ] 数据库记录交易所类型
- [ ] 同一策略在不同交易所独立运行

Step 4: 开发实现
参考 PROJECT_SPEC.md 19.2 章节代码示例

关键代码结构：
```python
# backend/core/exchange/base.py
class ExchangeAdapter(ABC):
    @abstractmethod
    def get_balance(self, currency: str) -> Decimal
    
    @abstractmethod
    def create_market_buy_order(self, symbol: str, amount: Decimal) -> Dict

# backend/core/exchange/binance.py
class BinanceAdapter(ExchangeAdapter):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret
        })
        if testnet:
            self.exchange.set_sandbox_mode(True)
```

环境变量：
BINANCE_API_KEY=你的API密钥
BINANCE_API_SECRET=你的API密钥
BINANCE_TESTNET=true

Step 5: 验收提交
Git提交信息：
```
Feature: 添加Binance交易所支持

参考：PROJECT_SPEC.md 第十九章

✅ 交易所适配器基类
✅ Binance适配器实现
✅ 交易所工厂模式
✅ 前端交易所选择
✅ 多交易所数据隔离

Files:
- backend/core/exchange/binance.py
- backend/core/exchange/factory.py
- frontend/src/components/ExchangeSelector.tsx
```

禁止：
- 不要同时添加超过2个交易所
- 不要实现合约交易
- 不要做跨交易所套利
```

---

### 示例3：AI容错架构（P1优先级）

```
实现高级功能：AI容错架构

参考：PROJECT_SPEC.md 第十七章 17.3
优先级：P1
预计耗时：2天

前置条件：Phase 3（基础AI）已完成 ✅

目标：
1. 本地AI故障自动切换到云端API
2. 云端API故障使用规则引擎兜底
3. 故障自动恢复检测
4. 完整的故障日志记录

按照 PROJECT_SPEC.md 第23.8 标准流程执行：

Step 1: 定位功能
- 阅读第十七章 AI容错架构
- 理解三层防护体系
- 理解故障检测和恢复机制

Step 2: 评估难度
- 预估时间：2天
- 依赖：Phase 3（DeepSeek集成）已完成 ✅
- 技术难点：异常捕获、超时处理、状态管理

Step 3: 创建任务清单

文件清单：
- [ ] backend/ai/orchestrator.py (新建，150行，AI协调器)
- [ ] backend/ai/local_brain.py (新建，120行，本地AI客户端)
- [ ] backend/ai/rule_engine.py (新建，100行，规则引擎)
- [ ] backend/ai/client.py (修改，重构为cloud_brain.py)
- [ ] backend/utils/monitor.py (新建，80行，健康监控)
- [ ] backend/data/migrations/005_ai_health.sql (新建)

验收清单：
- [ ] 模拟本地AI故障，自动切换到云端
- [ ] 模拟云端API故障，使用规则引擎
- [ ] 本地AI恢复后自动切回
- [ ] 故障日志完整记录
- [ ] 监控接口正常工作

Step 4: 开发实现
参考 PROJECT_SPEC.md 17.3 章节代码示例

关键实现：
```python
# backend/ai/orchestrator.py
class AIOrchestrator:
    def make_decision(self, prompt: str, decision_type: str) -> Dict:
        # Layer 1: 本地7B
        if self._should_use_local():
            try:
                result = self.local_brain.call(prompt, timeout=30)
                return {'decision': result, 'backend': 'local', 'cost': 0.0}
            except Exception as e:
                self.failure_count['local'] += 1
                logger.warning(f"本地AI故障: {e}")
        
        # Layer 2: 云端API
        try:
            result = self.cloud_brain.call(prompt)
            return {'decision': result, 'backend': 'cloud'}
        except Exception as e:
            self.failure_count['cloud'] += 1
            logger.error(f"云端API故障: {e}")
        
        # Layer 3: 规则引擎
        result = self.rule_engine.make_decision(decision_type)
        return {'decision': result, 'backend': 'fallback'}
```

环境变量（可选）：
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
AI_AUTO_REPAIR=true

Step 5: 验收提交
测试场景：
1. 正常情况：本地AI工作
2. 本地故障：自动切云端
3. 全部故障：使用规则引擎
4. 恢复场景：自动切回本地

Git提交信息：
```
Feature: AI容错架构（三层防护）

参考：PROJECT_SPEC.md 第十七章

✅ AI协调器（三层防护）
✅ 本地AI客户端（Ollama）
✅ 规则引擎（兜底策略）
✅ 故障检测和恢复
✅ 健康监控接口

Files:
- backend/ai/orchestrator.py
- backend/ai/local_brain.py
- backend/ai/rule_engine.py
```

禁止：
- 不要过度复杂化故障处理
- 不要实现AI自动下载模型
- 不要做分布式AI调度
```

---

## ⚠️ 强制执行规则

在整个开发过程中，AI必须严格遵守以下规则：

### 1. Phase顺序强制

```
✅ 允许：Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4+
❌ 禁止：跳跃式开发（如：Phase 0 → Phase 3）
❌ 禁止：并行开发多个Phase
❌ 禁止：未验收就继续下一个Phase
```

### 2. 验收标准强制

每个Phase必须完成以下验收才能继续：

```
后端验收：
- [ ] Postman测试所有API端点
- [ ] 无语法错误
- [ ] 无运行时错误
- [ ] 日志输出正确

前端验收：
- [ ] 浏览器无报错
- [ ] 功能可用（点击有反应）
- [ ] 数据正确显示
- [ ] Network请求成功

数据库验收：
- [ ] 表结构正确
- [ ] 数据插入成功
- [ ] 查询返回正确
- [ ] 无数据冗余

集成验证：
- [ ] 前后端完整链路通畅
- [ ] 实际业务场景可用
- [ ] 可向他人演示
```

### 3. 代码规范强制

参考 PROJECT_SPEC.md 第三章，必须遵守：

```python
# Python规范
- 类名：PascalCase
- 函数名：snake_case
- 常量：UPPER_SNAKE_CASE
- 私有方法：_leading_underscore
- 类型注解：必须添加
- 文档字符串：公共API必须添加

# TypeScript规范
- 组件：PascalCase
- 函数：camelCase
- 常量：UPPER_SNAKE_CASE
- 接口：PascalCase
- 类型导入：必须显式声明

# 数据库规范
- 表名：snake_case（复数）
- 字段名：snake_case
- 索引：idx_表名_字段名
```

### 4. 文件数量控制

```
Phase 0: 最多10个文件
Phase 1: 新增最多7个文件
Phase 2: 新增最多7个文件
Phase 3: 新增最多5个文件
Phase 4+: 每个功能新增不超过10个文件

超过限制 = 过度设计 → 触发紧急刹车
```

### 5. 紧急刹车机制

当出现以下情况时，AI必须立即停止并报告：

```
🚨 刹车信号：
1. 连续2小时无进展
2. 同一个bug修复超过3次仍未解决
3. 代码行数超过计划2倍
4. 创建的文件超过计划数量
5. 开始怀疑"这个方案是否正确"
6. 需要重构已完成的代码
7. 出现循环依赖
8. 测试一直失败

刹车动作：
1. 停止编写新代码
2. 回滚到上一个可工作版本
3. 重新分析问题
4. 寻找更简单的方案
5. 向用户报告问题和建议
```

参考：PROJECT_SPEC.md 第23.6章

---

## 📊 进度报告模板

每个Phase完成后，AI必须提供以下格式的报告：

```
========================
Phase [X] 完成报告
========================

✅ 完成状态：[已完成/进行中/阻塞]

📁 创建的文件：
- backend/xxx.py (XX行)
- frontend/src/xxx.tsx (XX行)
...

🧪 验收结果：
后端验收：
- [✅/❌] Postman测试通过
- [✅/❌] 无错误日志
- [✅/❌] API返回正确

前端验收：
- [✅/❌] 浏览器无报错
- [✅/❌] 功能可用
- [✅/❌] 数据显示正确

数据库验收：
- [✅/❌] 表创建成功
- [✅/❌] 数据插入成功
- [✅/❌] 查询返回正确

🎯 功能演示：
1. 启动后端：cd backend && python main.py
   访问：http://localhost:8000/docs
2. 启动前端：cd frontend && npm run dev
   访问：http://localhost:5173
3. 测试流程：[描述完整操作步骤]

⚠️ 遇到的问题：
- [问题描述]
  解决方案：[如何解决]

📝 Git提交：
[提交信息内容]

⏭️ 下一步：
[下一个Phase或功能]
```

---

## 🎓 最佳实践建议

### 对AI开发者的建议

1. **渐进式开发**
   - 不要一次性实现太多功能
   - 每完成一个小功能就验证
   - 确保每一步都可工作

2. **验证驱动**
   - 先写API，用Postman验证
   - 再写前端，用浏览器验证
   - 最后集成测试

3. **简单优先**
   - 能用简单方案就不用复杂方案
   - 能硬编码就不要配置化
   - 能用库就不要自己实现

4. **参考规范**
   - 所有设计都参考PROJECT_SPEC.md
   - 不要自创新的架构
   - 不要偏离既定方案

5. **及时求助**
   - 遇到问题立即报告
   - 不要死磕超过2小时
   - 寻求用户确认方向

### 对项目管理者的建议

1. **严格验收**
   - 每个Phase必须亲自验证
   - 不要接受"差不多完成"
   - 要求完整演示

2. **控制范围**
   - 不要中途添加需求
   - 不要要求完美实现
   - 先保证MVP能用

3. **定期检查**
   - 每天检查进度
   - 每周review代码
   - 及时发现问题

4. **保持简单**
   - 抵制复杂化诱惑
   - 优先核心功能
   - 延迟优化时机

---

## 📚 参考文档索引

- **PROJECT_SPEC.md**: 完整项目规范
  - 第1-7章：基础规范
  - 第8-12章：业务模块
  - 第13-17章：系统架构
  - 第18-22章：扩展设计
  - 第23-24章：实施规范

- **关键章节快速索引**：
  - 命名规范：第2章
  - 代码规范：第3章
  - 数据库设计：第4章
  - API设计：第5章
  - 前端设计：第6章
  - 策略引擎：第8章
  - AI决策：第20章
  - 模块化设计：第19章
  - MVP实施：第23章

---

## 🔄 版本历史

- **v1.0** (2025-11-16)
  - 初始版本
  - 包含Phase 0-3完整提示词
  - 包含Phase 4+功能扩展模板
  - 包含3个详细实施示例
  - 包含强制执行规则
  - 包含进度报告模板

---

**✅ 提示词手册完成！**

现在你可以：
1. 直接复制对应Phase的提示词给AI使用
2. 使用通用模板添加自定义功能
3. 参考示例了解详细实施流程
4. 按照最佳实践确保项目成功

祝开发顺利！🚀
