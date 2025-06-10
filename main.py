"""
SERVER HTTP EXPLORER - Laboratorio Didattico per il Protocollo HTTP
Creato con FastAPI per esplorare tutti gli aspetti del protocollo HTTP

Caratteristiche:
- Tutti i metodi HTTP (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
- Gestione completa di headers, query parameters, path parameters
- Diversi status codes di risposta
- Esempi pratici di API RESTful
- Logging dettagliato delle richieste
- Documentazione automatica con Swagger
"""

from fastapi import FastAPI, HTTPException, Request, Response, Header, Query, Path, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import json
import time
from datetime import datetime
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelli Pydantic per validazione dati
class Prodotto(BaseModel):
    """Modello per rappresentare un prodotto nell'e-commerce"""
    id: Optional[int] = None
    nome: str = Field(..., min_length=1, max_length=100, description="Nome del prodotto")
    descrizione: Optional[str] = Field(None, max_length=500, description="Descrizione dettagliata")
    prezzo: float = Field(..., gt=0, description="Prezzo in euro")
    categoria: str = Field(..., description="Categoria del prodotto")
    disponibile: bool = Field(True, description="Disponibilità del prodotto")
    tags: Optional[List[str]] = Field([], description="Tag per categorizzazione")

class AggiornaProdotto(BaseModel):
    """Modello per aggiornamento parziale del prodotto (PATCH)"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descrizione: Optional[str] = Field(None, max_length=500)
    prezzo: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = None
    disponibile: Optional[bool] = None
    tags: Optional[List[str]] = None

class Utente(BaseModel):
    """Modello per rappresentare un utente"""
    id: Optional[int] = None
    nome: str
    email: str
    eta: Optional[int] = Field(None, ge=0, le=120)

class RispostaHTTP(BaseModel):
    """Modello standard per le risposte dell'API"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str
    endpoint: str

