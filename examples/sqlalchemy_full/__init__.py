import os
from pathlib import Path

import uvicorn

from examples.sqlalchemy_full.app import app

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
