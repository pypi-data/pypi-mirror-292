import ast
def sparta_1d2c154ed4(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_4c42f4500c(script_text):return sparta_1d2c154ed4(script_text)