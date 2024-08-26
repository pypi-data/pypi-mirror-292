import ast
def sparta_7a58bfa7a9(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_5027f6fc43(script_text):return sparta_7a58bfa7a9(script_text)