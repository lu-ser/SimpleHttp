"""
UTILS - Funzioni di utilità e helper
"""

import os
import json
from datetime import datetime
from typing import List
from fastapi import HTTPException
from models import RispostaHTTP, Prodotto, RisorsaCorso

# Contatori per statistiche
contatori = {
    "visite_totali": 0,
    "richieste_per_metodo": {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
}

def crea_risposta(success: bool, message: str, data: any = None, endpoint: str = "") -> RispostaHTTP:
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
            <h1>{titolo}</h1>
            
            <div class="api-info">
                <strong>Content Negotiation Demo</strong><br>
                Questo endpoint restituisce HTML per browser e JSON per API client!<br>
                <a href="/prodotti" class="json-link">Versione JSON</a>
                <span style="margin: 0 10px;">•</span>
                <a href="/docs#/API%20Prodotti%20(E-commerce%20RESTful)/ottieni_prodotti_prodotti_get" class="json-link">Documentazione API</a>
            </div>
    """
    
    if not prodotti:
        html += "<p>Nessun prodotto trovato.</p>"
    else:
        for prodotto in prodotti:
            disponibilita = "Disponibile" if prodotto.disponibile else "Non disponibile"
            disponibilita_class = "available" if prodotto.disponibile else "unavailable"
            
            tags_html = ""
            if prodotto.tags:
                tags_html = "<div class='tags'>" + "".join([f"<span class='tag'>{tag}</span>" for tag in prodotto.tags]) + "</div>"
            
            html += f"""
            <div class="product">
                <h3>{prodotto.nome}</h3>
                <p><strong>Descrizione:</strong> {prodotto.descrizione or 'Nessuna descrizione'}</p>
                <p class="price">€{prodotto.prezzo:.2f}</p>
                <p><span class="category">{prodotto.categoria}</span></p>
                <p class="{disponibilita_class}">{disponibilita}</p>
                {tags_html}
                <small style="color: #666;">ID: {prodotto.id}</small>
            </div>
            """
    
    html += """
            <hr style="margin: 30px 0;">
            <div style="text-align: center; color: #666;">
                <p><strong>HTTP Explorer</strong> - Server didattico per il protocollo HTTP</p>
                <p><a href="/">Homepage</a> • <a href="/docs">Documentazione API</a> • <a href="/statistiche">Statistiche</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def genera_html_singolo_prodotto(prodotto: Prodotto) -> str:
    """Genera HTML per singolo prodotto"""
    disponibilita = "Disponibile" if prodotto.disponibile else "Non disponibile"
    disponibilita_class = "available" if prodotto.disponibile else "unavailable"
    
    tags_html = ""
    if prodotto.tags:
        tags_html = "<div class='tags'><strong>Tags:</strong> " + "".join([f"<span class='tag'>{tag}</span>" for tag in prodotto.tags]) + "</div>"
    
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
            <h1>{prodotto.nome}</h1>
            
            <div class="info-row">
                <strong>Descrizione:</strong><br>
                {prodotto.descrizione or 'Nessuna descrizione disponibile'}
            </div>
            
            <div class="price">€{prodotto.prezzo:.2f}</div>
            
            <div class="info-row">
                <strong>Categoria:</strong> <span class="category">{prodotto.categoria}</span>
            </div>
            
            <div class="info-row">
                <strong>Disponibilità:</strong> <span class="{disponibilita_class}">{disponibilita}</span>
            </div>
            
            {tags_html}
            
            <div class="info-row">
                <strong>ID Prodotto:</strong> {prodotto.id}
            </div>
            
            <div class="actions">
                <a href="/prodotti" class="btn btn-primary">Tutti i Prodotti</a>
                <a href="/prodotti/{prodotto.id}" class="btn btn-success">Versione JSON</a>
                <a href="/docs" class="btn btn-secondary">API Docs</a>
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
            .feature-list li:before { content: "✓ "; color: #28a745; font-weight: bold; }
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
                <h1>HTTP Explorer</h1>
                <p>Laboratorio Didattico per il Protocollo HTTP</p>
            </div>
            
            <div class="card">
                <h2>Benvenuto nel Laboratorio HTTP!</h2>
                <p>Questo server ti permette di esplorare tutti gli aspetti del protocollo HTTP attraverso esempi pratici e interattivi.</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/docs" class="btn btn-success">Documentazione Interattiva (Swagger)</a>
                    <a href="/prodotti" class="btn">API Prodotti</a>
                    <a href="/risorse" class="btn btn-warning">Risorse del Corso</a>
                    <a href="/statistiche" class="btn btn-warning">Statistiche Server</a>
                </div>
            </div>
            
            <div class="features">
                <div class="card">
                    <h2>Funzionalità</h2>
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
                
                
            </div>
            
            <div class="card">
                <h2>Endpoint Principali</h2>
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
        </div>
    </body>
    </html>
    """

def leggi_collezione_postman() -> str:
    """Legge la collezione Postman da file"""
    filename = "postman_collection.json"
    
    try:
        if not os.path.exists(filename):
            raise HTTPException(
                status_code=404, 
                detail=f"File collezione Postman '{filename}' non trovato"
            )
        
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verifica che sia JSON valido
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Il file '{filename}' contiene JSON non valido: {str(e)}"
            )
        
        return content
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' non trovato"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la lettura del file: {str(e)}"
        )

def scansiona_cartella_download() -> List[RisorsaCorso]:
    """Scansiona la cartella download e restituisce l'elenco delle risorse"""
    cartella_download = "download"
    risorse = []
    
    if not os.path.exists(cartella_download):
        return risorse
    
    for filename in os.listdir(cartella_download):
        filepath = os.path.join(cartella_download, filename)
        if os.path.isfile(filepath):
            # Calcola dimensione file
            dimensione_bytes = os.path.getsize(filepath)
            if dimensione_bytes < 1024:
                dimensione = f"{dimensione_bytes} bytes"
            elif dimensione_bytes < 1024 * 1024:
                dimensione = f"{dimensione_bytes / 1024:.1f} KB"
            else:
                dimensione = f"{dimensione_bytes / (1024 * 1024):.1f} MB"
            
            # Determina tipo file
            estensione = filename.split('.')[-1].lower() if '.' in filename else 'file'
            
            # Genera descrizione basata sul nome file
            nome_pulito = filename.replace('_', ' ').replace('-', ' ')
            if '.' in nome_pulito:
                nome_pulito = '.'.join(nome_pulito.split('.')[:-1])
            
            risorsa = RisorsaCorso(
                nome=nome_pulito.title(),
                descrizione=f"File {estensione.upper()} - {nome_pulito}",
                tipo=estensione,
                dimensione=dimensione,
                url_download=f"/download/{filename}"
            )
            risorse.append(risorsa)
    
    return sorted(risorse, key=lambda x: x.nome)