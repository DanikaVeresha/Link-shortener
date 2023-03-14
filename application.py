import base64
import os
import random
import string
from aiohttp import web
import motor.motor_asyncio
from cryptography import fernet
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb://root:example@{os.environ.get("DB_HOST","localhost")}:27017')
db = client['redirecter']
collection = db['redirects']


def html_response(document):
    file = open(document, "r")
    return web.Response(text=file.read(), content_type='text/html')


async def index_page(request):
    session = await get_session(request)
    username_in_session = None
    if 'user' in session:
        username_in_session = session['user']
    return html_response('redirecter.html')


async def login_page(request):
    return html_response('login.html')


async def register_page(request):
    return html_response('register.html')


async def recieve_url(request):
    data = await request.post()
    long_url = data['lond_url']
    generate_resourse_id = ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(6))
    document = await collection.insert_one(
        {'long_url': long_url,
         'resourse_id': generate_resourse_id})
    return web.Response(text=generate_resourse_id,
                        content_type='text/plain')


async def login_user(request):
    data = await request.post()
    username = data['username']
    password = data['password']
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://root:example@{os.environ.get("DB_HOST", "localhost")}:27017')
    db = client['redirecter']
    collection = db['users']
    user_info = await collection.find_one({'username': username, 'password': password})
    if user_info:
        session = await get_session(request)
        session['user'] = username
        return web.Response(text="""<html>You have been logged in/<html>""")
    return web.Response(text="""<html>Invalid username or password/<html>""")


async def register_user(request):
    data = await request.post()
    username = data['username']
    password = data['password']
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f'mongodb://root:example@{os.environ.get("DB_HOST", "localhost")}:27017')
    db = client['redirecter']
    collection = db['users']
    await collection.insert_one({'username': username, 'password': password})
    return web.Response(text="""<html>You have been registered/<html>""")


async def redirecter(request):
    resourse_id = request.match_info['resourse_id']
    document = await collection.find_one({'resourse_id': resourse_id})
    if document is None:
        return web.Response(text="Not found", status=404)
    long_url = document['long_url']
    return web.HTTPFound(long_url)


app = web.Application()
fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(app, EncryptedCookieStorage(secret_key))

app.add_routes([web.get('/', index_page)])
app.add_routes([web.post('/', recieve_url)])
app.add_routes([web.get('/login', login_page)])
app.add_routes([web.post('/login', login_user)])
app.add_routes([web.get('/register', register_page)])
app.add_routes([web.post('/register', register_user)])
app.add_routes([web.get('/{resourse_id}', redirecter)])
web.run_app(app)





