# 医学知识库系统 - 简化适配版
# System Operations (Linux Adapter)

## 系统铁律 (SYS-001 ~ SYS-016)

### SYS-001: 证据先于判断
任何医学主张必须有证据支撑，禁止无证据的绝对化表述。

### SYS-002: 合规边界
- 不得超适应症宣传
- 不得使用治愈/根治等绝对化用语
- 非头对头比较需标注限制

### SYS-003: 语域控制
根据受众选择 Register 等级 (R1-R5)。

### SYS-004: 中文表达底线
避免翻译腔，使用地道中文表达。

### SYS-005 ~ SYS-016: [其他约束...]

## 文档地图

```
V2medical-kb-system/
├── skills/              # Skill 定义
│   ├── medical-content-router/
│   ├── medical-database-query/
│   ├── medical-opinion-generator/
│   ├── medical-article-reviewer/
│   └── medical-writing/
├── project_standards/   # 项目标准
└── docs/               # 文档
```

## 日志机制 (DOC-017)

- 项目级日志: `logs/{project_id}/`
- 运行摘要: `logs/summary/`

## Workflow Gate

所有医学内容请求必须通过 `medical-content-router` 入口。
