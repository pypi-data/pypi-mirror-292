import ast
def sparta_f10e592743(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_f17681ea03(script_text):return sparta_f10e592743(script_text)