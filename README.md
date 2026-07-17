# Atrapa Estrellas Web

Videojuego 2D creado con Python, Pygame Community Edition y Pygbag. Está preparado para ejecutarse en computadora y publicarse como juego web en GitHub Pages, compatible con navegadores Android modernos.

## 1. Requisitos

- Python 3.12 o superior
- Visual Studio Code
- Git
- Una cuenta de GitHub

## 2. Abrir el proyecto en VS Code

Abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
code .
```

## 3. Crear el entorno virtual

En PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, ejecuta una vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Probar como aplicación de escritorio

```powershell
python main.py
```

Controles:

- Celular: toca y desliza horizontalmente.
- Computadora: flechas izquierda/derecha o teclas A/D.
- Espacio o Enter: iniciar/reiniciar.

## 5. Probar en el navegador local

Desde la carpeta del proyecto:

```powershell
python -m pygbag --ume_block 0 --can_close 1 .
```

Cuando termine de preparar el juego, abre:

```text
http://localhost:8000
```

La primera carga puede ser más lenta porque el navegador descarga y guarda el entorno Python/WebAssembly.

## 6. Publicar gratis en GitHub Pages

1. Crea en GitHub un repositorio público, por ejemplo `atrapa-estrellas`.
2. En esta carpeta ejecuta:

```powershell
git init
git branch -M main
git add .
git commit -m "Crear primera versión del juego"
git remote add origin https://github.com/TU_USUARIO/atrapa-estrellas.git
git push -u origin main
```

3. En GitHub entra a `Settings` > `Pages`.
4. En `Build and deployment`, selecciona `GitHub Actions`.
5. Abre la pestaña `Actions` y espera a que termine la publicación.
6. El enlace normalmente tendrá esta forma:

```text
https://TU_USUARIO.github.io/atrapa-estrellas/
```

Cada nuevo `git push` volverá a publicar el juego automáticamente.

## 7. Estructura

```text
atrapa_estrellas_web/
├── .github/
│   └── workflows/
│       └── pages.yml
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Próximas mejoras recomendadas

- Pantalla de selección de personaje.
- Música y efectos de sonido.
- Monedas, niveles y tienda.
- Guardado del récord en el navegador.
- Imágenes propias para personajes y fondos.
- Botón de pantalla completa.
