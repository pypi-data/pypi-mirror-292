from pythonds.basic.stack import Stack
from typing import TypeVar,overload

__all__ = ['Expression','Suffix_expression','Se','E']

AnyStr = TypeVar('AnyStr',str,bytes)

from suffix_expression import Expression


class ExpressionError(Exception):
    def __init__(self,m:str|None=''):
        self.m = m
    def __str__(self):
        return self.m
class Expression(object):
    def __init__(self,expression):
        """
        :param expression: expression
        """
        self.expression = str(expression)
        self.index = 0
    def __str__(self):
        """
        :return: str(self)
        """
        return self.expression
    def __len__(self):
        """
        :return: len(self)
        """
        return len(self.expression)
    def __iter__(self):
        """

        :return: self
        """
        return self
    def __next__(self):
        """

        :return: next(self)
        """
        if self.index >= len(self):
            self.index = 0
            raise StopIteration
        value = self.expression[self.index]
        self.index += 1
        return value
    @overload
    def __getitem__(self, item:slice):
        """

        :param item: index
        :return: self[item]
        """
        return self.expression[item.start:item.stop:item.step]
    @overload
    def __getitem__(self, item:int):
        if len(self) -1 >= item:return self.expression[item]
        else:raise IndexError('Expression index out of range')
    def __getitem__(self, item:type):
        return item
    @overload
    def __add__(self, other:Expression):
        return self.expression+other.expression
    @overload
    def __add__(self, other:str):
        return self.expression+other
    def __add__(self, other:bytes):
        return self.expression+other.decode()
    def __mul__(self, other):
        """

        :param other: same to __add__
        :return: self * other
        """
        return E(self.expression*other)
    def __bool__(self):
        """

        :return: bool(self)
        """
        return len(self) > 0
    def __repr__(self):
        """

        :return: repr(self)
        """
        return 'e'+'\''+self.expression+'\''
    def __int__(self):
        """

        :return: int(self)
        """
        if not self.expression.isnumeric():
            raise ValueError('invaild literal for int() with base 10:',self.expression)
        return int(self.expression)
class Suffix_expression(object):


    @staticmethod
    def count(expression):
        """
        计算后缀表达式
        :param expression:后缀表达式
        :return:
        """
        stack = Stack()  # 创建一个新的栈用于保存未被输出的运算符
        for i in expression:
            if str(i) in '1234567890':stack.push(i)
            elif i == '+':stack.push(int(stack.pop())+int(stack.pop()))
            elif i == '-':a = int(stack.pop());b = int(stack.pop());stack.push(b-a)
            elif i == '*':stack.push(int(stack.pop())*int(stack.pop()))
            elif i == '/':a = int(stack.pop());b = int(stack.pop());stack.push(b / a)
            else:raise ExpressionError('Operators and numbers must in "+","-","*","/","1","2","3","4","5","6","7","8","9" or "0".')
        return stack.pop()



    @staticmethod
    def generating(expression):
        """
        把中缀表达式转换成后缀表达式
        :param expression: 中缀表达式
        :return: 后缀表达式
        """
        result = []  # 结果列表
        stack = []  # 栈
        for item in expression:
            if item.isnumeric():  # 如果当前字符为数字那么直接放入结果列表
                result.append(item)
            else:  # 如果当前字符为一切其他操作符
                if len(stack) == 0:  # 如果栈空，直接入栈
                    stack.append(item)
                elif item in '*/(':  # 如果当前字符为*/（，直接入栈
                    stack.append(item)
                elif item == ')':  # 如果右括号则全部弹出（碰到左括号停止）
                    t = stack.pop()
                    while t != '(':
                        result.append(t)
                        t = stack.pop()
                # 如果当前字符为加减且栈顶为乘除，则开始弹出
                elif item in '+-' and stack[len(stack) - 1] in '*/':
                    if stack.count('(') == 0:  # 如果有左括号，弹到左括号为止
                        while stack:
                            result.append(stack.pop())
                    else:  # 如果没有左括号，弹出所有
                        t = stack.pop()
                        while t != '(':
                            result.append(t)
                            t = stack.pop()
                        stack.append('(')
                    stack.append(item)  # 弹出操作完成后将‘+-’入栈
                else:
                    stack.append(item)  # 其余情况直接入栈（如当前字符为+，栈顶为+-）

        # 表达式遍历完了，但是栈中还有操作符不满足弹出条件，把栈中的东西全部弹出
        while stack:
            result.append(stack.pop())
        # 返回字符串
        return Expression("".join(result))



Se = Suffix_expression
E = Expression
