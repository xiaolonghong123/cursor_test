# models.py - 数据模型（类似 Java 的 POJO 单独放一个文件）

from dataclasses import dataclass, field
from datetime import datetime


# ---------- 数据类：一条消费记录 ----------
# @dataclass 是装饰器：让下面的 class 变成“数据类”，自动生成 __init__、__repr__ 等
# 类似 C++ 的 struct 或 Java 的只存数据的 class
@dataclass
class Expense:
    """一条消费记录（类的文档字符串，用 help(Expense) 能看到）"""
    # 下面都是“类型注解”：变量名: 类型 = 默认值
    id: int
    amount: float
    category: str
    description: str = ""   # 默认空字符串，相当于 Java 的 description = ""
    # default_factory：默认值由“函数”生成，每次创建实例时调用一次（避免所有实例共享同一对象）
    # lambda: ... 是匿名函数，无参数，返回 datetime.now().strftime("%Y-%m-%d") 即 "2026-03-14"
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # 构造完成后自动调用的方法，用来做校验（类似在构造函数末尾写校验逻辑）
    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("金额必须大于0！")
