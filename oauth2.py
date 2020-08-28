import token as token
from httpx_oauth.oauth2 import OAuth2

client = OAuth2(
    "CLIENT_ID",
    "CLIENTE_SECRET",
    "AUTHORIZE_ENDPOINT",
    "ACCESS_TOKEN_ENDPOINT",
    refresh_token_endpoint="REFRESH_TOKEN_ENDPOINT",
    revoke_token_endpoint="REVOKE_TOKEN_ENDPOINT"
)

authorization_url = await client.get_authorization_url(
    "https://www.tintagel.bt/oauth-callback", scope=["SCOPE1", "SCOPE2", "SCOPE3"],
)

access_token = await client.get_access_token("CODE", "https://www.tintagel.bt/oauth-callback")

access_token = await client.refresh_token("REFRESH_TOKEN")

await client.revoke_token("TOKEN")

user_id, user_email =  await client.get_id_email("TOKEN")


if token.is_expired():
    token = await client.refresh_token(token["refresh_token"])
    # Save token to DB

access_token = token["access_token"]
# Do something useful with this access token