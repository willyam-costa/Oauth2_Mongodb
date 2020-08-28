import motor.motor_asyncio
from fastapi import FastAPI, Request
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2


DATABASE_URL = "mongodb://localhost:27017"
SECRET = "SECRET"
google_oauth_client = GoogleOAuth2("CLIENT_ID", "CLIENT_SECRET")#GOOGLE
facebook_oauth_client = FacebookOAuth2("CLIENT_ID", "CLIENT_SECRET")#FACEBOOK


class User(models.BaseUser, models.BaseOAuthAccountMixin):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass



client= motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["database_name"]
collection = db["users"]
user_db = MongoDBUserDatabase(UserDB, collection)

def on_after_register(user: UserDB, request: Request):
    print(f"Usuário {user.id} se registrou")


def on_after_forgot_password(user: UserDB, token: str ,request: Request):
    print(f"O usuário {user.id} esqueceu sua senha. token {token} resetado.")

jwt_authentication = JWTAuthentication( #Roteador de autenticação
    secret=SECRET, lifetime_seconds=3600, tokenUrl="/auth/jwt/login"
)
# FastAPI são ultilitários fornecidos para facilitar a integração do processo OAuth2 # https://fastapi.tiangolo.com/
app = FastAPI()
fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app.include_route(
    fastapi_users.get_oauth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_route(# Depois de registrar que chama a função on_after_register
    fastapi_users.get_register_router(on_after_register),
    prefix="/auth",
    tags=["auth"]
)

app.include_route(
    fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password()
    ),
    prefix="/auth",
    tags=["auth"]
)

app.include_route(fastapi_users.get_users_router(), prefix="/users", tags=["auth"])

google_oauth_router = fastapi_users.get_auth_router(
    google_oauth_client, SECRET, after_register=on_after_register
)

app.include_route(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

facebook_oauth_routher = fastapi_users.get_auth_router(
    facebook_oauth_client, SECRET,  after_register=on_after_register
)

app.include_route(google_oauth_router, prefix="/auth/google", tags=["auth"])
app.include_route(facebook_oauth_routher, prefix="/auth/facebook", tags=["auth"])