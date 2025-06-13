"""
MODELS - Modelli Pydantic per validazione dati
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

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

class RisorsaCorso(BaseModel):
    """Modello per rappresentare una risorsa del corso"""
    nome: str
    descrizione: str
    tipo: str  # pdf, txt, zip, etc.
    dimensione: str
    url_download: str

# Database simulato in memoria
prodotti_db = {
    1: Prodotto(id=1, nome="Smartphone Pro", descrizione="Ultimo modello con 5G", prezzo=899.99, categoria="elettronica", tags=["mobile", "5g"]),
    2: Prodotto(id=2, nome="Laptop Gaming", descrizione="Potente laptop per gaming", prezzo=1299.99, categoria="computer", tags=["gaming", "performance"]),
    3: Prodotto(id=3, nome="Cuffie Wireless", descrizione="Audio di alta qualità", prezzo=199.99, categoria="audio", disponibile=False, tags=["wireless", "audio"])
}

utenti_db = {
    1: Utente(id=1, nome="Mario Rossi", email="mario@email.com", eta=30),
    2: Utente(id=2, nome="Giulia Bianchi", email="giulia@email.com", eta=25)
}