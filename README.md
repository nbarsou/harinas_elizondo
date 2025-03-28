# README

---

## **Instalación y Configuración Inicial**

### **Clonar el Repositorio**

Para empezar, clona el repositorio en tu máquina local:

```bash
git clone https://github.com/nbarsou/harinas_elizondo.git
cd harinas_elizondo
```

### **Crear un Entorno Virtual (`venv`)**

Se recomienda trabajar en un **entorno virtual** para evitar conflictos de dependencias:

#### **Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

#### **Mac / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### **Instalar las Dependencias**

Una vez activado el entorno virtual, instala los paquetes necesarios:

```bash
pip install -r requirements.txt
```

---

## **2️⃣ Uso de Git y Estrategia de Ramas**

### **Estrategia de Ramas**

- La rama principal es **`main`** (código estable y revisado).
- Cada desarrollador trabajará en **su propia rama** basada en `main`.
  - Ejemplo: `feature/nombre-servicio` (`feature/user-service`, `feature/client-api`)
- **Todos los cambios deben pasar por una Pull Request (PR) antes de fusionarse en `main`**.

### **Flujo de Trabajo**

#### **Actualizar el Código Local**

Siempre antes de empezar a trabajar, asegúrate de que tienes la última versión del código:

```bash
git checkout main  # Cambia a la rama main
git pull origin main  # Descarga la última versión del código
```

#### **Crear y Cambiar a una Nueva Rama**

```bash
git checkout -b feature/nombre-de-tu-rama
git push -u origin feature/nombre-de-tu-rama
```

#### **Hacer Cambios y Confirmarlos**

Después de hacer cambios en tu código:

```bash
git add .
git commit -m "Descripción del cambio realizado"
git push origin feature/nombre-de-tu-rama
```

#### **Subir Cambios y Crear una Pull Request**

1. Sube tu código con `git push origin feature/nombre-de-tu-rama`
2. En **GitHub**, ve a la sección de Pull Requests y crea una **nueva PR** hacia `main`.
3. Un compañero revisará y aprobará la PR antes de hacer **merge**.

#### **Fusionar la Rama (Después de la Aprobación)**

Después de que la PR sea revisada y aprobada:

```bash
git checkout main
git pull origin main
git merge feature/nombre-de-tu-rama
git push origin main
```

#### **Eliminar la Rama (Opcional)**

Una vez que los cambios están en `main`, puedes borrar la rama:

```bash
git branch -d feature/nombre-de-tu-rama
git push origin --delete feature/nombre-de-tu-rama
```

---

## **3️⃣ Ejecutar Pruebas Unitarias**

Este proyecto usa `pytest` para ejecutar pruebas. Todas las pruebas están en la carpeta `tests/`.

### **Ejecutar Todas las Pruebas**

```bash
pytest
```

### **Ejecutar una Prueba Individual**

Si solo deseas ejecutar un archivo específico de pruebas:

```bash
pytest tests/test_nombre_archivo.py
```

Ejemplo:

```bash
pytest tests/test_client.py
```

---

## **4️⃣ Ejecutar la Aplicación**

Para ejecutar la aplicación Flask, usa:

```bash
python main.py
```

Luego, accede a la aplicación en tu navegador en:

```
http://127.0.0.1:5000/
```

Rutas disponibles:

- `/signin` → Inicio de sesión
- `/dashboard` → Panel principal
- `/inspection` → Inspecciones
- `/certification` → Certificación
- `/equipment` → Equipos
- `/clients` → Clientes
- `/users` → Usuarios

---

## **6️⃣ Buenas Prácticas**

✔ **Nunca hagas `push` directo a `main`**. Usa Pull Requests.  
✔ **Siempre trabaja en una rama separada para cada tarea**.  
✔ **Mantén tu código actualizado con `git pull origin main` antes de hacer cambios**.  
✔ **Asegúrate de que las pruebas pasan antes de enviar una Pull Request**.
