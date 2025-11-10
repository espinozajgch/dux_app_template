# Dux App

Aplicación en Streamlit.

## Estructura

```
app.py
src/
  auth.py
  io_files.py
  schema.py
  ui_components.py
data/
  jugadoras.xlsx        # (sube aquí tu archivo con columnas: id_jugadora, nombre_jugadora)
  partes_cuerpo.xlsx    # (sube aquí tu archivo con columna: parte)
  registros.jsonl       # se crea automáticamente (JSON Lines)
requirements.txt
README.md
```

## Requisitos

- Python 3.9+
- pip

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Auth

El sistema de autenticación desarrollado para este proyecto está diseñado para ser seguro, modular y reutilizable entre distintas aplicaciones. Está compuesto por tres capas principales: configuración, lógica base e interfaz de usuario, lo que permite mantener una arquitectura limpia y fácilmente integrable.

Principales características

#### **Autenticación JWT (JSON Web Tokens)**

- Uso de JWT firmados con algoritmo HS256 y un tiempo de expiración configurable (st.secrets["auth"]["time"]).
- Cada token contiene la identidad del usuario, su rol y una fecha de expiración.
- Los tokens se almacenan cifrados y se renuevan automáticamente al volver a iniciar sesión.

#### **Manejo de sesiones seguras con cookies cifradas**

- Implementación con EncryptedCookieManager, usando un secreto distinto al del JWT.
- Cada usuario tiene su propia cookie cifrada, identificada como auth_token_usuario@correo.
- Las sesiones son independientes entre usuarios y navegadores, incluso en Streamlit Cloud gratuito.
- El cierre de sesión (logout()) solo afecta al usuario actual, sin interferir en otras sesiones activas.

## Notas

- Vista de una sola página, previsualización antes de guardar y botón deshabilitado hasta cumplir validaciones.
- Tras guardar, se limpia el formulario (recarga de la app).

## Contributing

- Haz un fork del repositorio.
- Configuración de remoto

- Crea una rama nueva para tus cambios
- Realiza tus modificaciones y haz commit
- Haz push a tu fork
- Abre un Pull Request al repositorio original