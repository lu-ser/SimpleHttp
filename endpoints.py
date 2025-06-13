"""
ENDPOINTS - Tutti gli endpoint dell'API
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Response, Header, Query, Path
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from models import (
    Prodotto, AggiornaProdotto, Utente, RispostaHTTP, Temperatura, CreaTemperatura,
    prodotti_db, utenti_db, temperature_db
)
from utils import (
    crea_risposta, preferisce_html, genera_html_prodotti,
    genera_html_singolo_prodotto, genera_html_homepage,
    leggi_collezione_postman, scansiona_cartella_download, contatori
)

def register_routes(app: FastAPI):
    """Registra tutti gli endpoint nell'app FastAPI"""
    
    # Monta la cartella download per servire file statici
    if os.path.exists("download"):
        app.mount("/download", StaticFiles(directory="download"), name="download")
    
    # ================================
    # ENDPOINT INFORMATIVI E DIAGNOSTICI
    # ================================

    @app.get("/", summary="Pagina principale")
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
                    "/risorse": "Risorse del corso scaricabili"
                }
            },
            endpoint="/"
        )

    @app.get("/statistiche", response_model=RispostaHTTP, summary="Statistiche del server")
    async def ottieni_statistiche():
        """Mostra statistiche di utilizzo del server"""
        return crea_risposta(
            success=True,
            message="Statistiche aggiornate del server",
            data=contatori,
            endpoint="/statistiche"
        )

    @app.get("/headers", response_model=Dict[str, str], summary="Ispeziona headers")
    async def ispeziona_headers(request: Request):
        """Restituisce tutti gli headers della richiesta ricevuta"""
        return dict(request.headers)

    @app.get("/user-agent", summary="Informazioni User-Agent")
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
    # RISORSE DEL CORSO
    # ================================

    @app.get("/risorse", summary="Risorse del corso")
    async def pagina_risorse(request: Request, accept: str = Header(None)):
        """
        Pagina con tutte le risorse del corso scaricabili
        """
        risorse = scansiona_cartella_download()
        
        if preferisce_html(accept):
            html_content = f"""
            <!DOCTYPE html>
            <html lang="it">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Risorse del Corso - HTTP Explorer</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 900px; margin: 0 auto; }}
                    h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px; }}
                    .intro {{ background: #e8f4fd; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .resources-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }}
                    .resource-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; transition: transform 0.2s; }}
                    .resource-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    .resource-type {{ display: inline-block; background: #6c757d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-bottom: 10px; }}
                    .resource-type.pdf {{ background: #dc3545; }}
                    .resource-type.txt {{ background: #28a745; }}
                    .resource-type.zip {{ background: #ffc107; color: #212529; }}
                    .resource-type.json {{ background: #17a2b8; }}
                    .download-btn {{ display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                    .download-btn:hover {{ background: #0056b3; }}
                    .no-resources {{ text-align: center; color: #6c757d; font-style: italic; padding: 40px; }}
                    .back-link {{ text-align: center; margin-top: 30px; }}
                    .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }}
                    .btn:hover {{ background: #545b62; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Risorse del Corso</h1>
                    
                    <div class="intro">
                        <h3>Materiali Didattici</h3>
                        <p>In questa sezione trovi tutti i materiali del corso "Didattica per il laboratorio di telecomunicazioni" che puoi scaricare e utilizzare per le tue lezioni.</p>
                        <p><strong>Suggerimento:</strong> Fai clic destro sui link di download e seleziona "Salva link con nome" per scaricare i file.</p>
                    </div>
            """
            
            if not risorse:
                html_content += """
                    <div class="no-resources">
                        <h3>Nessuna risorsa disponibile</h3>
                        <p>Al momento non ci sono risorse nella cartella download.</p>
                        <p>Il docente può aggiungere file nella cartella 'download' del progetto.</p>
                    </div>
                """
            else:
                html_content += '<div class="resources-grid">'
                for risorsa in risorse:
                    html_content += f"""
                    <div class="resource-card">
                        <span class="resource-type {risorsa.tipo}">{risorsa.tipo.upper()}</span>
                        <h3>{risorsa.nome}</h3>
                        <p>{risorsa.descrizione}</p>
                        <p><strong>Dimensione:</strong> {risorsa.dimensione}</p>
                        <a href="{risorsa.url_download}" class="download-btn" download>Scarica</a>
                    </div>
                    """
                html_content += '</div>'
            
            html_content += """
                    <div class="back-link">
                        <a href="/" class="btn">Torna alla Homepage</a>
                        <a href="/docs" class="btn">Documentazione API</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # Risposta JSON per API client
        return crea_risposta(
            success=True,
            message=f"Trovate {len(risorse)} risorse del corso",
            data=risorse,
            endpoint="/risorse"
        )

    # ================================
    # API PRODOTTI (E-COMMERCE SIMULATO)
    # ================================

    @app.get("/prodotti", summary="Lista tutti i prodotti")
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
                }
            },
            endpoint="/prodotti"
        )

    @app.get("/prodotti/{prodotto_id}", summary="Dettagli prodotto")
    async def ottieni_prodotto(
        request: Request,
        accept: str = Header(None),
        prodotto_id: int = Path(..., ge=1, description="ID del prodotto")
    ):
        """Ottieni dettagli di un prodotto specifico"""
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
            data=prodotto,
            endpoint=f"/prodotti/{prodotto_id}"
        )

    @app.post("/prodotti", response_model=RispostaHTTP, status_code=201, summary="Crea nuovo prodotto")
    async def crea_prodotto(prodotto: Prodotto):
        """Crea un nuovo prodotto"""
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

    @app.put("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="Aggiorna prodotto (completo)")
    async def aggiorna_prodotto_completo(
        prodotto_id: int = Path(..., ge=1),
        prodotto: Prodotto = None
    ):
        """Aggiornamento completo di un prodotto (PUT)"""
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

    @app.patch("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="Aggiorna prodotto (parziale)")
    async def aggiorna_prodotto_parziale(
        prodotto_id: int = Path(..., ge=1),
        aggiornamenti: AggiornaProdotto = None
    ):
        """Aggiornamento parziale di un prodotto (PATCH)"""
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

    @app.delete("/prodotti/{prodotto_id}", response_model=RispostaHTTP, summary="Elimina prodotto")
    async def elimina_prodotto(prodotto_id: int = Path(..., ge=1)):
        """Elimina un prodotto"""
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

    @app.get("/utenti", response_model=RispostaHTTP, summary="Lista utenti")
    async def ottieni_utenti():
        """Lista tutti gli utenti registrati"""
        return crea_risposta(
            success=True,
            message="Lista utenti ottenuta",
            data=list(utenti_db.values()),
            endpoint="/utenti"
        )

    @app.post("/utenti", response_model=RispostaHTTP, status_code=201, summary="Crea utente")
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
    # API TEMPERATURE (IoT)
    # ================================

    @app.get("/temperature", response_model=RispostaHTTP, summary="Lista temperature")
    async def ottieni_temperature(
        sensore: Optional[str] = Query(None, description="Filtra per sensore"),
        posizione: Optional[str] = Query(None, description="Filtra per posizione"),
        limite: int = Query(10, ge=1, le=100, description="Numero massimo di risultati")
    ):
        """
        Lista le letture di temperatura con filtri opzionali
        
        Utile per simulare sensori IoT che inviano dati
        """
        temperature_filtrate = list(temperature_db.values())
        
        # Applica filtri
        if sensore:
            temperature_filtrate = [t for t in temperature_filtrate if t.sensore.lower() == sensore.lower()]
        
        if posizione:
            temperature_filtrate = [t for t in temperature_filtrate if t.posizione and posizione.lower() in t.posizione.lower()]
        
        # Ordina per timestamp (più recenti prima)
        temperature_filtrate.sort(key=lambda x: x.timestamp or "", reverse=True)
        
        # Applica limite
        temperature_filtrate = temperature_filtrate[:limite]
        
        return crea_risposta(
            success=True,
            message=f"Trovate {len(temperature_filtrate)} letture di temperatura",
            data={
                "temperature": temperature_filtrate,
                "statistiche": {
                    "totale_letture": len(temperature_db),
                    "sensori_attivi": len(set(t.sensore for t in temperature_db.values())),
                    "temperatura_media": round(sum(t.valore for t in temperature_db.values()) / len(temperature_db), 2)
                },
                "filtri_applicati": {
                    "sensore": sensore,
                    "posizione": posizione,
                    "limite": limite
                }
            },
            endpoint="/temperature"
        )

    @app.post("/temperature", response_model=RispostaHTTP, status_code=201, summary="Invia temperatura")
    async def invia_temperatura(temperatura: CreaTemperatura):
        """
        Invia una nuova lettura di temperatura
        
        Simula un sensore IoT che invia dati al server
        """
        from datetime import datetime
        
        # Genera nuovo ID
        nuovo_id = max(temperature_db.keys()) + 1 if temperature_db else 1
        
        # Crea la temperatura con timestamp automatico
        nuova_temperatura = Temperatura(
            id=nuovo_id,
            valore=temperatura.valore,
            sensore=temperatura.sensore,
            timestamp=datetime.now().isoformat(),
            unita=temperatura.unita,
            posizione=temperatura.posizione
        )
        
        # Salva nel database
        temperature_db[nuovo_id] = nuova_temperatura
        
        return crea_risposta(
            success=True,
            message="Temperatura registrata con successo",
            data=nuova_temperatura,
            endpoint="/temperature"
        )

    @app.get("/temperature/{temperatura_id}", response_model=RispostaHTTP, summary="Dettagli temperatura")
    async def ottieni_temperatura(temperatura_id: int = Path(..., ge=1, description="ID della lettura")):
        """Ottieni dettagli di una specifica lettura di temperatura"""
        if temperatura_id not in temperature_db:
            raise HTTPException(
                status_code=404,
                detail=f"Lettura temperatura con ID {temperatura_id} non trovata"
            )
        
        temperatura = temperature_db[temperatura_id]
        
        return crea_risposta(
            success=True,
            message="Lettura temperatura trovata",
            data=temperatura,
            endpoint=f"/temperature/{temperatura_id}"
        )

    @app.delete("/temperature/{temperatura_id}", response_model=RispostaHTTP, summary="Elimina temperatura")
    async def elimina_temperatura(temperatura_id: int = Path(..., ge=1)):
        """Elimina una lettura di temperatura"""
        if temperatura_id not in temperature_db:
            raise HTTPException(status_code=404, detail="Lettura temperatura non trovata")
        
        temperatura_eliminata = temperature_db.pop(temperatura_id)
        
        return crea_risposta(
            success=True,
            message="Lettura temperatura eliminata con successo",
            data={"temperatura_eliminata": temperatura_eliminata},
            endpoint=f"/temperature/{temperatura_id}"
        )

    @app.get("/temperature/sensore/{nome_sensore}", response_model=RispostaHTTP, summary="Temperature per sensore")
    async def temperature_per_sensore(nome_sensore: str = Path(..., description="Nome del sensore")):
        """Ottieni tutte le letture di un sensore specifico"""
        letture_sensore = [t for t in temperature_db.values() if t.sensore.lower() == nome_sensore.lower()]
        
        if not letture_sensore:
            raise HTTPException(
                status_code=404,
                detail=f"Nessuna lettura trovata per il sensore {nome_sensore}"
            )
        
        # Ordina per timestamp
        letture_sensore.sort(key=lambda x: x.timestamp or "", reverse=True)
        
        # Calcola statistiche
        valori = [t.valore for t in letture_sensore]
        statistiche = {
            "numero_letture": len(letture_sensore),
            "temperatura_minima": min(valori),
            "temperatura_massima": max(valori),
            "temperatura_media": round(sum(valori) / len(valori), 2),
            "ultima_lettura": letture_sensore[0].timestamp if letture_sensore else None
        }
        
        return crea_risposta(
            success=True,
            message=f"Letture del sensore {nome_sensore}",
            data={
                "sensore": nome_sensore,
                "letture": letture_sensore,
                "statistiche": statistiche
            },
            endpoint=f"/temperature/sensore/{nome_sensore}"
        )

    # ================================
    # ENDPOINT PER TESTING HTTP
    # ================================

    @app.get("/test/status/{status_code}", summary="Test status codes")
    async def test_status_code(status_code: int = Path(..., ge=100, le=599)):
        """Endpoint per testare diversi status codes HTTP"""
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

    @app.get("/test/delay/{secondi}", summary="Test timeout e latenza")
    async def test_delay(secondi: float = Path(..., ge=0.1, le=10)):
        """Endpoint che risponde dopo un delay specificato"""
        await asyncio.sleep(secondi)
        
        return crea_risposta(
            success=True,
            message=f"Risposta dopo {secondi} secondi di delay",
            data={"delay_richiesto": secondi},
            endpoint=f"/test/delay/{secondi}"
        )

    @app.get("/test/headers-personalizzati", summary="Test headers personalizzati")
    async def test_headers_personalizzati(response: Response):
        """Endpoint che aggiunge headers personalizzati alla risposta"""
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

    @app.options("/test/cors", summary="Test CORS preflight")
    async def test_cors_preflight():
        """Endpoint per testare richieste CORS preflight"""
        return {"message": "CORS preflight riuscito", "metodi_permessi": ["GET", "POST", "PUT", "DELETE", "PATCH"]}

    @app.head("/test/head", summary="Test metodo HEAD")
    async def test_metodo_head():
        """Endpoint per testare il metodo HEAD"""
        return {"message": "Questo body non sarà mai inviato con HEAD"}

    @app.get("/test/content-negotiation", summary="Demo Content Negotiation")
    async def demo_content_negotiation(
        request: Request,
        accept: str = Header(None),
        formato: Optional[str] = Query(None, description="Forza formato: 'html' o 'json'")
    ):
        """Endpoint dedicato per dimostrare Content Negotiation"""
        
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
                    <h1>Content Negotiation Demo</h1>
                    
                    <div class="demo-box success">
                        <h3>Hai ricevuto HTML!</h3>
                        <p>Il tuo client ha inviato un header Accept che indica preferenza per HTML, oppure hai usato il parametro ?formato=html</p>
                        <p><strong>Header Accept ricevuto:</strong> <code>{accept or "Nessuno"}</code></p>
                    </div>
                    
                    <div class="demo-box info">
                        <h3>Come funziona?</h3>
                        <p>La <strong>Content Negotiation</strong> permette allo stesso endpoint di restituire formati diversi basandosi sulle preferenze del client:</p>
                        <ul>
                            <li><strong>Browser</strong> → Invia <code>Accept: text/html</code> → Riceve pagina HTML</li>
                            <li><strong>API Client</strong> → Invia <code>Accept: application/json</code> → Riceve dati JSON</li>
                            <li><strong>curl senza header</strong> → Riceve JSON (default)</li>
                        </ul>
                    </div>
                    
                    <div class="grid">
                        <div>
                            <h3>Testa nel Browser</h3>
                            <a href="/test/content-negotiation" class="btn">Ricarica (HTML)</a><br>
                            <a href="/test/content-negotiation?formato=json" class="btn">Forza JSON</a>
                        </div>
                        
                        <div>
                            <h3>Testa con curl</h3>
                            <div class="code">
                                # JSON (default)<br>
                                curl http://localhost:8000/test/content-negotiation<br><br>
                                
                                # HTML forzato<br>
                                curl -H "Accept: text/html" \\<br>
                                &nbsp;&nbsp;http://localhost:8000/test/content-negotiation
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="/" class="btn">Homepage</a>
                        <a href="/docs" class="btn">Documentazione API</a>
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

    @app.get("/postman-collection", summary="Download Collezione Postman")
    async def download_postman_collection():
        """Scarica la collezione Postman per testare tutti gli endpoint"""
        
        # Genera la collezione dinamicamente
        collezione_json = leggi_collezione_postman()
        
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

    @app.get("/test/cache", summary="Test caching HTTP")
    async def test_cache(response: Response):
        """Endpoint per testare headers di cache HTTP"""
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

    @app.post("/test/echo", summary="Echo della richiesta")
    async def echo_richiesta(request: Request):
        """Endpoint che restituisce tutti i dettagli della richiesta ricevuta"""
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

    @app.get("/test/ip", summary="Il tuo indirizzo IP")
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

    @app.get("/robots.txt", response_class=PlainTextResponse, summary="File robots.txt")
    async def robots_txt():
        """File robots.txt standard per i web crawler"""
        return """User-agent: *
Allow: /
Disallow: /test/

# HTTP Explorer - Server didattico
# Crawl-delay: 1
"""