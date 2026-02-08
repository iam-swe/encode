from app.ui import demo 
import os
import opik

opik.configure(
    api_key=os.getenv('OPIK_API_KEY'),
    workspace=os.getenv('OPIK_WORKSPACE') 
)

if __name__ == "__main__":
    demo.launch() 