# 🏕️ 夏令营追踪器

> 粘贴通知文本，AI 自动提取关键信息，按报名截止日期排序管理所有夏令营。

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 功能

- **智能提取**：粘贴夏令营通知原文，调用 AI 自动识别学校、学院、项目名称、报名时间、活动时间
- **截止日期追踪**：倒计时方框实时显示剩余天数，状态徽章区分「报名中 / 即将截止 / 未开始 / 已过期」
- **活动日历**：12 个月纵览，活动日期按营地数量标注深浅绿色，悬浮显示对应营地信息
- **双格式存储**：数据同时写入 `camps.csv`（可直接用 Excel 打开）和 `camps.json`
- **去重保护**：项目名称 + 报名截止日期相同时拒绝重复添加
- **一键启停**：macOS 双击 `start.command` / `stop.command` 启动或关闭服务

## 界面预览

| 追踪列表 | 活动日历 |
|---------|---------|
| 按截止日期排序的卡片列表，含倒计时方框 | 双列月历，绿色深度随营地数量变化 |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/songguozhen/SummerCamp.git
cd SummerCamp
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

项目使用[硅基流动](https://siliconflow.cn)的 DeepSeek-V3 模型进行信息提取。

在项目根目录创建 `.env` 文件：

```
SILICONFLOW_API_KEY=your_api_key_here
```

> 在硅基流动控制台申请 API Key：https://cloud.siliconflow.cn/account/ak

### 4. 启动服务

**方式一：双击启动（macOS）**

直接双击项目目录中的 `start.command`，服务启动后自动打开浏览器。

**方式二：命令行**

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

然后打开浏览器访问 [http://localhost:8000](http://localhost:8000)

### 5. 关闭服务

双击 `stop.command`，或在终端按 `Ctrl+C`。

## 使用方法

1. 在左侧文本框粘贴夏令营通知原文
2. 点击「✨ 提取信息」，等待 AI 解析
3. 在确认表单中核对并修改字段，点击「💾 保存」
4. 右侧列表按报名截止日期自动排序展示
5. 切换到「📅 活动日历」页查看所有营地的活动时间分布

## 项目结构

```
SummerCamp/
├── main.py              # FastAPI 后端（API 提取 + CRUD）
├── requirements.txt     # Python 依赖
├── start.command        # macOS 一键启动脚本
├── stop.command         # macOS 一键关闭脚本
├── static/
│   └── index.html       # 单页前端（纯 HTML/CSS/JS）
└── data/                # 自动生成，勿提交
    ├── camps.csv        # 主数据文件
    └── camps.json       # 同步备份
```

## 数据字段说明

| 字段 | 说明 |
|------|------|
| `school` | 大学 / 高校名称 |
| `institute` | 学院 / 研究所名称 |
| `program_name` | 夏令营项目名称 |
| `registration_start` | 报名开始日期 |
| `registration_end` | 报名截止日期（主排序键） |
| `activity_start` | 活动开始日期 |
| `activity_end` | 活动结束日期 |
| `notes` | 备注 |

## 依赖

- [FastAPI](https://fastapi.tiangolo.com/) — Web 框架
- [Uvicorn](https://www.uvicorn.org/) — ASGI 服务器
- [openai](https://github.com/openai/openai-python) — 调用硅基流动 API（兼容 OpenAI 格式）
- [python-dotenv](https://github.com/theskumar/python-dotenv) — 读取 `.env` 配置

## 注意事项

- `.env` 文件已在 `.gitignore` 中排除，请勿手动提交
- `data/` 目录已在 `.gitignore` 中排除，数据仅保存在本地
- 本工具为本地个人使用设计，不含身份认证，请勿暴露到公网

## License

MIT
