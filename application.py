"""Punto de entrada WSGI. AWS Elastic Beanstalk busca `application` en este modulo."""

from src import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
