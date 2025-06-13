import os

def create_directories_and_files():
    structure = [
        # File principali
        "main.py",
        "requirements.txt",
        "README.md",

        # Directory app
        "app/__init__.py",
        "app/main.py",

        # Sottodirectory di app e relativi file
        "app/api/__init__.py",
        "app/api/products.py",
        "app/api/users.py",
        "app/api/testing.py",
        "app/api/resources.py",

        "app/models/__init__.py",
        "app/models/products.py",
        "app/models/users.py",
        "app/models/responses.py",

        "app/templates/base.html",
        "app/templates/homepage.html",
        "app/templates/products_list.html",
        "app/templates/product_detail.html",
        "app/templates/content_negotiation.html",
        "app/templates/resources.html",

        "app/static/css/style.css",
        "app/static/js/main.js",

        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/middleware.py",
        "app/core/utils.py",

        "app/database/__init__.py",
        "app/database/fake_db.py",

        # Directory download
        "download/esempi/client_http_examples.py",
        "download/esempi/rest_api_examples.json",
        "download/esempi/curl_commands.sh",

        "download/documentazione/guida_protocollo_http.pdf",
        "download/documentazione/http_status_codes.pdf",
        "download/documentazione/rest_api_best_practices.pdf",

        "download/tools/postman_collection.json",
        "download/tools/http_tester.html",
        "download/tools/network_analyzer.py",

        "download/laboratori/lab01_basic_http.md",
        "download/laboratori/lab02_rest_api.md",
        "download/laboratori/lab03_content_negotiation.md",

        # Directory tests
        "tests/__init__.py",
        "tests/test_api.py",
        "tests/test_content_negotiation.py",
    ]

    for path in structure:
        directory = os.path.dirname(path)
        if directory:  # Crea directory solo se il percorso non è vuoto
            os.makedirs(directory, exist_ok=True)
        if "." in os.path.basename(path):  # Crea i file richiesti
            with open(path, "w") as f:
                pass  # Crea file vuoto

    print("Struttura creata con successo!")

if __name__ == "__main__":
    create_directories_and_files()