# Inizializzazione FastAPI
app = FastAPI(
    title="🌐 HTTP Explorer - Laboratorio Didattico",
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
    
    Perfetto per imparare HTTP attraverso esempi pratici! 🚀
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

# Database simulato in memoria
prodotti_db: Dict[int, Prodotto] = {
    1: Prodotto(id=1, nome="Smartphone Pro", descrizione="Ultimo modello con 5G", prezzo=899.99, categoria="elettronica", tags=["mobile", "5g"]),
    2: Prodotto(id=2, nome="Laptop Gaming", descrizione="Potente laptop per gaming", prezzo=1299.99, categoria="computer", tags=["gaming", "performance"]),
    3: Prodotto(id=3, nome="Cuffie Wireless", descrizione="Audio di alta qualità", prezzo=199.99, categoria="audio", disponibile=False, tags=["wireless", "audio"])
}

utenti_db: Dict[int, Utente] = {
    1: Utente(id=1, nome="Mario Rossi", email="mario@email.com", eta=30),
    2: Utente(id=2, nome="Giulia Bianchi", email="giulia@email.com", eta=25)
}

# Contatori per statistiche
contatori = {
    "visite_totali": 0,
    "richieste_per_metodo": {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
}

# Middleware per logging dettagliato
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware che logga tutte le richieste HTTP per scopi didattici"""
    start_time = time.time()
    
    # Log della richiesta in arrivo
    logger.info(f"📨 RICHIESTA: {request.method} {request.url}")
    logger.info(f"   Headers: {dict(request.headers)}")
    
    if request.method in contatori["richieste_per_metodo"]:
        contatori["richieste_per_metodo"][request.method] += 1
    contatori["visite_totali"] += 1
    
    # Processa la richiesta
    response = await call_next(request)
    
    # Log della risposta
    process_time = time.time() - start_time
    logger.info(f"📤 RISPOSTA: {response.status_code} - Tempo: {process_time:.3f}s")
    
    # Aggiungi header personalizzato con tempo di processamento
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Served-By"] = "HTTP-Explorer-Server"
    
    return response

def crea_risposta(success: bool, message: str, data: Any = None, endpoint: str = "") -> RispostaHTTP:
    """Utility per creare risposte standardizzate"""
    return RispostaHTTP(
        success=success,
        message=message,
        data=data,
        timestamp=datetime.now().isoformat(),
        endpoint=endpoint
    )

def preferisce_html(accept_header: str = None) -> bool:
    """
    Determina se il client preferisce HTML basandosi sull'header Accept
    Content Negotiation secondo RFC 7231
    """
    if not accept_header:
        return False
    
    accept_lower = accept_header.lower()
    
    # Se richiede esplicitamente HTML
    if 'text/html' in accept_lower:
        # Controlla se HTML ha priorità più alta di JSON
        html_priority = 1.0
        json_priority = 0.0
        
        # Parsing semplificato delle priorità q-values
        if 'text/html' in accept_lower:
            # Estrae q-value per HTML se presente
            html_part = accept_lower.split('text/html')[1].split(',')[0]
            if 'q=' in html_part:
                try:
                    html_priority = float(html_part.split('q=')[1].split(';')[0].split(',')[0])
                except:
                    html_priority = 1.0
        
        if 'application/json' in accept_lower:
            # Estrae q-value per JSON se presente  
            json_part = accept_lower.split('application/json')[1].split(',')[0]
            if 'q=' in json_part:
                try:
                    json_priority = float(json_part.split('q=')[1].split(';')[0].split(',')[0])
                except:
                    json_priority = 1.0
        
        return html_priority >= json_priority
    
    return False

def genera_html_prodotti(prodotti: List[Prodotto], titolo: str = "Lista Prodotti") -> str:
    """Genera HTML per visualizzare lista prodotti"""
    html = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titolo} - HTTP Explorer</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            .product {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; background: #fafafa; }}
            .product h3 {{ color: #007bff; margin-top: 0; }}
            .price {{ font-weight: bold; color: #28a745; font-size: 1.2em; }}
            .category {{ background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em; }}
            .available {{ color: #28a745; }}
            .unavailable {{ color: #dc3545; }}
            .tags {{ margin-top: 10px; }}
            .tag {{ background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }}
            .api-info {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .json-link {{ display: inline-block; margin-top: 10px; padding: 8px 15px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; }}
            .json-link:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 {titolo}</h1>
            
            <div class="api-info">
                <strong>🔄 Content Negotiation Demo</strong><br>
                Questo endpoint restituisce HTML per browser e JSON per API client!<br>
                <a href="/prodotti" class="json-link">📄 Versione JSON</a>
                <span style="margin: 0 10px;">•</span>
                <a href="/docs#/📦%20API%20Prodotti%20(E-commerce%20RESTful)/ottieni_prodotti_prodotti_get" class="json-link">📖 Documentazione API</a>
            </div>
    """
    
    if not prodotti:
        html += "<p>🔍 Nessun prodotto trovato.</p>"
    else:
        for prodotto in prodotti:
            disponibilita = "✅ Disponibile" if prodotto.disponibile else "❌ Non disponibile"
            disponibilita_class = "available" if prodotto.disponibile else "unavailable"
            
            tags_html = ""
            if prodotto.tags:
                tags_html = "<div class='tags'>" + "".join([f"<span class='tag'>{tag}</span>" for tag in prodotto.tags]) + "</div>"
            
            html += f"""
            <div class="product">
                <h3>📦 {prodotto.nome}</h3>
                <p><strong>Descrizione:</strong> {prodotto.descrizione or 'Nessuna descrizione'}</p>
                <p class="price">💰 €{prodotto.prezzo:.2f}</p>
                <p><span class="category">{prodotto.categoria}</span></p>
                <p class="{disponibilita_class}">{disponibilita}</p>
                {tags_html}
                <small style="color: #666;">ID: {prodotto.id}</small>
            </div>
            """
    
    html += """
            <hr style="margin: 30px 0;">
            <div style="text-align: center; color: #666;">
                <p>🚀 <strong>HTTP Explorer</strong> - Server didattico per il protocollo HTTP</p>
                <p><a href="/">🏠 Homepage</a> • <a href="/docs">📖 Documentazione API</a> • <a href="/statistiche">📊 Statistiche</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def genera_html_singolo_prodotto(prodotto: Prodotto) -> str:
    """Genera HTML per singolo prodotto"""
    disponibilita = "✅ Disponibile" if prodotto.disponibile else "❌ Non disponibile"
    disponibilita_class = "available" if prodotto.disponibile else "unavailable"
    
    tags_html = ""
    if prodotto.tags:
        tags_html = "<div class='tags'><strong>🏷️ Tags:</strong> " + "".join([f"<span class='tag'>{tag}</span>" for tag in prodotto.tags]) + "</div>"
    
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{prodotto.nome} - HTTP Explorer</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 600px; }}
            h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            .price {{ font-weight: bold; color: #28a745; font-size: 1.5em; margin: 15px 0; }}
            .category {{ background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; }}
            .available {{ color: #28a745; }}
            .unavailable {{ color: #dc3545; }}
            .info-row {{ margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }}
            .tags {{ margin-top: 15px; }}
            .tag {{ background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.9em; margin-right: 5px; }}
            .actions {{ margin-top: 30px; text-align: center; }}
            .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .btn:hover {{ opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 {prodotto.nome}</h1>
            
            <div class="info-row">
                <strong>📝 Descrizione:</strong><br>
                {prodotto.descrizione or 'Nessuna descrizione disponibile'}
            </div>
            
            <div class="price">💰 €{prodotto.prezzo:.2f}</div>
            
            <div class="info-row">
                <strong>📂 Categoria:</strong> <span class="category">{prodotto.categoria}</span>
            </div>
            
            <div class="info-row">
                <strong>📋 Disponibilità:</strong> <span class="{disponibilita_class}">{disponibilita}</span>
            </div>
            
            {tags_html}
            
            <div class="info-row">
                <strong>🆔 ID Prodotto:</strong> {prodotto.id}
            </div>
            
            <div class="actions">
                <a href="/prodotti" class="btn btn-primary">📋 Tutti i Prodotti</a>
                <a href="/prodotti/{prodotto.id}" class="btn btn-success">📄 Versione JSON</a>
                <a href="/docs" class="btn btn-secondary">📖 API Docs</a>
            </div>
        </div>
    </body>
    </html>
    """

def genera_html_homepage() -> str:
    """Genera HTML per homepage"""
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HTTP Explorer - Laboratorio Didattico</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
            .header { text-align: center; color: white; margin-bottom: 40px; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .card { background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .card h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li { padding: 8px 0; border-bottom: 1px solid #eee; }
            .feature-list li:before { content: "✅ "; color: #28a745; font-weight: bold; }
            .btn { display: inline-block; padding: 12px 25px; margin: 10px 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; transition: background 0.3s; }
            .btn:hover { background: #0056b3; }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #1e7e34; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-warning:hover { background: #e0a800; }
            .endpoint-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px; }
            .endpoint { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
            .endpoint strong { color: #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 HTTP Explorer</h1>
                <p>Laboratorio Didattico per il Protocollo HTTP</p>
            </div>
            
            <div class="card">
                <h2>🎯 Benvenuto nel Laboratorio HTTP!</h2>
                <p>Questo server ti permette di esplorare tutti gli aspetti del protocollo HTTP attraverso esempi pratici e interattivi.</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/docs" class="btn btn-success">📖 Documentazione Interattiva (Swagger)</a>
                    <a href="/prodotti" class="btn">📦 API Prodotti</a>
                    <a href="/download/postman-collection" class="btn btn-warning">📥 Scarica Collezione Postman</a>
                    <a href="/statistiche" class="btn btn-warning">📊 Statistiche Server</a>
                </div>
            </div>
            
            <div class="features">
                <div class="card">
                    <h2>🚀 Funzionalità</h2>
                    <ul class="feature-list">
                        <li>Tutti i metodi HTTP (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)</li>
                        <li>Content Negotiation (HTML + JSON)</li>
                        <li>Testing di Status Codes</li>
                        <li>Gestione Headers personalizzati</li>
                        <li>API RESTful completa</li>
                        <li>Cache e CORS</li>
                        <li>Logging dettagliato</li>
                        <li>Documentazione automatica</li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>📚 Cosa Imparerai</h2>
                    <ul class="feature-list">
                        <li>Come funzionano le richieste HTTP</li>
                        <li>Differenze tra metodi (GET vs POST vs PUT)</li>
                        <li>Status codes e gestione errori</li>
                        <li>Headers e loro utilizzo</li>
                        <li>Content Negotiation</li>
                        <li>API RESTful design</li>
                        <li>Caching e ottimizzazione</li>
                        <li>Sicurezza e CORS</li>
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <h2>🔗 Endpoint Principali</h2>
                <div class="endpoint-grid">
                    <div class="endpoint">
                        <strong>GET /prodotti</strong><br>
                        <small>Lista prodotti con filtri</small>
                    </div>
                    <div class="endpoint">
                        <strong>POST /prodotti</strong><br>
                        <small>Crea nuovo prodotto</small>
                    </div>
                    <div class="endpoint">
                        <strong>GET /test/status/{code}</strong><br>
                        <small>Test status codes</small>
                    </div>
                    <div class="endpoint">
                        <strong>GET /headers</strong><br>
                        <small>Ispeziona headers</small>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🧪 Content Negotiation Demo</h2>
                <p>Questo server dimostra la <strong>Content Negotiation</strong> - la capacità di restituire diversi formati basandosi sull'header <code>Accept</code> della richiesta:</p>
                <ul>
                    <li><strong>Browser</strong> (Accept: text/html) → Riceve pagine HTML</li>
                    <li><strong>API Client</strong> (Accept: application/json) → Riceve dati JSON</li>
                    <li><strong>curl</strong> senza Accept → Riceve JSON (default)</li>
                </ul>
                <p><strong>Prova tu stesso:</strong></p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace;">
                    # Nel browser → HTML<br>
                    <a href="/prodotti" style="color: #007bff;">http://localhost:8000/prodotti</a><br><br>
                    
                    # Con curl → JSON<br>
                    curl http://localhost:8000/prodotti<br><br>
                    
                    # Forza HTML con curl<br>
                    curl -H "Accept: text/html" http://localhost:8000/prodotti
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# ================================
# ENDPOINT INFORMATIVI E DIAGNOSTICI
# ================================

@app.get("/", summary="🏠 Pagina principale")
async def homepage(request: Request, accept: str = Header(None)):
    """
    Endpoint principale con informazioni sul server
    
    Dimostra Content Negotiation:
    - Browser (Accept: text/html) → Riceve HTML
    - API Client (Accept: application/json) → Riceve JSON
    """
    if preferisce_html(accept):
        return HTMLResponse(content=genera_html_homepage())
    
    # Risposta JSON per API client
    return crea_risposta(
        success=True,
        message="Benvenuto nell'HTTP Explorer! Server didattico per esplorare il protocollo HTTP.",
        data={
            "content_negotiation": {
                "descrizione": "Questo endpoint supporta content negotiation",
                "formati_supportati": ["application/json", "text/html"],
                "header_utilizzato": "Accept",
                "esempio_html": "curl -H 'Accept: text/html' http://localhost:8000/",
                "esempio_json": "curl -H 'Accept: application/json' http://localhost:8000/"
            },
            "funzionalita": [
                "Gestione completa di tutti i metodi HTTP",
                "Content Negotiation (HTML + JSON)",
                "Esempi di API RESTful",
                "Testing di status codes",
                "Gestione headers personalizzati",
                "Documentazione interattiva su /docs"
            ],
            "endpoints_principali": {
                "/docs": "Documentazione Swagger interattiva",
                "/prodotti": "API per gestione prodotti (e-commerce) - Supporta HTML + JSON",
                "/utenti": "API per gestione utenti",
                "/test": "Endpoint per testing vari scenari HTTP",
                "/download/postman-collection": "Download collezione Postman per test completi"
            }
        },
        endpoint="/"
    )

@app.get("/statistiche", response_model=RispostaHTTP, summary="📊 Statistiche del server")
async def ottieni_statistiche():
    """Mostra statistiche di utilizzo del server"""
    return crea_risposta(
        success=True,
        message="Statistiche aggiornate del server",
        data=contatori,
        endpoint="/statistiche"
    )

@app.get("/headers", response_model=Dict[str, str], summary="🔍 Ispeziona headers")
async def ispeziona_headers(request: Request):
    """Restituisce tutti gli headers della richiesta ricevuta"""
    return dict(request.headers)

@app.get("/user-agent", summary="🌐 Informazioni User-Agent")
async def analizza_user_agent(user_agent: str = Header(None)):
    """Analizza l'header User-Agent della richiesta"""
    if not user_agent:
        raise HTTPException(status_code=400, detail="Header User-Agent mancante")
    
    # Analisi semplificata dello User-Agent
    analisi = {
        "user_agent_completo": user_agent,
        "contiene_mobile": "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent,
        "browser_rilevato": None,
        "sistema_operativo": None
    }
    
    # Rilevamento browser
    if "Chrome" in user_agent:
        analisi["browser_rilevato"] = "Chrome"
    elif "Firefox" in user_agent:
        analisi["browser_rilevato"] = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        analisi["browser_rilevato"] = "Safari"
    elif "Edge" in user_agent:
        analisi["browser_rilevato"] = "Edge"
    
    # Rilevamento OS
    if "Windows" in user_agent:
        analisi["sistema_operativo"] = "Windows"
    elif "Mac OS" in user_agent:
        analisi["sistema_operativo"] = "macOS"
    elif "Linux" in user_agent:
        analisi["sistema_operativo"] = "Linux"
    elif "Android" in user_agent:
        analisi["sistema_operativo"] = "Android"
    elif "iOS" in user_agent:
        analisi["sistema_operativo"] = "iOS"
    
    return crea_risposta(
        success=True,
        message="Analisi User-Agent completata",
        data=analisi,
        endpoint="/user-agent"
    )

# ================================
# API PRODOTTI (E-COMMERCE SIMULATO)
# ================================

@app.get("/prodotti", summary="📦 Lista tutti i prodotti")
async def ottieni_prodotti(
    request: Request,
    accept: str = Header(None),
    categoria: Optional[str] = Query(None, description="Filtra per categoria"),
    disponibile: Optional[bool] = Query(None, description="Filtra per disponibilità"),
    prezzo_min: Optional[float] = Query(None, ge=0, description="Prezzo minimo"),
    prezzo_max: Optional[float] = Query(None, ge=0, description="Prezzo massimo"),
    limite: int = Query(10, ge=1, le=100, description="Numero massimo di risultati"),
    pagina: int = Query(1, ge=1, description="Numero di pagina")
):
    """
    Ottieni lista prodotti con filtri opzionali
    
    Dimostra:
    - Content Negotiation (HTML per browser, JSON per API)
    - Query parameters per filtri
    - Paginazione
    - Validazione parametri
    
    Header Accept:
    - text/html → Pagina HTML navigabile
    - application/json → Dati JSON strutturati
    """
    prodotti_filtrati = list(prodotti_db.values())
    
    # Applicazione filtri
    if categoria:
        prodotti_filtrati = [p for p in prodotti_filtrati if p.categoria.lower() == categoria.lower()]
    
    if disponibile is not None:
        prodotti_filtrati = [p for p in prodotti_filtrati if p.disponibile == disponibile]
    
    if prezzo_min is not None:
        prodotti_filtrati = [p for p in prodotti_filtrati if p.prezzo >= prezzo_min]
    
    if prezzo_max is not None:
        prodotti_filtrati = [p for p in prodotti_filtrati if p.prezzo <= prezzo_max]
    
    # Paginazione
    start_idx = (pagina - 1) * limite
    end_idx = start_idx + limite
    prodotti_paginati = prodotti_filtrati[start_idx:end_idx]
    
    # Content Negotiation
    if preferisce_html(accept):
        # Crea titolo dinamico basato sui filtri
        titolo = "Lista Prodotti"
        if categoria:
            titolo += f" - Categoria: {categoria.title()}"
        if disponibile is not None:
            titolo += f" - {'Disponibili' if disponibile else 'Non Disponibili'}"
        if prezzo_min or prezzo_max:
            range_prezzo = []
            if prezzo_min:
                range_prezzo.append(f"min €{prezzo_min}")
            if prezzo_max:
                range_prezzo.append(f"max €{prezzo_max}")
            titolo += f" - Prezzo: {', '.join(range_prezzo)}"
        
        return HTMLResponse(content=genera_html_prodotti(prodotti_paginati, titolo))
    
    # Risposta JSON per API client
    return crea_risposta(
        success=True,
        message=f"Trovati {len(prodotti_filtrati)} prodotti, mostrati {len(prodotti_paginati)}",
        data={
            "prodotti": prodotti_paginati,
            "paginazione": {
                "pagina_corrente": pagina,
                "limite_per_pagina": limite,
                "totale_risultati": len(prodotti_filtrati),
                "totale_pagine": (len(prodotti_filtrati) + limite - 1) // limite
            },
            "filtri_applicati": {
                "categoria": categoria,
                "disponibile": disponibile,
                "prezzo_min": prezzo_min,
                "prezzo_max": prezzo_max
            },
            "content_negotiation_info": {
                "formato_corrente": "JSON",
                "formati_supportati": ["application/json", "text/html"],
                "per_html": "Apri questo URL nel browser o usa: curl -H 'Accept: text/html' <URL>"
            }
        },
        endpoint="/prodotti"
    )

@app.get("/prodotti/{prodotto_id}", summary="🔍 Dettagli prodotto")
async def ottieni_prodotto(
    request: Request,
    accept: str = Header(None),
    prodotto_id: int = Path(..., ge=1, description="ID del prodotto")
):
    """
    Ottieni dettagli di un prodotto specifico
    
    Dimostra:
    - Path parameters con validazione
    - Status code 404 per risorsa non trovata
    - Content Negotiation (HTML + JSON)
    """
    if prodotto_id not in prodotti_db:
        raise HTTPException(
            status_code=404,
            detail=f"Prodotto con ID {prodotto_id} non trovato"
        )
    
    prodotto = prodotti_db[prodotto_id]
    
    # Content Negotiation
    if preferisce_html(accept):
        return HTMLResponse(content=genera_html_singolo_prodotto(prodotto))
    
    # Risposta JSON per API client
    return crea_risposta(
        success=True,
        message="Prodotto trovato",
        data={
            "prodotto": prodotto,
            "content_negotiation_info": {
                "formato_corrente": "JSON",
                "formato_alternativo": "HTML - Apri nel browser",
                "url_html": f"/prodotti/{prodotto_id}"
            }
        },
        endpoint=f"/prodotti/{prodotto_id}"
    )

@app.post("/prodotti", response_model=RispostaHTTP, status_code=201, summary="➕ Crea nuovo prodotto")
async def crea_prodotto(prodotto: Prodotto):
    """
    Crea un nuovo prodotto
    
    Dimostra:
    - Metodo POST per creazione
    - Status code 201 (Created)
    - Validazione automatica con Pydantic
    - Header Location per la risorsa creata
    """
    # Genera nuovo ID
    nuovo_id = max(prodotti_db.keys()) + 1 if prodotti_db else 1
    prodotto.id = nuovo_id
    
    # Salva nel database
    prodotti_db[nuovo_id] = prodotto
    
    # Crea risposta con header Location
    response = JSONResponse(
        status_code=201,
        content=crea_risposta(
            success=True,
            message="Prodotto creato con successo",
            data=prodotto,
            endpoint="/prodotti"
        ).dict(),
        headers={"Location": f"/prodotti/{nuovo_id}"}
    )
    
    return response

@app.put("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="🔄 Aggiorna prodotto (completo)")
async def aggiorna_prodotto_completo(
    prodotto_id: int = Path(..., ge=1),
    prodotto: Prodotto = None
):
    """
    Aggiornamento completo di un prodotto (PUT)
    
    Dimostra:
    - Metodo PUT per sostituzione completa
    - Differenza tra PUT e PATCH
    """
    if prodotto_id not in prodotti_db:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    
    prodotto.id = prodotto_id
    prodotti_db[prodotto_id] = prodotto
    
    return crea_risposta(
        success=True,
        message="Prodotto aggiornato completamente",
        data=prodotto,
        endpoint=f"/prodotti/{prodotto_id}"
    )

@app.patch("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="✏️ Aggiorna prodotto (parziale)")
async def aggiorna_prodotto_parziale(
    prodotto_id: int = Path(..., ge=1),
    aggiornamenti: AggiornaProdotto = None
):
    """
    Aggiornamento parziale di un prodotto (PATCH)
    
    Dimostra:
    - Metodo PATCH per modifiche parziali
    - Aggiornamento solo dei campi forniti
    """
    if prodotto_id not in prodotti_db:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    
    prodotto_esistente = prodotti_db[prodotto_id]
    
    # Applica solo i campi forniti
    dati_aggiornamento = aggiornamenti.dict(exclude_unset=True)
    for campo, valore in dati_aggiornamento.items():
        setattr(prodotto_esistente, campo, valore)
    
    return crea_risposta(
        success=True,
        message=f"Prodotto aggiornato parzialmente. Campi modificati: {list(dati_aggiornamento.keys())}",
        data=prodotto_esistente,
        endpoint=f"/prodotti/{prodotto_id}"
    )

@app.delete("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="🗑️ Elimina prodotto")
async def elimina_prodotto(prodotto_id: int = Path(..., ge=1)):
    """
    Elimina un prodotto
    
    Dimostra:
    - Metodo DELETE
    - Status code 204 per eliminazione riuscita
    """
    if prodotto_id not in prodotti_db:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")
    
    prodotto_eliminato = prodotti_db.pop(prodotto_id)
    
    return crea_risposta(
        success=True,
        message="Prodotto eliminato con successo",
        data={"prodotto_eliminato": prodotto_eliminato},
        endpoint=f"/prodotti/{prodotto_id}"
    )

# ================================
# API UTENTI
# ================================

@app.get("/utenti", response_model=RispostaHTTP, summary="👥 Lista utenti")
async def ottieni_utenti():
    """Lista tutti gli utenti registrati"""
    return crea_risposta(
        success=True,
        message="Lista utenti ottenuta",
        data=list(utenti_db.values()),
        endpoint="/utenti"
    )

@app.post("/utenti", response_model=RispostaHTTP, status_code=201, summary="👤 Crea utente")
async def crea_utente(utente: Utente):
    """Crea un nuovo utente"""
    nuovo_id = max(utenti_db.keys()) + 1 if utenti_db else 1
    utente.id = nuovo_id
    utenti_db[nuovo_id] = utente
    
    return crea_risposta(
        success=True,
        message="Utente creato con successo",
        data=utente,
        endpoint="/utenti"
    )

# ================================
# ENDPOINT PER TESTING HTTP
# ================================

@app.get("/test/status/{status_code}", summary="🧪 Test status codes")
async def test_status_code(status_code: int = Path(..., ge=100, le=599)):
    """
    Endpoint per testare diversi status codes HTTP
    
    Utile per vedere come il client gestisce diverse risposte
    """
    status_messages = {
        200: "OK - Richiesta riuscita",
        201: "Created - Risorsa creata",
        204: "No Content - Operazione riuscita senza contenuto",
        400: "Bad Request - Richiesta malformata",
        401: "Unauthorized - Autenticazione richiesta",
        403: "Forbidden - Accesso negato",
        404: "Not Found - Risorsa non trovata",
        409: "Conflict - Conflitto con lo stato corrente",
        422: "Unprocessable Entity - Dati non validi",
        500: "Internal Server Error - Errore del server",
        502: "Bad Gateway - Gateway non valido",
        503: "Service Unavailable - Servizio non disponibile"
    }
    
    message = status_messages.get(status_code, f"Status code {status_code}")
    
    if status_code >= 400:
        raise HTTPException(status_code=status_code, detail=message)
    
    return JSONResponse(
        status_code=status_code,
        content=crea_risposta(
            success=True,
            message=message,
            data={"status_code_richiesto": status_code},
            endpoint=f"/test/status/{status_code}"
        ).dict()
    )

@app.get("/test/delay/{secondi}", summary="⏱️ Test timeout e latenza")
async def test_delay(secondi: float = Path(..., ge=0.1, le=10)):
    """
    Endpoint che risponde dopo un delay specificato
    
    Utile per testare timeout e gestione latenza
    """
    import asyncio
    await asyncio.sleep(secondi)
    
    return crea_risposta(
        success=True,
        message=f"Risposta dopo {secondi} secondi di delay",
        data={"delay_richiesto": secondi},
        endpoint=f"/test/delay/{secondi}"
    )

@app.get("/test/headers-personalizzati", summary="📋 Test headers personalizzati")
async def test_headers_personalizzati(response: Response):
    """
    Endpoint che aggiunge headers personalizzati alla risposta
    
    Dimostra come impostare headers custom
    """
    response.headers["X-Custom-Header"] = "Valore-Personalizzato"
    response.headers["X-API-Version"] = "1.0.0"
    response.headers["X-Response-Time"] = datetime.now().isoformat()
    response.headers["X-Server-Name"] = "HTTP-Explorer"
    
    return crea_risposta(
        success=True,
        message="Risposta con headers personalizzati",
        data={"headers_aggiunti": ["X-Custom-Header", "X-API-Version", "X-Response-Time", "X-Server-Name"]},
        endpoint="/test/headers-personalizzati"
    )

@app.options("/test/cors", summary="🌐 Test CORS preflight")
async def test_cors_preflight():
    """
    Endpoint per testare richieste CORS preflight
    
    Dimostra come gestire richieste OPTIONS
    """
    return {"message": "CORS preflight riuscito", "metodi_permessi": ["GET", "POST", "PUT", "DELETE", "PATCH"]}

@app.head("/test/head", summary="🔍 Test metodo HEAD")
async def test_metodo_head():
    """
    Endpoint per testare il metodo HEAD
    
    HEAD restituisce solo gli headers, senza body
    """
    return {"message": "Questo body non sarà mai inviato con HEAD"}

@app.get("/test/content-negotiation", summary="🔄 Demo Content Negotiation")
async def demo_content_negotiation(
    request: Request,
    accept: str = Header(None),
    formato: Optional[str] = Query(None, description="Forza formato: 'html' o 'json'")
):
    """
    Endpoint dedicato per dimostrare Content Negotiation
    
    Mostra come lo stesso endpoint può restituire formati diversi:
    - Browser → HTML
    - API Client → JSON
    - Query parameter ?formato=html/json per forzare formato
    """
    
    # Forza formato se specificato via query parameter
    if formato == "html":
        deve_restituire_html = True
    elif formato == "json":
        deve_restituire_html = False
    else:
        # Usa content negotiation standard
        deve_restituire_html = preferisce_html(accept)
    
    dati_demo = {
        "titolo": "Content Negotiation Demo",
        "descrizione": "Questo endpoint dimostra come HTTP permette al client di specificare il formato preferito",
        "meccanismo": "Header Accept della richiesta",
        "formati_supportati": ["text/html", "application/json"],
        "esempi": {
            "browser": "Apri questo URL nel browser → ricevi HTML",
            "curl_json": "curl http://localhost:8000/test/content-negotiation → ricevi JSON",
            "curl_html": "curl -H 'Accept: text/html' http://localhost:8000/test/content-negotiation → ricevi HTML",
            "forzare_json": "/test/content-negotiation?formato=json",
            "forzare_html": "/test/content-negotiation?formato=html"
        },
        "header_ricevuto": accept or "Nessun header Accept",
        "decisione": "HTML" if deve_restituire_html else "JSON"
    }
    
    if deve_restituire_html:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Content Negotiation Demo - HTTP Explorer</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .demo-box {{ background: #e8f4fd; border: 2px solid #3498db; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .success {{ background: #d4edda; border-color: #28a745; }}
                .info {{ background: #d1ecf1; border-color: #17a2b8; }}
                .code {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; font-family: monospace; margin: 10px 0; }}
                .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                .btn:hover {{ background: #0056b3; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔄 Content Negotiation Demo</h1>
                
                <div class="demo-box success">
                    <h3>✅ Hai ricevuto HTML!</h3>
                    <p>Il tuo client ha inviato un header Accept che indica preferenza per HTML, oppure hai usato il parametro ?formato=html</p>
                    <p><strong>Header Accept ricevuto:</strong> <code>{accept or "Nessuno"}</code></p>
                </div>
                
                <div class="demo-box info">
                    <h3>🧠 Come funziona?</h3>
                    <p>La <strong>Content Negotiation</strong> permette allo stesso endpoint di restituire formati diversi basandosi sulle preferenze del client:</p>
                    <ul>
                        <li><strong>Browser</strong> → Invia <code>Accept: text/html</code> → Riceve pagina HTML</li>
                        <li><strong>API Client</strong> → Invia <code>Accept: application/json</code> → Riceve dati JSON</li>
                        <li><strong>curl senza header</strong> → Riceve JSON (default)</li>
                    </ul>
                </div>
                
                <div class="grid">
                    <div>
                        <h3>🌐 Testa nel Browser</h3>
                        <a href="/test/content-negotiation" class="btn">🔄 Ricarica (HTML)</a><br>
                        <a href="/test/content-negotiation?formato=json" class="btn">📄 Forza JSON</a>
                    </div>
                    
                    <div>
                        <h3>💻 Testa con curl</h3>
                        <div class="code">
                            # JSON (default)<br>
                            curl http://localhost:8000/test/content-negotiation<br><br>
                            
                            # HTML forzato<br>
                            curl -H "Accept: text/html" \\<br>
                            &nbsp;&nbsp;http://localhost:8000/test/content-negotiation
                        </div>
                    </div>
                </div>
                
                <div class="demo-box">
                    <h3>📊 Altri Endpoint con Content Negotiation</h3>
                    <p>Prova questi endpoint sia nel browser che con API client:</p>
                    <ul>
                        <li><a href="/prodotti">📦 /prodotti</a> - Lista prodotti</li>
                        <li><a href="/prodotti/1">🔍 /prodotti/1</a> - Singolo prodotto</li>
                        <li><a href="/">🏠 /</a> - Homepage</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/" class="btn">🏠 Homepage</a>
                    <a href="/docs" class="btn">📖 Documentazione API</a>
                    <a href="/download/postman-collection" class="btn" style="background: #28a745;">📥 Scarica Collezione Postman</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # Risposta JSON
    return crea_risposta(
        success=True,
        message="Content Negotiation Demo - Formato JSON",
        data=dati_demo,
        endpoint="/test/content-negotiation"
    )

def genera_collezione_postman() -> str:
    """
    Legge la collezione Postman da file e la restituisce come stringa JSON
    
    Returns:
        str: Contenuto del file collezione Postman in formato JSON
        
    Raises:
        HTTPException: Se il file non esiste o non è valido
    """
    import os
    import json
    from fastapi import HTTPException
    
    # Nome del file collezione (nella stessa directory del server)
    filename = "postman_collection.json"
    
    try:
        # Verifica se il file esiste
        if not os.path.exists(filename):
            raise HTTPException(
                status_code=404, 
                detail=f"File collezione Postman '{filename}' non trovato. Assicurati che il file sia presente nella directory del server."
            )
        
        # Legge il file
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verifica che sia JSON valido
        try:
            json.loads(content)  # Valida il JSON
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Il file '{filename}' contiene JSON non valido: {str(e)}"
            )
        
        return content
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' non trovato nella directory del server"
        )
    except PermissionError:
        raise HTTPException(
            status_code=500,
            detail=f"Permessi insufficienti per leggere il file '{filename}'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la lettura del file '{filename}': {str(e)}"
        )

@app.get("/download/postman-collection", summary="📥 Download Collezione Postman")
async def download_postman_collection():
    """
    Scarica la collezione Postman per testare tutti gli endpoint
    
    Restituisce il file JSON pronto per l'importazione in Postman.
    Il file include tutti gli endpoint organizzati per categoria con esempi.
    
    **Come usare:**
    1. Clicca su questo endpoint per scaricare
    2. Apri Postman
    3. Import → Upload Files → Seleziona il file scaricato
    4. La collezione sarà pronta per l'uso!
    """
    
    # Genera la collezione dinamicamente
    collezione_json = genera_collezione_postman()
    
    # Headers per il download del file
    headers = {
        "Content-Disposition": "attachment; filename=HTTP-Explorer-Collection.postman_collection.json",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    
    return Response(
        content=collezione_json,
        headers=headers,
        media_type="application/json"
    )

@app.get("/test/cache", summary="💾 Test caching HTTP")
async def test_cache(response: Response):
    """
    Endpoint per testare headers di cache HTTP
    """
    # Imposta headers di cache
    response.headers["Cache-Control"] = "public, max-age=3600"  # Cache per 1 ora
    response.headers["ETag"] = '"abc123def456"'  # Entity Tag per validazione
    response.headers["Last-Modified"] = "Wed, 21 Oct 2015 07:28:00 GMT"
    
    return crea_risposta(
        success=True,
        message="Risposta con headers di cache",
        data={"cache_info": "Questa risposta può essere cachata per 1 ora"},
        endpoint="/test/cache"
    )

@app.post("/test/echo", summary="🔄 Echo della richiesta")
async def echo_richiesta(request: Request):
    """
    Endpoint che restituisce tutti i dettagli della richiesta ricevuta
    
    Utile per debugging e comprensione delle richieste HTTP
    """
    body = await request.body()
    
    try:
        body_json = json.loads(body) if body else None
    except:
        body_json = None
    
    return crea_risposta(
        success=True,
        message="Echo della richiesta ricevuta",
        data={
            "metodo": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": dict(request.path_params),
            "body_raw": body.decode() if body else None,
            "body_json": body_json,
            "client_ip": request.client.host if request.client else None
        },
        endpoint="/test/echo"
    )

# ================================
# ENDPOINT DI UTILITÀ
# ================================

@app.get("/test/ip", summary="🌍 Il tuo indirizzo IP")
async def ottieni_ip_client(request: Request):
    """Restituisce l'indirizzo IP del client"""
    # Controlla headers di proxy (X-Forwarded-For, X-Real-IP)
    ip_forwarded = request.headers.get("X-Forwarded-For")
    ip_real = request.headers.get("X-Real-IP")
    ip_client = request.client.host if request.client else None
    
    return {
        "ip_rilevato": ip_forwarded or ip_real or ip_client,
        "dettagli": {
            "client_host": ip_client,
            "x_forwarded_for": ip_forwarded,
            "x_real_ip": ip_real
        }
    }

@app.get("/robots.txt", response_class=PlainTextResponse, summary="🤖 File robots.txt")
async def robots_txt():
    """File robots.txt standard per i web crawler"""
    return """User-agent: *
Allow: /
Disallow: /test/

# HTTP Explorer - Server didattico
# Crawl-delay: 1
"""

if __name__ == "__main__":
    print("🚀 Avvio HTTP Explorer Server...")
    print("📖 Documentazione: http://localhost:8000/docs")
    print("🔍 API Explorer: http://localhost:8000/redoc")
    print("🏠 Homepage: http://localhost:8000/")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )