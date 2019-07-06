import math
from flask import Flask, request

app = Flask("helloFlask")
@app.route("/")
def index():
    return "I'm using flask!"
	
@app.route("/add/<float:number_1>/<float:number_2>")
def plus(number_1, number_2):
    return "{}".format(number_1 + number_2)

@app.route("/sub/<float:number_1>/<float:number_2>")
def minus(number_1, number_2):
    return "{}".format(number_1 - number_2)
	
@app.route("/mul/<float:number_1>/<float:number_2>")
def mult(number_1, number_2):
    return "{}".format(number_1 * number_2)
	
@app.route("/div/<float:number_1>/<float:number_2>")
def div(number_1, number_2):
    if number_2 == 0.0:
        return "NaN"
    return "{}".format(number_1 / number_2)
		

@app.route("/trig/<func>")
def trig(func):
    try:
        angle = request.args["angle"]
    except KeyError:
        return "Missing query parameter: angle", 500
    try:
        unit = request.args["unit"]
    except KeyError:
        unit = "radian"
        
    if unit != "radian" and unit != "degree":
        return "Invalid query parameter value(s)", 500
    for c in angle:
        if ord(c) > 58 or ord(c) < 45 or ord(c) == 47:
            return "Invalid query parameter value(s)", 500
        
    if unit == "degree":
        angle = float(angle)*math.pi/180
        
    if func == "cos":
        return "{}".format(round(math.cos(float(angle)), 3)), 200
    if func == "sin":
        return "{}".format(round(math.sin(float(angle)), 3)), 200
    return "Operation not found", 404
