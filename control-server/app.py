import asyncio
import logging
import uuid
from hashlib import sha256

from codespace import CodespaceController
from pymongo import MongoClient
from quart import Quart, request

mongo = MongoClient(f"mongodb://root:password@127.0.0.1:27017")
whitelist = mongo["user"]["whitelist"]
accounts = mongo["user"]["account"]

app = Quart(__name__)
app.json.ensure_ascii = False
app.logger.setLevel(logging.INFO)

register_keys = set(["id", "name", "tel", "pwd"])
login_keys = set(["id", "pwd"])


def hash_password(request_form):
    return sha256(
        f"{request_form['pwd']}salt{request_form['id']}*".encode("utf-8")
    ).hexdigest()


def generate_subdomain():
    return str(uuid.uuid4())[-12:]


@app.before_serving
async def startup():
    global codespace
    loop = asyncio.get_event_loop()
    codespace = CodespaceController(loop=loop, logger=app.logger)


@app.post("/register")
async def register():
    request_data = await request.form

    if set(request_data.keys()) != register_keys:
        return "Bad request", 400

    whitelist_data = whitelist.find_one(
        {
            "_id": request_data["id"],
            "name": request_data["name"],
            "tel": request_data["tel"],
        }
    )
    if whitelist_data is None:
        return {"success": False, "msg": "学号不在白名单中，或其他信息不匹配，请检查信息是否有误"}
    if whitelist_data["enabled"] == False:
        return {"success": False, "msg": "账户存在，但不再有效，请联系管理员"}
    if accounts.find_one(request_data["id"]) is not None:
        return {"success": False, "msg": "账户已存在，请登录"}

    for i in range(10):
        subdomain = generate_subdomain()
        if accounts.find_one({"subdomain": subdomain}) is None:
            accounts.insert_one(
                {
                    "_id": request_data["id"],
                    "pwd": hash_password(request_data),
                    "subdomain": generate_subdomain(),
                }
            )
            return {"success": True}
    return {"success": False, "msg": "域名冲突，请联系管理员"}


@app.route("/login", methods=["POST"])
async def login():
    request_form = await request.form

    if set(request_form.keys()) != login_keys:
        return "Bad request", 400
    data = accounts.find_one(
        {"_id": request_form["id"], "pwd": hash_password(request_form)}
    )
    if data is None:
        return {"success": False, "msg": "用户名或密码错误"}
    if whitelist.find_one(request_form["id"])["enabled"] == False:
        return {"success": False, "msg": "账户存在，但不再有效，请联系管理员"}

    response = await codespace.run_or_fetch(data)
    response["success"] = True
    return response


def after_request(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


app.after_request(after_request)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
