import click
import json
from flask import Flask, Blueprint, Response, request
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from jsonschema import validate, ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

MASON = "application/vnd.mason+json"
LINK_RELATIONS_URL = "/sensorhub/link-relations/"
ERROR_PROFILE = "/profiles/error/"
SENSOR_PROFILE = "/profiles/sensor/"

MEASUREMENT_PAGE_SIZE = 50

# ^
# |
# PREPARATIONS
# MODELS
# |
# v

deployments = db.Table("deployments",
    db.Column("deployment_id", db.Integer, db.ForeignKey("deployment.id"), primary_key=True),
    db.Column("sensor_id", db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    description=db.Column(db.String(256), nullable=True)
    
    sensor = db.relationship("Sensor", back_populates="location", uselist=False)

class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    
    sensors = db.relationship("Sensor", secondary=deployments, back_populates="deployments")

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)
    
    location = db.relationship("Location", back_populates="sensor")
    measurements = db.relationship("Measurement", back_populates="sensor")
    deployments = db.relationship("Deployment", secondary=deployments, back_populates="sensors")
    
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "model"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Sensor's unique name",
            "type": "string"
        }
        props["model"] = {
            "description": "Name of the sensor's model",
            "type": "string"
        }
        return schema
    
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
        
    sensor = db.relationship("Sensor", back_populates="measurements")
    
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["value"]
        }
        props = schema["properties"] = {}
        props["value"] = {
            "description": "Measured value.",
            "type": "number"
        }
        props["time"] = {
            "description": "Measurement timestamp",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-9]{2}:[0-5][0-9]:[0-5][0-9]Z$"
        }
        return schema

# ^
# |
# MODELS
# UTILS
# |
# v

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class SensorhubBuilder(MasonBuilder):

    def add_control_delete_sensor(self, sensor):
        self.add_control(
            "senhub:delete",
            api.url_for(SensorItem, sensor=sensor),
            method="DELETE",
            title="Delete this sensor"
        )

    def add_control_add_measurement(self, sensor):
        self.add_control(
            "senhub:add-measurement",
            api.url_for(MeasurementCollection, sensor=sensor),
            method="POST",
            encoding="json",
            title="Add a new measurement for this sensor",
            schema=Measurement.get_schema()
        )

    def add_control_add_sensor(self):
        self.add_control(
            "senhub:add-sensor",
            api.url_for(SensorCollection),
            method="POST",
            encoding="json",
            title="Add a new sensor",
            schema=Sensor.get_schema()
        )

    def add_control_modify_sensor(self, sensor):
        self.add_control(
            "edit",
            api.url_for(SensorItem, sensor=sensor),
            method="PUT",
            encoding="json",
            title="Edit this sensor",
            schema=Sensor.get_schema()
        )

    def add_control_get_measurements(self, sensor):
        base_uri = api.url_for(MeasurementCollection, sensor=sensor)
        uri = base_uri + "?start={index}"
        self.add_control(
            "senhub:measurements",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    @staticmethod
    def _paginator_schema():
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        props = schema["properties"]
        props["index"] = {
            "description": "Starting index for pagination",
            "type": "integer",
            "default": "0"
        }
        return schema

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)

# ^
# |
# UTILS
# RESOURCES
# |
# v

class SensorCollection(Resource):

    def get(self):
        body = SensorhubBuilder()

        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(SensorCollection))
        body.add_control_add_sensor()
        body["items"] = []
        for db_sensor in Sensor.query.all():
            item = SensorhubBuilder(
                name=db_sensor.name,
                model=db_sensor.model,
                location=db_sensor.location and db_sensor.location.name
            )
            item.add_control("self", api.url_for(SensorItem, sensor=db_sensor.name))
            item.add_control("profile", SENSOR_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Sensor.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        sensor = Sensor(
            name=request.json["name"],
            model=request.json["model"],
        )

        try:
            db.session.add(sensor)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", 
                "Sensor with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": api.url_for(SensorItem, sensor=request.json["name"])
        })


