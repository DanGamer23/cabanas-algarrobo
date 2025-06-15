🏡 Proyecto Cabañas Algarrobo ☀️
¡Bienvenido al proyecto Cabañas Algarrobo! Esta plataforma integral está diseñada para simplificar la gestión y reserva de cabañas, ofreciendo una experiencia fluida tanto para administradores como para usuarios.

📝 Descripción del Proyecto
Cabañas Algarrobo es una solución completa que consta de una aplicación web robusta desarrollada con Django para la administración y visualización, y una API potente construida con FastAPI para la gestión de usuarios y otras funcionalidades clave.

Los usuarios pueden:

Registrarse e iniciar sesión de forma segura.
Explorar las cabañas disponibles.
Realizar reservas de manera sencilla.
Completar pagos de forma eficiente.
El panel administrativo proporciona herramientas completas para la gestión de:

Cabañas
Reservas
Pagos
Usuarios
🛠️ Tecnologías Utilizadas
Este proyecto ha sido construido con tecnologías modernas y eficientes:

Django 5.2: Para el desarrollo de la aplicación web principal.
FastAPI: Para la creación de la API RESTful.
MySQL: Como sistema de gestión de bases de datos.
Bootstrap 5: Para un diseño responsivo y atractivo en el frontend.
SQLAlchemy: Como ORM para la interacción con la base de datos en la API.
Python 3.11: El lenguaje de programación base para todo el proyecto.
🚀 Instalación del Proyecto
Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

Clona el repositorio:

Bash

git clone https://github.com/tu_usuario/cabanas-algarrobo.git
cd cabanas-algarrobo
(Opcional, pero muy recomendado) Crea y activa un entorno virtual:

Bash

python -m venv venv
En Windows:
Bash

venv\Scripts\activate
En Linux / macOS:
Bash

source venv/bin/activate
Instala las dependencias necesarias:

Bash

pip install -r requirements.txt
Configura tu base de datos MySQL:
Asegúrate de haber creado una base de datos y un usuario dedicados para este proyecto en MySQL.

Configura las variables de entorno:
Crea un archivo .env (o similar) y define las variables de entorno requeridas para la conexión a la base de datos y otras configuraciones.

Ejecuta las migraciones de la base de datos:

Bash

python manage.py migrate
Ejecuta el servidor de Django:

Bash

python manage.py runserver
Ejecuta la API de FastAPI (en una terminal separada):

Bash

uvicorn main:app --reload --port 8001
💻 Uso de la Aplicación
Una vez que ambos servidores estén en funcionamiento:

Accede a la aplicación web en tu navegador:
http://localhost:8000

La API de FastAPI estará disponible para pruebas en:
http://localhost:8001/docs (documentación interactiva de Swagger UI)