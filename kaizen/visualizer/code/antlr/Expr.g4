grammar Expr;
expr : term (PLUS term | MINUS term)*;
term : factor (MULT factor | DIV factor)*;
factor : INT | '(' expr ')';