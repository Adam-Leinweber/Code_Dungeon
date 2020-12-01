from sly import Lexer
from sly import Parser

class BasicLexer(Lexer): 
    tokens = { ID, NUMBER, STRING, #ITERABLE,
               IF, ELSE, WHILE, SAY,
               PLUS, MINUS, TIMES, DIVIDE, ASSIGN,
               EQ, LT, LEQ, GT, GEQ, NEQ } 
    ignore = '\t '
    literals = {'(', ')', '[', ']', '{', '}', ',', ';'} 
    
    # Regular expression rules for tokens
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    EQ      = r'=='
    ASSIGN  = r'='
    LEQ     = r'<='
    LT      = r'<'
    GEQ     = r'>='
    GT      = r'>'
    NEQ     = r'!='

    # Base ID rule
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'
    # ITERABLE = r'\[(\d,?)+\]'
    # Special cases
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE
    ID['say'] = SAY
    
    # Number token 
    @_(r'\d+') 
    def NUMBER(self, t): 
        # convert it into a python integer 
        t.value = int(t.value)  
        return t 
  
    # Comment token 
    @_(r'#.*') 
    def COMMENT(self, t): 
        pass
  
    # Newline token(used only for showing 
    # errors in new line) 
    @_(r'\n+') 
    def newline(self, t): 
        self.lineno = t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
        
class BasicParser(Parser): 
    #tokens are passed from lexer to parser 
    tokens = BasicLexer.tokens 
  
    precedence = (
        ('left', PLUS, MINUS), 
        ('left', TIMES, DIVIDE), 
        ('right', 'UMINUS'),
    )
    def __init__(self): 
        self.env = { } 
  
    @_('') 
    def statement(self, p): 
        pass
  
    @_('var_assign') 
    def statement(self, p): 
        return p.var_assign 
  
    @_('ID ASSIGN expr') 
    def var_assign(self, p): 
        return ('var_assign', p.ID, p.expr) 
  
    @_('ID ASSIGN STRING') 
    def var_assign(self, p): 
        return ('var_assign', p.ID, p.STRING) 

    # @_('ID ASSIGN ITERABLE') 
    # def var_assign(self, p): 
    #     return ('var_assign', p.ID, p.ITERABLE) 

    # @_('index')
    # def expr(self, p):
    #     return p.index
    
    # @_('ITERABLE "[" NUMBER "]"')
    # def index(self, p):
    #     return ('index', p.ITERABLE, p.NUMBER)
    
    @_('expr') 
    def statement(self, p): 
        return p.expr

    @_('term')
    def expr(self, p):
        return p.term

    @_('factor')
    def term(self, p):
        return p.factor
    
    @_('expr PLUS expr') 
    def expr(self, p): 
        return ('add', p.expr0, p.expr1) 
  
    @_('expr MINUS expr') 
    def expr(self, p): 
        return ('sub', p.expr0, p.expr1) 
  
    @_('expr TIMES expr') 
    def expr(self, p): 
        return ('mul', p.expr0, p.expr1) 
  
    @_('expr DIVIDE expr') 
    def expr(self, p): 
        return ('div', p.expr0, p.expr1) 

    @_('expr LT expr') 
    def expr(self, p): 
        return ('lt', p.expr0, p.expr1)   

    @_('expr LEQ expr') 
    def expr(self, p): 
        return ('leq', p.expr0, p.expr1)   

    @_('expr GT expr') 
    def expr(self, p): 
        return ('gt', p.expr0, p.expr1)   

    @_('expr GEQ expr') 
    def expr(self, p): 
        return ('geq', p.expr0, p.expr1)   

    @_('expr EQ expr') 
    def expr(self, p): 
        return ('eq', p.expr0, p.expr1)   

    @_('expr NEQ expr') 
    def expr(self, p): 
        return ('neq', p.expr0, p.expr1)   

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr
    
    @_('"-" expr %prec UMINUS') 
    def expr(self, p): 
        return p.expr 
  
    @_('ID') 
    def expr(self, p): 
        return ('var', p.ID) 
  
    @_('NUMBER') 
    def expr(self, p): 
        return ('num', p.NUMBER)

    @_('STRING') 
    def expr(self, p): 
        return ('str', p.STRING)

    @_('SAY expr')
    def expr(self, p):
        return('say', p.expr)
            
class BasicExecute:
    return_value = bool
    def __init__(self, tree, env): 
        self.env = env 
        result = self.walkTree(tree) 

        self.return_value = result
        print(self.return_value)
        # if result is not None and isinstance(result, int): 
        #     print(result)
        # if isinstance(result, str) and result[0] == '"': 
        #     print(result)

        
    def walkTree(self, node): 
  
        if isinstance(node, int): 
            return node 
        if isinstance(node, str): 
            return node 
  
        if node is None: 
            return None
  
        if node[0] == 'program': 
            if node[1] == None: 
                self.walkTree(node[2]) 
            else: 
                self.walkTree(node[1]) 
                self.walkTree(node[2]) 
  
        if node[0] == 'num': 
            return node[1] 
  
        if node[0] == 'str': 
            return node[1]

        if node[0] == 'say':
            # if self.walkTree(node[1]) != None:
            #     print(self.walkTree(node[1]))
            return node[1]

        if node[0] == 'index':
            return node[1][node[2]]
        
        if node[0] == 'add':
            try:
                if type(self.walkTree(node[1])) == str and type(self.walkTree(node[2])) == str:
                    return self.walkTree(node[1])[:-1] + self.walkTree(node[2])[1:]
                return self.walkTree(node[1]) + self.walkTree(node[2])
            except:
                print('You can\'t add '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'sub':
            try:
                return self.walkTree(node[1]) - self.walkTree(node[2]) 
            except:
                print('You can\'t subtract '+str(self.walkTree(node[1]))+' from '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'mul':
            try:
                return self.walkTree(node[1]) * self.walkTree(node[2]) 
            except:
                print('You can\'t multiply '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'div':
            try:
                return int(self.walkTree(node[1]) / self.walkTree(node[2]))
            except:
                print('You can\'t divide '+str(self.walkTree(node[1]))+' by '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'lt':
            try:
                return self.walkTree(node[1]) < self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'leq': 
            try:
                return self.walkTree(node[1]) <= self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'gt': 
            try:
                return self.walkTree(node[1]) > self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'geq': 
            try:
                return self.walkTree(node[1]) >= self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'eq': 
            try:
                return self.walkTree(node[1]) == self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
        elif node[0] == 'neq': 
            try:
                return self.walkTree(node[1]) != self.walkTree(node[2]) 
            except:
                print('You can\'t compare '+str(self.walkTree(node[1]))+' and '+str(self.walkTree(node[2]))+'!')
  
        if node[0] == 'var_assign': 
            self.env[node[1]] = self.walkTree(node[2]) 
            return node[1] 
  
        if node[0] == 'var': 
            try: 
                return self.env[node[1]] 
            except LookupError: 
                print("'"+node[1]+"' is undefined!") 
                return 0

if __name__ == '__main__': 
    lexer = BasicLexer() 
    parser = BasicParser() 
    env = {} 

    # reading = True
    # while reading:
    f = open('test_code.cd', 'r')
    lineno = 0
    for line in f:
        lineno += 1
        text = line

        if line.replace(' ','')[0:2] == "if": # if we see an if statement 
            text = line.replace('if', '')
            tree = parser.parse(lexer.tokenize(text))
            if (BasicExecute(tree, env).return_value):
                # go until we see end if                
                print("YES")
        
        elif text:
            tree = parser.parse(lexer.tokenize(text)) 
            BasicExecute(tree, env)
