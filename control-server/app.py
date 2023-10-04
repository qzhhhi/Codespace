import base64
from flask import Flask
from flask import request
from pymongo import MongoClient
from hashlib import sha256
import uuid
import docker as docker_sdk
from time import sleep

docker = docker_sdk.from_env()

mongo = MongoClient(f"mongodb://root:password@127.0.0.1:27017")
whitelist = mongo["user"]["whitelist"]
accounts = mongo["user"]["account"]

app = Flask(__name__)
app.json.ensure_ascii = False

register_keys = set(["id", "name", "tel", "pwd"])
login_keys = set(["id", "pwd"])

active_containers = {}

def hash_password(request_form):
    return sha256(f"{request_form['pwd']}salt{request_form['id']}*".encode('utf-8')).hexdigest()

def generate_subdomain():
    return str(uuid.uuid4())[-12:]

def get_container_name(data):
    return f"alliance-vsc-server-{data['_id']}"

@app.route("/register", methods=['POST'])
def register():
    if set(request.form.keys()) != register_keys:
        return "Bad request", 400
    
    data = whitelist.find_one({"_id": request.form["id"], "name": request.form["name"], "tel": request.form["tel"]})
    if data is None:
        return {"success": False, "msg": "学号不在白名单中，或其他信息不匹配，请检查信息是否有误"}
    if data["enabled"] == False:
        return {"success": False, "msg": "账户存在，但不再有效，请联系管理员"}
    if accounts.find_one(request.form["id"]) is not None:
        return {"success": False, "msg": "账户已存在，请登录"}
    
    for i in range(10):
        subdomain = generate_subdomain()
        if accounts.find_one({"subdomain": subdomain}) is None:
            accounts.insert_one({
                "_id": request.form["id"],
                "pwd": hash_password(request.form),
                "subdomain": generate_subdomain()
            })
            return {"success": True}
    return {"success": False, "msg": "域名冲突，请联系管理员"}
        
    
@app.route("/login", methods=['POST'])
def login():
    if set(request.form.keys()) != login_keys:
        return "Bad request", 400    
    data = accounts.find_one({
        "_id": request.form["id"],
        "pwd": hash_password(request.form)
    })
    if data is None:
        return {"success": False, "msg": "用户名或密码错误"}
    if whitelist.find_one(request.form["id"])["enabled"] == False:
        return {"success": False, "msg": "账户存在，但不再有效，请联系管理员"}
    
    try:
        pass
        container = docker.containers.get(get_container_name(data))
        env = dict((line.split("=", 1) for line in container.attrs["Config"]["Env"]))
        return {"success": True, "active": True, "subdomain": env["WEBSITE_SUBDOMAIN"], "token": env["LOGIN_TOKEN"]}
    except docker_sdk.errors.NotFound: pass

    subdomain = data['subdomain']
    token = uuid.uuid4()
    docker.containers.run(
        "qzhhhi/alliance-vsc-server:0.0.5",
        name=get_container_name(data),
        detach=True, remove=True, hostname="alliance",
        environment=[f"WEBSITE_SUBDOMAIN={subdomain}", f"LOGIN_TOKEN={token}"],        
    )
    return {"success": True, "active": False, "subdomain": subdomain, "token": token}

def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

app.after_request(after_request)