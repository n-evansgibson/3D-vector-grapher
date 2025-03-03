import string
import copy
from builtins import eval # I know, I know. I'm sorry. This was a temporary fix to my lack of a calculator. 

# 3x + 2
# solves for the value of an expression with x, y, and/or z (simple expressions only)
# output: float
def evalExpression(exp, x, y, z):
    # if there is any multiplication, do that first
    if hasMult(exp):
        multExpression, multStart, multEnd = findMult(exp, x, y, z)
        newTerm = str(doMultiplication(multExpression, x, y, z))
        # replace the old term with the new term
        newExp = replaceTerm(exp, multStart, multEnd, newTerm)
        evalExpression(newExp, x, y, z)
    elif '+' in exp or '-' in exp:
        pass
        # addExpression, addStart, addEnd = findAddition(exp, x, y, z)

def evalExpression(exp, x, y, z):
    expr = copy.copy(exp)
    print('before mods', expr)
    expr = giveVarsMultipliers(expr)
    print('multipliers:', expr)
    expr = replaceVarsWithNums(expr, x, y, z)
    print('after mods:', expr)
    return eval(expr)

def replaceVarsWithNums(exp, x, y, z):
    vars = {'x': x, 'y': y, 'z': z}
    for var, value in vars.items():
        exp = exp.replace(var, f"({value})")  # Replace variable with its value
    return exp

# adds * before variables so eval operates properly
def giveVarsMultipliers(exp):
    vars = ['x', 'y', 'z']
    i = 0
    while i < len(exp):
        c = exp[i]
        if c in vars and (exp[i-1] in string.digits or exp[i-1] in vars) and i != 0:
            exp = exp[:i] + '*' + exp[i:]
            i += 1
        i += 1
    return exp
            

def replaceTerm(exp, oldStart, oldEnd, newTerm):
    # get everything before and after the old term
    beforeExp = exp[:oldStart]
    afterExp = exp[oldEnd + 1:]
    # add in the new expression
    return beforeExp + newTerm + afterExp

# determines if an expression has multiplication or not
def hasMult(exp):
    if '*' in exp: return True
    vars = ['x', 'y', 'z']
    for i in range(len(exp) - 1):
        c1 = exp[i]
        c2 = exp[i+1]
        # If either both strings are variables or only one is, return True
        if (c2 in vars and c1 not in vars) or (c1 in vars and c2 not in vars) or (c1 in vars and c2 in vars):
            return True
    return False

# finds the first multiplicative term in an expression (given that there is mult)
# also returns start and end indices of term
def findMult(exp, x, y, z):
    vars = ['x', 'y', 'z']
    allowedChars = list(string.digits) + ['.']
    # if there is an asterik *, find each number
    if '*' in exp:
        multIndex = exp.find('*')
        termStart = termEnd = multIndex
        # finds the term before the asterik * 
        for i in range(multIndex - 1, -1, -1):
            c = exp[i]
            if c in allowedChars: 
                termStart -=1 
            else: break
        # finds the term after the asterik * 
        for i in range(multIndex + 1, len(exp)):
            c = exp[i]
            if c in allowedChars:
                termEnd += 1
            else: break
        return exp[termStart:termEnd+1], termStart, termEnd
    # if there is a variable or more
    for i in range(len(exp) - 1):
        c1 = exp[i]
        c2 = exp[i + 1]
        # if there is a number before a variable
        if (c2 in vars and c1 not in vars):
            termEnd = i + 1
            termStart = termEnd
            for i in range(termEnd - 1, -1, -1):
                c = exp[i]
                if c in allowedChars:
                    termStart -= 1
                else: break
            return exp[termStart:termEnd + 1], termStart, termEnd
        # if there is a number after a variable
        elif (c1 in vars and c2 not in vars):
            termStart = i 
            termEnd = termStart
            for i in range(termStart + 1, len(exp)):
                c = exp[i]
                if c in allowedChars:
                    termStart += 1
                else: break
            return exp[termStart:termEnd + 1], termStart, termEnd
        # if there are two variables
        elif (c1 in vars and c2 in vars):
            termStart = i
            termEnd = i + 1
            return exp[termStart:termEnd + 1], termStart, termEnd

        
# adds two numbers togethers, or variable x, y, or z 
def doAddition(exp, x, y, z, sign):
    addIndex = exp.find('+') if sign == 1 else exp.find('-')
    num1 = exp[:addIndex].strip()
    num2 = exp[addIndex+1:].strip()
    if num1 == 'x':
        num1 = x
    elif num1 == 'y':
        num1 = y
    elif num1 == 'z':
        num1 = z
    else:
        num1 = float(num1)
    if num2 == 'x':
        num2 = x
    elif num2 == 'y':
        num2 = y
    elif num2 == 'z':
        num2 = z
    else:
        num2 = float(num2)
    if sign == 1:
        return num1 + num2
    else: 
        return num1 - num2

#multiplies two numbers together, or variable x, y, or z
def doMultiplication(exp, x, y, z): 
    # if one of the terms is a variable, take the numbers directly
    for var in ['x', 'y', 'z']:
        if  exp[0] == var:
            num1 = strToFloat(var, x, y, z)
            num2 = float(exp[1:])
            break
        elif exp[-1] == str(var):
            num1 = float(exp[:-1])
            num2 = strToFloat(var, x, y, z)
            break
    multIndex = exp.find('*')
    if multIndex != -1:
        num1 = float(exp[:multIndex])
        num2 = float(exp[multIndex+1:])
    return num1*num2
    
# converts variable string into its actual value
def strToFloat(str, x, y, z):
    if str == 'x':
        return x
    elif str == 'y':
        return y
    elif str == 'z':
        return z

def main():
    print(giveVarsMultipliers('2x'))
    print(evalExpression('2x', 2, 1, 3))
main()
