import uvicorn
from app import create_app

def main():
    """Avvia il server HTTP Explorer"""
    print("Avvio HTTP Explorer Server...")
    print("Documentazione: http://localhost:8000/docs")
    print("API Explorer: http://localhost:8000/redoc") 
    print("Homepage: http://localhost:8000/")
    print("Risorse corso: http://localhost:8000/risorse")
    
    uvicorn.run(
        "app:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        factory=True
    )

if __name__ == "__main__":
    main()