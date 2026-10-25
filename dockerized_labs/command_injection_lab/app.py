from flask import Flask, render_template, request
import subprocess
import os
import ast
import operator

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval_expression(expression):
    parsed = ast.parse(expression, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
            left = _eval(node.left)
            right = _eval(node.right)
            return ALLOWED_OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
            operand = _eval(node.operand)
            return ALLOWED_OPERATORS[type(node.op)](operand)
        raise ValueError("Invalid expression")

    return _eval(parsed)


@app.route("/")
def index():
    """Main page with command injection lab description"""
    return render_template("index.html")


@app.route("/lab1", methods=["GET", "POST"])
def lab1():
    """Lab 1: Name Server Lookup with Command Injection"""
    if request.method == "POST":
        domain = request.form.get("domain", "")
        os_type = request.form.get("os", "")

        if os_type == "win":
            command = f"nslookup {domain}"
        else:
            command = f"dig {domain}"

        try:
            # Intentionally vulnerable command execution
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            output = stdout.decode("utf-8") + stderr.decode("utf-8")
        except Exception as e:
            output = str(e)

        return render_template("lab1.html", output=output)

    return render_template("lab1.html")


@app.route("/lab2", methods=["GET", "POST"])
def lab2():
    """Lab 2: Python eval() Code Execution"""
    if request.method == "POST":
        try:
            expression = request.form.get("val", "")
            output = safe_eval_expression(expression)
            return render_template("lab2.html", output=str(output))
        except Exception as e:
            return render_template("lab2.html", output=str(e))
    return render_template("lab2.html")

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=True)
