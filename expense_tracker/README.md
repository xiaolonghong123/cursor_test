# 消费追踪工具

## 运行方式

1. **使用虚拟环境（推荐）**
   ```bash
   cd expense_tracker
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python main.py --help
   ```

2. **或先安装依赖后直接运行**
   ```bash
   pip install -r requirements.txt
   python main.py --help
   ```

## 命令示例

- `python main.py add 28.5 餐饮 --desc "午饭"` — 添加一条消费
- `python main.py list` — 列出所有记录
- `python main.py summary` — 按分类汇总
