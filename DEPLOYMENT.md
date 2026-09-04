# Guía de Despliegue en Railway.app

## 📋 Requisitos previos
- Cuenta en GitHub (gratuita)
- Cuenta en Railway.app (gratuita)

## 🚀 Paso 1: Subir a GitHub

### 1.1 Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre del repositorio: `agenda-personal`
3. Descripción: "Agenda personal para gestión de evidencias"
4. Marca "Public" o "Private" (como prefieras)
5. No agregues README, .gitignore o licencia (ya los tenemos)
6. Haz clic en "Create repository"

### 1.2 Subir tu código
Abre una terminal en el directorio `evidence_manager` y ejecuta:

```bash
git init
git add .
git commit -m "Initial commit - Agenda Personal"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/agenda-personal.git
git push -u origin main
```

**Importante:** Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

## 🚀 Paso 2: Desplegar en Railway.app

### 2.1 Crear cuenta en Railway
1. Ve a https://railway.app/
2. Haz clic en "Start New Project"
3. Selecciona "Login with GitHub"
4. Autoriza Railway para acceder a tu cuenta de GitHub

### 2.2 Conectar tu repositorio
1. En Railway, haz clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona tu repositorio `agenda-personal`
4. Railway detectará automáticamente que es una app Python/Flask

### 2.3 Configurar el despliegue
Railway detectará automáticamente:
- **Framework:** Flask
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py web`

### 2.4 Variables de entorno (si es necesario)
Si necesitas configurar variables de entorno:
1. Ve a la pestaña "Variables" en tu proyecto Railway
2. Agrega las variables que necesites

## 🎉 Paso 3: ¡Listo!

Railway construirá y desplegará tu aplicación automáticamente. En unos minutos tendrás:

- **URL pública:** `https://tu-proyecto.railway.app`
- **SSL/HTTPS:** Automático y gratuito
- **Disponibilidad 24/7:** Funciona siempre
- **Base de datos:** SQLite local (para producción considerar upgrade)

## 📱 Paso 4: Usar tu aplicación

1. Copia la URL que te da Railway
2. Úsala en tu móvil desde cualquier lugar
3. Funciona aunque tu PC esté apagada

## 🔧 Paso 5: Actualizaciones futuras

Cuando quieras hacer cambios:

```bash
git add .
git commit -m "Descripción de cambios"
git push
```

Railway detectará los cambios y redeployará automáticamente.

## 💡 Notas importantes

- **Plan gratuito:** Railway ofrece $5/mes en créditos gratuitos
- **Base de datos:** Actualmente usa SQLite local. Para producción considerar PostgreSQL
- **Dominio personal:** Puedes conectar tu propio dominio si lo deseas
- **Monitoreo:** Railway ofrece métricas y logs básicos gratis

## ⚠️ Limitaciones del plan gratuito

- **Sleep mode:** La app se "duerme" después de 30 minutos de inactividad
- **Cold starts:** Primeras cargas pueden tomar 10-30 segundos al "despertar"
- **Recursos:** Limitados pero suficientes para uso personal

## 🚀 Solución para 24/7 real

Si necesitas que nunca se duerma:
- Considera upgrade al plan Hobby ($5/mes)
- O usa servicios como Render.com (similar, también tiene sleep mode en plan gratuito)

## 📞 Soporte

Si tienes problemas:
- Revisa los logs en Railway
- Verifica que el Procfile esté correcto
- Asegúrate de que requirements.txt tenga las dependencias correctas