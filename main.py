import discord
from discord.ext import commands
import requests
import sys

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="/", intents=intents)

def parse_proxy(proxy: str):
    """
    Parses a proxy in the format host:port:username:password.
    """
    parts = proxy.split(":")
    if len(parts) == 4:
        host, port, username, password = parts
        return {"host": host, "port": port, "username": username, "password": password}
    elif len(parts) == 2:
        host, port = parts
        return {"host": host, "port": port}
    else:
        raise ValueError("Invalid proxy format")

def check_proxy(proxy_dict: dict):
    """
    Checks proxy availability and determines its type.
    """
    protocols = ["http", "https", "socks4", "socks5"]
    for protocol in protocols:
        proxy_url = f"{protocol}://{proxy_dict['host']}:{proxy_dict['port']}"
        proxies = {"http": proxy_url, "https": proxy_url}

        if "username" in proxy_dict and "password" in proxy_dict:
            proxies["http"] = f"{protocol}://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
            proxies["https"] = proxies["http"]

        try:
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
            if response.status_code == 200:
                return protocol
        except requests.exceptions.RequestException:
            continue
    return None

def format_env(proxy_dict: dict, protocol: str):
    """
    Formats proxy for Linux environment variables.
    """
    proxy_auth = f"{proxy_dict['username']}:{proxy_dict['password']}@" if "username" in proxy_dict else ""
    proxy_env = f"{protocol}://{proxy_auth}{proxy_dict['host']}:{proxy_dict['port']}"
    return {
        "http_proxy": proxy_env,
        "https_proxy": proxy_env
    }

def create_response(protocol: str, env_vars: dict):
    """
    Helper function to format the response message.
    """
    return (
        f"Proxy is working. Type: {protocol}\n"
        f"`http_proxy={env_vars['http_proxy']}`\n"
        f"`https_proxy={env_vars['https_proxy']}`"
    )

@bot.command(name="format_proxy")
async def format_proxy(ctx, *, proxy: str):
    """
    Command /format_proxy
    """
    try:
        proxy_dict = parse_proxy(proxy)
        protocol = check_proxy(proxy_dict)

        if protocol:
            env_vars = format_env(proxy_dict, protocol)
            response = create_response(protocol, env_vars)
        else:
            response = "Proxy is not working or the type could not be determined."
    except ValueError as e:
        response = f"Error: {e}"

    await ctx.send(response)

# Run the bot
if len(sys.argv) > 1:
    bot.run(sys.argv[1])
else:
    print("Error: Token is missing!")
