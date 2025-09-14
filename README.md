# MiEmbybot 部署与使用指南

本项目是一个基于 Telegram 的 Emby 管理与互动机器人，支持账户管理、排行推送、观影奖励结算、红包、点播集成（MoviePilot，可选），并提供灵活的控制面板。

下文提供从零到一的详细部署步骤与常见问题排查建议。

---

## 功能概览

- 账户管理：注册/续期码、换绑 TG、重置密码、封存/解封等
- 观影榜与奖励：可定时推送播放榜，支持将观影时长按比例自动兑换币值
- 面板设置：在 Telegram 内在线修改开关、策略与价格等（含“观影换算比例”“线路设置”等）
- 用户自选线路：普通用户可在面板中选择个人适配的 Emby 线路（管理员可配置线路列表）
- Red Envelope/红包：支持群内红包功能（可禁用）
- MoviePilot 点播集成（可选）
- API 服务（可选）：对外提供查询/管理接口

---

## 环境要求

- Python 3.10+
- 操作系统推荐：Debian/Ubuntu/CentOS 亦可，Windows/macOS 仅用于开发测试
- 数据库：MySQL 5.7+/8.0（或兼容）
- Emby 服务器：确保可访问且 API 正常

---

## 获取代码与安装依赖

```bash
git clone https://github.com/JasonNF/MiEmbybot.git
cd MiEmbybot
pip install -r requirements.txt
```

---

## 准备配置文件 config.json

项目内提供了 `config_example.json` 作为参考示例（示例包含展示用占位符，非严格 JSON）。请在项目根目录创建你的实际配置 `config.json`，根据实际情况填写。

关键配置说明（节选）：

```json
{
  "bot_name": "你的BotSession名",
  "bot_token": "123456:ABCDEF-xxx",
  "owner_api": 123456,
  "owner_hash": "你的ApiHash",
  "owner": 111111111,
  "group": [-1001234567890],

  "money": "M币",
  "emby_api": "你的EmbyApiKey",
  "emby_url": "http://你的emby主机:8096",
  "emby_line": "https://emby.default.example",
  "emby_lines": [
    "https://emby.emby.com",
    "https://usemby.emby.com",
    "https://sgemby.emby.com"
  ],
  "emby_whitelist_line": null,

  "db_host": "localhost",
  "db_user": "root",
  "db_pwd": "password",
  "db_name": "miemby",
  "db_port": 3306,

  "emby_block": ["nsfw"],
  "extra_emby_libs": ["电视"],

  "open": {
    "stat": false,
    "all_user": 1000,
    "timing": 0,
    "tem": 0,
    "allow_code": true,
    "checkin": true,
    "exchange": true,
    "whitelist": true,
    "invite": false,
    "leave_ban": true,
    "uplays": true,
    "uplays_seconds_per_coin": 1800,
    "exchange_cost": 200,
    "whitelist_cost": 9999,
    "invite_cost": 200
  },

  "schedall": {
    "dayrank": true,
    "weekrank": true,
    "dayplayrank": false,
    "weekplayrank": false,
    "check_ex": true,
    "low_activity": false,
    "backup_db": false
  },

  "moviepilot": {
    "status": false,
    "username": null,
    "password": null,
    "access_token": null,
    "price": 1
  },

  "auto_update": {
    "status": true,
    "git_repo": "JasonNF/MiEmbybot",
    "commit_sha": null
  },

  "api": {
    "status": true,
    "http_url": "0.0.0.0",
    "http_port": 8838,
    "allow_origins": ["*"]
  }
}
```

> 安全与开源建议
>
> - 仓库已提供 `config.sample.json`，请以此为模板创建你的私有 `config.json`。
> - `.gitignore` 已忽略 `config.json`、`*.session`、`data/user_prefs.json`、`mysql_data/` 等敏感/本地文件，避免泄露。
> - 在公开仓库请勿提交包含真实凭据的配置。

要点：

- `open.uplays_seconds_per_coin` 控制观影时长兑换币值的比例（默认 1800 秒 = 1 币）。
- `emby_lines` 为可选线路列表，普通用户可在面板中自由切换；`emby_line` 为默认线路。
- `emby_whitelist_line` 可为白名单用户额外展示专属线路（仅展示，不会覆盖用户自选）。
- 使用 MySQL 时请确保数据库与账户已就绪，应用对库拥有读写权限。

---

## 启动（本机方式）

```bash
python3 main.py
```

首次运行会在 Telegram 中创建/初始化会话，按日志提示完成必要设置。

---

## 使用 Docker 运行

项目仓库包含 `Dockerfile` 与 `docker-compose.yml`，可按需选择：

1) Docker 构建与运行

```bash
docker build -t miembybot:latest .
docker run --name miembybot \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/log:/app/log \
  -p 8838:8838 \
  -d miembybot:latest
```

2) docker-compose 运行

```bash
docker-compose up -d
```

注意：请将真实的 `config.json` 挂载至容器内 `/app/config.json`，并映射 `data/` 与 `log/` 目录以持久化用户偏好与日志。

---

## 关键特性配置与面板操作

- 观影换算比例（秒/币）
  - 代码位置：`bot/scheduler/userplays_rank.py`
  - 配置项：`open.uplays_seconds_per_coin`
  - 面板入口：`/config` → “设置观影换算比例（秒/币）”

- 用户切换 Emby 线路
  - 管理员在 `config.json` 配置 `emby_lines` 列表
  - 普通用户面板：`🌐 线路切换` → 选择合适线路 → 服务器面板将显示个人已选线路
  - 相关代码：
    - `bot/modules/panel/member_panel.py`（入口与回调）
    - `bot/modules/panel/server_panel.py`（展示逻辑，优先显示用户自选线路）
    - `bot/func_helper/user_prefs.py`（存储用户偏好）

---

## 运行时目录与持久化

- `data/user_prefs.json`：保存用户线路选择等偏好（需写权限）
- `log/`：日志目录（导出日志、榜单ID 等）

---

## 常见问题排查

- 语法检查通过但无法启动
  - 检查 `config.json` 是否为严格 JSON 且字段完整
  - 检查数据库连接与 Emby API 可达性

- 无法连接 Telegram
  - 检查 `bot_token`、`owner_api`、`owner_hash`，以及服务器出网能力（代理可按需在配置中启用）

- 面板按钮不生效
  - 确认机器人已加入群并为管理员（如需）
  - 查看运行日志是否有报错

---

## 安全建议

- 请妥善保管 `bot_token`、数据库账户与 Emby API Key
- 如需对外开放 API（`api.status: true`），请在反向代理层做好访问控制与限流

---

## 许可证

本项目遵循仓库内 `LICENSE` 说明。
