# main.py
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
from pathlib import Path
from typing import List
import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="建丰的个人消费追踪工具 🚀")
DATA_FILE = Path("expenses.json")

@dataclass
class Expense:
    """一条消费记录"""
    id: int
    amount: float
    category: str
    description: str = ""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("金额必须大于0！")

def load_expenses() -> List[Expense]:
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
            return [Expense(**item) for item in data]
    except Exception as e:
        console.print(f"[red]读取文件出错: {e}[/red]")
        return []

def save_expenses(expenses: List[Expense]):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in expenses], f, ensure_ascii=False, indent=2)

@app.command()
def add(
    amount: float = typer.Argument(..., help="消费金额（例如 28.5）"),
    category: str = typer.Argument(..., help="分类（餐饮/交通/购物 等）"),
    description: str = typer.Option("", "--desc", "-d", help="描述/备注")
):
    """添加一条新消费"""
    expenses = load_expenses()
    new_id = max((e.id for e in expenses), default=0) + 1
    try:
        exp = Expense(id=new_id, amount=amount, category=category, description=description)
        expenses.append(exp)
        save_expenses(expenses)
        console.print(f"[green]添加成功！[/green] ID: {new_id} | {amount:.2f} 元 | {category}")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")

@app.command("list")
def list_expenses():
    """列出所有消费记录"""
    expenses = load_expenses()
    if not expenses:
        console.print("[yellow]还没有任何记录～[/yellow]")
        return

    table = Table(title="消费记录")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("金额", style="magenta")
    table.add_column("分类", style="green")
    table.add_column("描述")
    table.add_column("日期", style="blue")

    total = 0.0
    for e in expenses:
        table.add_row(str(e.id), f"{e.amount:.2f}", e.category, e.description or "-", e.date)
        total += e.amount

    console.print(table)
    console.print(f"\n[bold]总消费：[/bold][red]{total:.2f} 元[/red]")

@app.command()
def summary():
    """按分类统计月度汇总"""
    expenses = load_expenses()
    if not expenses:
        console.print("[yellow]无数据[/yellow]")
        return

    from collections import defaultdict
    by_category = defaultdict(float)
    for e in expenses:
        by_category[e.category] += e.amount

    table = Table(title="分类汇总")
    table.add_column("分类", style="green")
    table.add_column("金额", style="red", justify="right")

    for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        table.add_row(cat, f"{amt:.2f}")

    console.print(table)
    console.print(f"总计: [bold red]{sum(by_category.values()):.2f}[/bold red] 元")

if __name__ == "__main__":
    app()