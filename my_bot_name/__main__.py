import uvicorn

from my_bot_name.app import app
from my_bot_name.configurations import API_CONFIG

if __name__ == "__main__":
    uvicorn.run(app=app, port=API_CONFIG.port, host=API_CONFIG.host)
