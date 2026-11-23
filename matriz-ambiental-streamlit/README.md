# Matriz de obligaciones y cumplimiento ambiental

Aplicación web hecha con [Streamlit](https://streamlit.io) para registrar obligaciones ambientales
(legales, compromisos del instrumento de gestión y requisitos voluntarios como ISO 14001),
dar seguimiento a su estado y calcular indicadores de cumplimiento.

## Funciones

- Tabla editable: obligación, norma, tipo, autoridad, frecuencia, responsable, fecha límite, estado y evidencia.
- Estados: Cumple, Parcial, No cumple y No aplica.
- Indicadores: cumplimiento (%), cumplimiento ponderado, obligaciones vencidas, gráfico por estado y cruce por tipo.
- Lista de pendientes ordenada por días para el plazo.
- Carga y descarga en Excel o CSV (`data/plantilla_ejemplo.csv` sirve de plantilla).

## Ejecutar en tu computadora

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (el archivo `app.py` debe quedar en la raíz).
2. Entra a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub.
3. Elige **Create app**, selecciona tu repositorio y la rama, y escribe `app.py` como archivo principal.
4. Pulsa **Deploy**. Streamlit instalará lo que figura en `requirements.txt`.

## Subir a GitHub

```bash
git init
git add .
git commit -m "Matriz de obligaciones y cumplimiento ambiental"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/matriz-ambiental-streamlit.git
git push -u origin main
```

## Notas

- La app no guarda datos en un servidor: descarga tu matriz y vuelve a cargarla cuando la necesites.
- Las normas del ejemplo son referenciales (Perú). Verifica su vigencia antes de usarlas en un trabajo o una auditoría.
- Cálculo: cumplimiento = Cumple ÷ (total − No aplica). El ponderado cuenta Parcial como 0,5.

## Estructura

```
app.py
requirements.txt
.streamlit/config.toml
data/plantilla_ejemplo.csv
README.md
```
