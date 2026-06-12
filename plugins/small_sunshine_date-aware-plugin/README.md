# 日期感知插件 v2.0.0

让麦麦能够更准确感知节假日信息的插件

## 关于此分支

这是一个适配新版 MaiBot SDK 的分支版本。

- **源项目**: [heitiehu-beep/date_aware_plugin](https://github.com/heitiehu-beep/date_aware_plugin)
- **原作者**: [heitiehu-beep](https://github.com/heitiehu-beep)
- **分支维护者**: [small_sunshine](https://github.com/MCYXG233)
- **新仓库**: [MCYXG233/date_aware_plugin_New](https://github.com/MCYXG233/date_aware_plugin_New)

本分支旨在将原插件适配到 MaiBot v1.0.0+ 的新 SDK 架构。

## 功能特性

- 自动日期注入：每次对话时自动将当前日期信息注入到 LLM prompt
- 节假日识别：自动识别昨天、今天、明天的节假日
- 手动查询：通过 `/date` 命令查询当前日期信息
- 工具提供：提供 `get_date_info` 工具供其他插件调用

## 使用方法

### 手动查询

```
/date
```

返回格式示例：
```
昨天 | 12月31日 星期三
今天 | 1月1日 星期四【元旦】
明天 | 1月2日 星期五【元旦】
```

### 自动注入

插件会自动在每次对话时注入日期信息，无需手动触发。

## 配置选项

在 `config.toml` 中配置：

```toml
[plugin]
enabled = true          # 是否启用插件

[date]
enable_llm_expand = false   # 是否启用 LLM 扩展日期信息
llm_model = "replyer"       # 使用的模型名称
```

## 工作原理

插件使用 `@Tool` 和 `@Command` 装饰器声明组件，通过 `PluginContext` 与 MaiBot 主进程通信。

## 节假日数据

节假日数据来源于 holiday-calendar 项目，通过 unpkg CDN 获取。

备用节假日列表（固定节日）：
- 元旦 (01-01)
- 情人节 (02-14)
- 妇女节 (03-08)
- 愚人节 (04-01)
- 劳动节 (05-01)
- 青年节 (05-04)
- 儿童节 (06-01)
- 建党节 (07-01)
- 建军节 (08-01)
- 教师节 (09-10)
- 国庆节 (10-01)
- 圣诞节 (12-25)

## 组件说明

| 组件类型 | 名称 | 说明 |
|---------|------|------|
| Tool | get_date_info | 获取日期信息的工具 |
| Command | date | /date 命令处理器 |

## 作者

- 原作者: [heitiehu-beep](https://github.com/heitiehu-beep)
- 分支维护者: [small_sunshine](https://github.com/MCYXG233)

## 许可证

MIT License