class SensorItem(Resource):

    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(404, "Not found", 
                "No sensor was found with the name {}".format(sensor)
            )
        
        body = SensorhubBuilder(
            name=db_sensor.name,
            model=db_sensor.model,
            location=db_sensor.location and db_sensor.location.name
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(SensorItem, sensor=sensor))
        body.add_control("profile", SENSOR_PROFILE)
        body.add_control("collection", api.url_for(SensorCollection))
        body.add_control_delete_sensor(sensor)
        body.add_control_modify_sensor(sensor)
        body.add_control_add_measurement(sensor)
        body.add_control_get_measurements(sensor)
        body.add_control("senhub:measurements-first",
            api.url_for(MeasurementCollection, sensor=sensor)
        )
        if db_sensor.location is not None:
            body.add_control("senhub:location", 
                api.url_for(LocationItem, location=db_sensor.location.sensor)
            )
        
        return Response(json.dumps(body), 200, mimetype=MASON)
    
    def put(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(404, "Not found", 
                "No sensor was found with the name {}".format(sensor)
            )
        
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Sensor.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
    
        db_sensor.name = request.json["name"]
        db_sensor.model = request.json["model"]
        
        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", 
                "Sensor with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=204)

    def delete(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(404, "Not found", 
                "No sensor was found with the name {}".format(sensor)
            )

        db.session.delete(db_sensor)
        db.session.commit()

        return Response(status=204)


class LocationItem(Resource):

    def get(self, location):
        return create_error_response(501, "Unimplemented")


class MeasurementCollection(Resource):

    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(404, "Not found", 
                "No sensor was found with the name {}".format(sensor)
            )

        try:
            start = int(request.args.get("start", 0))
        except ValueError:
            return create_error_response(400, "Invalid query string value")

        remaining = Measurement.query.filter_by(sensor=db_sensor).order_by("time").offset(start)

        body = SensorhubBuilder(
            items=[]
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        base_uri = api.url_for(MeasurementCollection, sensor=sensor)
        body.add_control("up", api.url_for(SensorItem, sensor=sensor))
        if start >= 50:
            body.add_control("self", base_uri + "?start={}".format(start))
            body.add_control("prev", base_uri + "?start={}".format(start - MEASUREMENT_PAGE_SIZE))
        else:
            body.add_control("self", base_uri)
        if remaining.count() > 50:
            body.add_control("next", base_uri + "?start={}".format(start + MEASUREMENT_PAGE_SIZE))

        for meas in remaining.limit(MEASUREMENT_PAGE_SIZE):
            item = SensorhubBuilder(
                value=meas.value,
                time=meas.time.isoformat()
            )
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

# ^
# |
# RESOURCES
# ROUTES & CLI
# |
# v

app.register_blueprint(api_bp)

api.add_resource(SensorCollection, "/sensors/")
api.add_resource(SensorItem, "/sensors/<sensor>/")
api.add_resource(LocationItem, "/locations/<location>/")
api.add_resource(MeasurementCollection, "/sensors/<sensor>/measurements/")

@app.route(LINK_RELATIONS_URL)
def send_link_relations():
    return "link relations"

@app.route("/profiles/<profile>/")
def send_profile(profile):
    return "you requests {} profile".format(profile)

@app.route("/admin/")
def admin_site():
    return app.send_static_file("html/admin.html")

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

@click.command("testgen")
@with_appcontext
def generate_test_data():
    import datetime
    import random
    s = Sensor(
        name="test-sensor-1",
        model="testsensor"
    )
    now = datetime.datetime.now()
    interval = datetime.timedelta(seconds=10)
    for i in range(1000):
        m = Measurement(
            value=round(random.random() * 100, 2),
            time=now
        )
        now += interval
        s.measurements.append(m)
    
    db.session.add(s)
    db.session.commit()

app.cli.add_command(init_db_command)
app.cli.add_command(generate_test_data)
