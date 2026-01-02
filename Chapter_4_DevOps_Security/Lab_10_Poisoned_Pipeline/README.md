# Lab 10: Poisoned Pipeline Attack - MLSecOps Security

## Descripción del Laboratorio

Este laboratorio demuestra un ataque crítico de **Poisoned Pipeline** mediante la explotación de deserialización insegura de Pickle en pipelines de machine learning. El ataque simula cómo un adversario puede comprometer un script de pre-procesamiento en GitHub Actions o cualquier pipeline CI/CD que procese modelos de ML.

## Objetivos de Aprendizaje

- Comprender los riesgos de usar `pickle.load()` en modelos de ML
- Identificar vulnerabilidades en pipelines de ML (MLSecOps)
- Implementar un PoC de ataque de deserialización
- Aprender técnicas de mitigación y mejores prácticas

## Arquitectura del Ataque

```
┌─────────────────────────────────────────────────────────┐
│  ATTACK VECTOR: Compromised CI/CD Pipeline             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  1. Attacker compromises GitHub repository             │
│  2. Replaces legitimate model.pkl with poisoned_model  │
│  3. Commits malicious file to trigger CI/CD           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  VULNERABLE CODE PATTERN:                              │
│                                                         │
│  with open('model.pkl', 'rb') as f:                    │
│      model = pickle.load(f)  # ⚠️ EXECUTES CODE        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  PAYLOAD EXECUTION:                                    │
│  - Reverse shell                                        │
│  - Data exfiltration                                    │
│  - Install backdoor packages                            │
│  - Modify system configuration                          │
└─────────────────────────────────────────────────────────┘
```

## Componentes del Laboratorio

### 1. `poison_poc.py`
Script principal que demuestra el ataque de deserialización Pickle.

**Características:**
- Crea un archivo Pickle malicioso que ejecuta código arbitrario
- Simula código vulnerable de pipeline
- Muestra alternativas seguras

**Uso:**
```bash
# Crear solo el archivo envenenado (sin ejecutar)
python3 poison_poc.py --create-only

# Demostración completa del ataque
python3 poison_poc.py
```

### 2. `PoC_Exploit.md`
Análisis técnico detallado del exploit y metodología de ataque.

## Requisitos

- Python 3.8+
- Entorno aislado (Docker recomendado)
- **ADVERTENCIA**: No ejecutar en sistemas de producción

## Ejecución del Laboratorio

### Paso 1: Preparar el entorno

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# El script no requiere dependencias externas
```

### Paso 2: Crear el archivo envenenado

```bash
python3 poison_poc.py --create-only
```

Esto creará `poisoned_model.pkl` sin ejecutar el código malicioso.

### Paso 3: Analizar el archivo

```bash
# Ver el contenido del archivo Pickle (sin deserializar)
strings poisoned_model.pkl | head -20
```

### Paso 4: Ejecutar la demostración (en entorno controlado)

```bash
python3 poison_poc.py
```

## Análisis Técnico

### ¿Por qué Pickle es peligroso?

Pickle permite la serialización de objetos Python arbitrarios, incluyendo funciones y clases. Durante la deserialización (`pickle.load()`), el método `__reduce__()` puede ser sobrescrito para ejecutar código arbitrario.

### Vector de Ataque

1. **Compromiso de repositorio**: El atacante compromete el repositorio Git o tiene acceso a modificar archivos
2. **Inyección de modelo envenenado**: Reemplaza un modelo legítimo con uno envenenado
3. **Trigger de pipeline**: El commit activa el pipeline CI/CD
4. **Ejecución automática**: El pipeline carga el modelo usando `pickle.load()`
5. **Ejecución de payload**: El código malicioso se ejecuta en el contexto del pipeline

### Ejemplo de Código Vulnerable

```python
# ⚠️ VULNERABLE - No usar en producción
def load_model(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)  # Ejecuta código arbitrario
    return model
```

## Mitigaciones

### 1. Usar SafeTensors (Recomendado)

```python
from safetensors import safe_open

def safe_load_model(model_path):
    with safe_open(model_path, framework="pt") as f:
        # SafeTensors solo carga datos, no código
        tensors = {}
        for key in f.keys():
            tensors[key] = f.get_tensor(key)
    return tensors
```

### 2. Validación de Checksums

```python
import hashlib

def verify_model_integrity(model_path, expected_hash):
    with open(model_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    if file_hash != expected_hash:
        raise ValueError("Model integrity check failed!")
```

### 3. Firmas Digitales (CoSign)

```bash
# Firmar modelo antes de commit
cosign sign-blob --key cosign.key model.pkl

# Verificar antes de cargar
cosign verify-blob --key cosign.pub --signature model.pkl.sig model.pkl
```

### 4. Análisis Estático (SAST)

```bash
# Usar Checkov para escanear infraestructura de IA
checkov -d . --framework dockerfile --framework kubernetes
```

### 5. Sandboxing

```python
# Cargar modelos en contenedores aislados
docker run --rm -v $(pwd):/models python:3.11 \
    python -c "import pickle; pickle.load(open('/models/model.pkl', 'rb'))"
```

## Impacto en Producción

- **Confidencialidad**: Exfiltración de datos y secretos
- **Integridad**: Modificación de modelos y datos
- **Disponibilidad**: Denegación de servicio mediante consumo de recursos
- **Autenticación**: Bypass mediante backdoors instalados

## Referencias

- [OWASP ML Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/)
- [NIST AI 100-2: Adversarial Machine Learning](https://csrc.nist.gov/publications/detail/nistir/8312/draft)
- [SafeTensors Documentation](https://huggingface.co/docs/safetensors/)
- [MLSecOps Principles](https://mlsecops.com/)

## Notas de Seguridad

⚠️ **ADVERTENCIA**: Este código es únicamente para fines educativos en entornos controlados. No ejecutar en sistemas de producción o con acceso a datos sensibles.

## Autor

Desarrollado como parte del curso **CAISP (Certified AI Security Professional)** - Lab 10, Sesión 10.

