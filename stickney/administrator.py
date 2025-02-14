from fastapi import FastAPI, HTTPException, Depends, Request
import authentication as auth
from fastapi.middleware.cors import CORSMiddleware
import logging
from configuration import get_settings, Settings
from contextlib import asynccontextmanager
from schemas import ReloadQuery, ResponseUpdate, ConfigResponse
from  xmlrpc.client import ServerProxy
# Load uvicorn logger
logger = logging.getLogger('uvicorn.error')

# ======================================================================
# Supervisor connection
# ======================================================================
SUPERVISOR_RPC_URL = "http://localhost:9001/RPC2"


def restart_vllm_server():
    """
    Función importante para reiniciar el servidor que se encarga de la
    conversión.
    """
    
    try:
        server = ServerProxy(SUPERVISOR_RPC_URL)
        server.supervisor.stopProcess('vllm-server')
        server.supervisor.startProcess('vllm-server')
        logger.info("VLLM-server restarted successfully.")
    except Exception as e:
        logger.info(f"Error restarting VLLM-server: {e}")

# ======================================================================
# LifeSpan for configs
# ======================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Comenzamos con el objeto cargando los settings
    settings = get_settings()

    logger.info(f'REST-API startup with given config: {settings.model_dump()}')
    app.state.settings = settings
    yield
    
    # Delete global objects
    del app.state.settings
    logger.info("Configuration deleted.")

# Set up the FastAPI app and define the endpoints
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.post("/reload/", summary="Reload Model with a given config", response_model=ResponseUpdate)
def reload(query: ReloadQuery, 
           settings:Settings = Depends(lambda: app.state.settings),
           _ = Depends(auth.get_api_key)):
    """
    Change the model that is being used for inference at runtime.
    Update the configuration and update the config file.
    Send a signal to supervisor to kill vllm and restart with the new model.
    """
    try:
        # Map the ReloadQuery fields to the Settings fields.
        logger.info("New settings received")
        settings.update_config(MODEL_ID=query.model_id)
        logger.info("Configuration updated. Sending signal to supervisor.")
        restart_vllm_server()
        return {
            "message": "Configuration updated successfully. VLLM restarted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@app.get("/config/", summary="Get current configuraion", response_model=ConfigResponse)
def get_config(request:Request,
           _ = Depends(auth.get_api_key)):
    """
    Return current configuration
    """
    try:
        # Acess the current setting
        logger.info("Accessing settings.")
        
        settings = request.app.state.settings
        return {"MODEL_ID":settings.MODEL_ID}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)