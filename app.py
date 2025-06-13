"""
APP - Configurazione FastAPI e middleware
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
from utils import contatori

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Crea e configura l'applicazione FastAPI"""
    
    app = FastAPI(
        title="HTTP Explorer - Laboratorio Didattico",
        description="""
        ## Server educativo per esplorare il protocollo HTTP
        
        Questo server fornisce endpoint per testare:
        - **Tutti i metodi HTTP** (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
        - **Status codes** diversi (200, 201, 400, 404, 500, etc.)
        - **Headers personalizzati** e gestione CORS
        - **Query parameters** e **path parameters**
        - **Request/Response body** in vari formati
        - **Autenticazione** simulata
        - **Caching** e **conditional requests**
        
        Perfetto per imparare HTTP attraverso esempi pratici!
        """,
        version="1.0.0",
        contact={
            "name": "HTTP Explorer",
            "email": "info@httpexplorer.com"
        }
    )

    # Configurazione CORS per permettere richieste da qualsiasi origine
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware per logging dettagliato
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Middleware che logga tutte le richieste HTTP per scopi didattici"""
        start_time = time.time()
        
        # Log della richiesta in arrivo
        logger.info(f"RICHIESTA: {request.method} {request.url}")
        logger.info(f"   Headers: {dict(request.headers)}")
        
        if request.method in contatori["richieste_per_metodo"]:
            contatori["richieste_per_metodo"][request.method] += 1
        contatori["visite_totali"] += 1
        
        # Processa la richiesta
        response = await call_next(request)
        
        # Log della risposta
        process_time = time.time() - start_time
        logger.info(f"RISPOSTA: {response.status_code} - Tempo: {process_time:.3f}s")
        
        # Aggiungi header personalizzato con tempo di processamento
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Served-By"] = "HTTP-Explorer-Server"
        
        return response

    # Registra gli endpoint
    from endpoints import register_routes
    register_routes(app)
    
    return app