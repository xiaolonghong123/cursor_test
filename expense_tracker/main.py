# main.py - 消费追踪命令行程序入口

# ---------- 导入模块 ----------
# asdict: 把 dataclass 实例转成字典（dict），便于序列化
from dataclasses import asdict
# 数据模型：从当前目录的 models 模块导入 Expense 类（类似 Java 的 import com.xxx.Expense）
from models import Expense
# 读写 JSON 文件（类似 Java 的 Gson/Jackson）
import json
# Path：面向对象的路径，比字符串路径更好用，跨平台
from pathlib import Path
# 类型注解，给函数参数/返回值标类型，方便阅读和 IDE 提示（类似 Java 泛型 List<Expense>）
from typing import List
# typer：基于 Click 的命令行框架，用装饰器定义子命令和参数（类似 Java 的 picocli）
import typer
# rich：终端美化输出，支持颜色、表格等
from rich.console import Console
from rich.table import Table

# ---------- 全局对象 ----------
# 创建一个“控制台”对象，后面用 console.print() 输出带样式的文字
console = Console()
# 创建 Typer 应用，所有子命令都挂在这上面；help 是运行 --help 时显示的说明
app = typer.Typer(help="建丰的个人消费追踪工具 🚀")
# 数据文件路径。Path("expenses.json") 表示当前目录下的 expenses.json
DATA_FILE = Path("expenses.json")


# ---------- 从文件加载所有消费记录 ----------
# -> List[Expense] 表示返回值类型是“Expense 的列表”
def load_expenses() -> List[Expense]:
    # 文件不存在就返回空列表 []（Python 里列表用方括号）
    if not DATA_FILE.exists():
        return []
    try:
        # with ... as f：打开文件，用完后自动关闭，类似 Java 的 try-with-resources
        # encoding="utf-8" 保证中文不乱码
        with DATA_FILE.open(encoding="utf-8") as f:
            # json.load(f) 从文件句柄 f 读入，解析成 Python 对象（这里是 list of dict）
            data = json.load(f)
            # 列表推导式：[表达式 for 变量 in 可迭代对象]
            # item 是字典，Expense(**item) 表示用字典的键值对作为关键字参数构造 Expense
            # 例如 item = {"id": 1, "amount": 28.5, ...} -> Expense(id=1, amount=28.5, ...)
            return [Expense(**item) for item in data]
    except Exception as e:
        # 捕获任意异常，e 是异常对象；rich 的 [red]...[/red] 表示红色输出
        console.print(f"[red]读取文件出错: {e}[/red]")
        return []


# ---------- 把所有消费记录写回文件 ----------
def save_expenses(expenses: List[Expense]):
    # "w" 表示写模式，会覆盖原文件
    with DATA_FILE.open("w", encoding="utf-8") as f:
        # asdict(e) 把 Expense 转成字典；[asdict(e) for e in expenses] 得到字典列表
        # json.dump 写入文件；ensure_ascii=False 让中文直接存中文；indent=2 缩进 2 格
        json.dump([asdict(e) for e in expenses], f, ensure_ascii=False, indent=2)


# ---------- 子命令：添加一条消费 ----------
# @app.command() 把这个函数注册为 Typer 的子命令，命令行里写 add 就会调这个函数
@app.command()
def add(
    # typer.Argument(...) 表示“必填的位置参数”，... 相当于“无默认值”
    amount: float = typer.Argument(..., help="消费金额（例如 28.5）"),
    category: str = typer.Argument(..., help="分类（餐饮/交通/购物 等）"),
    # typer.Option 表示“可选参数”，"" 是默认值，--desc 和 -d 是选项名
    description: str = typer.Option("", "--desc", "-d", help="描述/备注")
):
    """添加一条新消费（这里会出现在 add --help 的说明里）"""
    expenses = load_expenses()
    # max(可迭代对象, default=0)：取最大值，没有元素时用 0；(e.id for e in expenses) 是生成器表达式
    new_id = max((e.id for e in expenses), default=0) + 1
    try:
        exp = Expense(id=new_id, amount=amount, category=category, description=description)
        # list.append() 在列表末尾追加一个元素
        expenses.append(exp)
        save_expenses(expenses)
        # f"..." 是 f-string，花括号里可写表达式；:.2f 表示保留两位小数
        console.print(f"[green]添加成功！[/green] ID: {new_id} | {amount:.2f} 元 | {category}")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")


# ---------- 子命令：列出所有记录 ----------
# @app.command("list") 表示命令行里用 list 调用，但函数名可以叫 list_expenses（避免覆盖内置的 list）
@app.command("list")
def list_expenses():
    """列出所有消费记录"""
    expenses = load_expenses()
    # 空列表在布尔上下文中为 False，所以 not expenses 等价于 len(expenses)==0
    if not expenses:
        console.print("[yellow]还没有任何记录～[/yellow]")
        return

    # 用 rich 画表格
    table = Table(title="消费记录")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("金额", style="magenta")
    table.add_column("分类", style="green")
    table.add_column("描述")
    table.add_column("日期", style="blue")

    total = 0.0
    # for 变量 in 可迭代对象：遍历列表，e 依次是每条 Expense
    for e in expenses:
        # e.description or "-"：若 description 为空字符串则显示 "-"（空串在布尔上为 False）
        table.add_row(str(e.id), f"{e.amount:.2f}", e.category, e.description or "-", e.date)
        total += e.amount

    console.print(table)
    console.print(f"\n[bold]总消费：[/bold][red]{total:.2f} 元[/red]")


# ---------- 子命令：按分类汇总 ----------
@app.command()
def summary():
    """按分类统计月度汇总"""
    expenses = load_expenses()
    if not expenses:
        console.print("[yellow]无数据[/yellow]")
        return

    # defaultdict(float)：访问不存在的键时自动用 float() 即 0.0 作为默认值，不用先判断 key 是否存在
    from collections import defaultdict
    by_category = defaultdict(float)
    for e in expenses:
        by_category[e.category] += e.amount

    table = Table(title="分类汇总")
    table.add_column("分类", style="green")
    table.add_column("金额", style="red", justify="right")

    # sorted(..., key=lambda x: x[1], reverse=True)：按金额（元组第二项）从大到小排序
    # .items() 返回 (键, 值) 的序列，cat 是分类名，amt 是金额
    for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        table.add_row(cat, f"{amt:.2f}")

    console.print(table)
    # sum(可迭代对象) 求和；.values() 是所有金额
    console.print(f"总计: [bold red]{sum(by_category.values()):.2f}[/bold red] 元")


# ---------- 程序入口 ----------
# 只有“直接运行这个文件”时（python main.py）才为 True；被 import 时为 False
# 类似 C++/Java 的 int main() / public static void main(String[] args)
if __name__ == "__main__":
    app()  # 交给 Typer 解析命令行（如 add/list/summary）并调用对应函数
