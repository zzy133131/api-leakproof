# 🔑 API LeakProof

> 实时监控你的 API Key，防止被第三方平台中转盗用。

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()

## 解决的问题

市面上有很多第三方 API 接入平台（API 中转站、聚合平台等），在这些平台上填入自己的 API Key 存在泄露风险——你的 Key 可能被平台开发者拿去做免费中转。**API LeakProof** 通过本地代理 + 官方用量对比的方式，实时检测异常调用。

## 工作原理

```
你的应用 → 本地代理(localhost:8080) → 真实 API 提供商
                    │                        │
                    ▼                        ▼
              代理记录(A)              官方用量(B)
                    │                        │
                    └──── 对比 A vs B ───────┘
                              │
                       差异 > 0 → 🚨 告警
```

1. **本地代理** 记录你发出的每一次 API 调用
2. **定时拉取** 官方用量数据
3. **对比差异** — 官方比代理多出来的调用 = 别人在盗用你的 Key
4. **即时告警** — 异常 IP、用量差异、费用暴涨，macOS 原生通知

## 功能

- ✅ 本地 HTTP 代理，拦截并记录所有 API 调用
- ✅ 多平台支持：OpenAI / Claude / DeepSeek / Qwen / 自定义
- ✅ 多 Key 同时监控
- ✅ IP 异常检测：发现非本人 IP 的调用
- ✅ 用量差异检测：官方用量 vs 代理记录的调用次数
- ✅ 费用异常告警
- ✅ macOS 原生通知中心告警
- ✅ 简洁暗色 GUI（PySide6）

## 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/api-leakproof.git
cd api-leakproof

# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -e .

# 启动
api-leakproof
# 或者
python app/main.py
```

## 使用

1. 启动应用，代理自动运行在 `localhost:8080`
2. 点击 **+ 添加 Key**，填入你的 API Key 和对应平台
3. 在你的 API 客户端中，将代理地址设为 `http://localhost:8080`
4. 应用会自动监控，发现异常时推送 macOS 通知

### 配置 API 客户端使用代理

**Python (openai SDK):**
```python
import openai
openai.proxy = "http://localhost:8080"
```

**Python (requests):**
```python
requests.post(
    "https://api.openai.com/v1/chat/completions",
    proxies={"https": "http://localhost:8080"},
    ...
)
```

**环境变量:**
```bash
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
```

## 技术栈

- **GUI:** PySide6 (Qt for Python)
- **代理:** Python http.server + urllib
- **数据库:** SQLite
- **调度:** APScheduler
- **加密:** cryptography (Fernet/AES-128)
- **通知:** macOS osascript + Notification Center

## 项目结构

```
api-leakproof/
├── app/            # PySide6 GUI
├── proxy/          # 本地代理引擎
├── monitor/        # 监控 & 告警引擎
├── db/             # 数据层 (SQLite)
├── shared/         # 公共类型
├── config/         # 配置
└── tests/          # 测试
```

## 开发计划

- [ ] HTTPS 代理支持（MITM）
- [ ] 更完善的各平台官方用量 API 对接
- [ ] 菜单栏托盘图标
- [ ] Windows / Linux 支持
- [ ] 自动 Key 轮换建议
- [ ] 统计分析面板

## License

MIT © 2025
