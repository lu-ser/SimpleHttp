# HTTP Explorer - Laboratorio Didattico

Server educativo per il corso "Didattica per il laboratorio di telecomunicazioni".

## Struttura del Progetto

```
http-explorer/
├── main.py              # Avvio del server
├── app.py               # Configurazione FastAPI e middleware
├── models.py            # Modelli Pydantic per validazione dati
├── endpoints.py         # Tutti gli endpoint dell'API
├── utils.py             # Funzioni di utilità e helper
├── download/            # Cartella con risorse del corso
│   ├── guida-http.txt
│   ├── esercizi-laboratorio.txt
│   └── postman-examples.json
├── postman_collection.json  # Collezione Postman (opzionale)
└── README.md
```

## Installazione e Avvio

1. **Installa le dipendenze:**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Avvia il server:**
   ```bash
   python main.py
   ```

3. **Accedi al server:**
   - Homepage: http://localhost:8000/
   - Documentazione API: http://localhost:8000/docs
   - Risorse del corso: http://localhost:8000/risorse

## Funzionalità Principali

### Content Negotiation
Il server dimostra la **Content Negotiation** HTTP - la capacità di restituire formati diversi basandosi sull'header `Accept`:

- **Browser** → Riceve pagine HTML navigabili
- **API Client** → Riceve dati JSON strutturati
- **curl** senza header → Riceve JSON (default)

### Endpoint Didattici

1. **API Prodotti** (`/prodotti`)
   - GET, POST, PUT, PATCH, DELETE
   - Filtri e paginazione
   - Validazione con Pydantic

2. **Testing HTTP** (`/test/*`)
   - Status codes (`/test/status/404`)
   - Headers personalizzati
   - Timeout e latenza
   - Cache HTTP
   - Echo delle richieste

3. **Risorse del Corso** (`/risorse`)
   - Download di materiali didattici
   - File nella cartella `download/`

## Aggiungere Risorse del Corso

Per aggiungere materiali scaricabili:

1. Crea la cartella `download/` se non esiste
2. Aggiungi i tuoi file (PDF, TXT, ZIP, etc.)
3. I file saranno automaticamente disponibili su `/risorse`

Esempio:
```
download/
├── guida-protocollo-http.pdf
├── esercizi-laboratorio.txt
├── slides-lezione-1.pdf
└── codici-esempio.zip
```

## Esempi di Utilizzo

### Testare Content Negotiation

```bash
# Ricevi JSON (default)
curl http://localhost:8000/prodotti

# Forza HTML
curl -H "Accept: text/html" http://localhost:8000/prodotti

# Nel browser (ricevi HTML automaticamente)
# http://localhost:8000/prodotti
```

### Testare Status Codes

```bash
# Test 404
curl http://localhost:8000/test/status/404

# Test 500
curl http://localhost:8000/test/status/500
```

### Creare un Prodotto

```bash
curl -X POST http://localhost:8000/prodotti \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Nuovo Prodotto",
    "descrizione": "Descrizione del prodotto",
    "prezzo": 29.99,
    "categoria": "elettronica"
  }'
```

## Personalizzazione

Il server è facilmente estendibile:

- **Aggiungi endpoint** in `endpoints.py`
- **Modifica modelli dati** in `models.py`
- **Personalizza HTML** nelle funzioni in `utils.py`
- **Aggiungi middleware** in `app.py`

## Requisiti Tecnici

- Python 3.7+
- FastAPI
- Uvicorn
- Pydantic (incluso con FastAPI)

## Supporto

Per domande o problemi:
- Consulta la documentazione su `/docs`
- Controlla i log del server nella console
- Verifica che la porta 8000 sia libera