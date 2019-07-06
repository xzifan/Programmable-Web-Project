import json
import collections
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class StorageItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    location = db.Column(db.String(64), nullable=False)
	
    product = db.relationship("Product", back_populates="in_storage")
	
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(64), unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
	
    in_storage = db.relationship("StorageItem", back_populates="product")

                
@app.route("/products/add/", methods=["POST"])
def add_product():
    if request.method == "POST":
        if request.headers["Content-Type"] == "application/json":
            try:
                handle = request.json["handle"]
                weight = request.json["weight"]
                price = request.json["price"]

                count = Product.query.count()
                handleList = [Product.query.get(i).handle for i in range(1, count + 1)]

                if handle not in handleList:
                    if isinstance(weight, float) and isinstance(price, float):
                        product = Product(
                            handle=handle,
                            weight=weight,
                            price=price)
                        db.session.add(product)
                        db.session.commit()
                        return "", 201
                    return "Weight and price must be numbers", 400
                return "Handle already exists", 409
            except KeyError:
                return "Incomplete request - missing fields", 400
            except TypeError:
                return "Request content type must be JSON", 415
    return "POST method required", 405


@app.route("/storage/<product>/add/", methods=["POST"])
def add_to_storage(product):
    try:
        if request.method == "POST":
            count = Product.query.count()
            handleList = [Product.query.get(i).handle for i in range(1, count+1)]
            if product in handleList:
                product = Product.query.filter_by(handle=product).first()
                if product:
                    qty = request.json["qty"]
                    location = request.json["location"]
                    if isinstance(qty, int):
                        item = StorageItem(
                            product=product,
                            qty=qty,
                            location=location)
                        db.session.add(item)
                        db.session.commit()
                        return "", 201
                    return "Qty must be an integer", 400
            return "Product not found", 404
        return "POST method required", 405
    except KeyError:
        return "Incomplete request - missing fields", 400

@app.route("/storage/", methods=["GET"])
def get_inventory():
    content = collections.OrderedDict()
    j_data = []
    listofInventory = []
    listOfStorage = []
    Pro_data = Product.query.all()
	
    for pro in Pro_data:
        content["handle"] = pro.handle
        content["weight"] = pro.weight
        content["price"] = pro.price
		
        in_stor = StorageItem.query.filter_by(product=pro).all()
        if in_stor:
            for stor in in_stor:
                listofInventory.append(stor.location)
                listofInventory.append(stor.qty)
                listOfStorage.append(listofInventory)
                listofInventory = []
            
        content["inventory"] = listOfStorage
        listOfStorage = []
        json.dumps(content)
        j_data.append(content)
        content = {}

    return jsonify(j_data)
			
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
