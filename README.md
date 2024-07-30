# RealTimeSpeechTranslate
Grabar audio en tiempo real, transcribirlo usando la API de Deepgram y traducirlo al español usando la API de Groq. La transcripción y la traducción se muestran en una interfaz gráfica.

## Requisitos

1. Python 3.x
2. Instalar las dependencias listadas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Instalar VOICEMEETER para la captura de audio en Windows:
- [Descargar VOICEMEETER](https://vb-audio.com/Voicemeeter/)

## Configuración
Crear un archivo .env en el mismo directorio que el código con las siguientes claves API:
```
DEEPGRAM_API_KEY=tu_deepgram_api_key
GROQ_API_KEY=tu_groq_api_key

```
si no tienes key
- [Registrarse en Deepgram](https://console.deepgram.com/signup)
- [Registrarse en Groq](https://platform.groq.com/signup)

## Ejecución
Para ejecutar la aplicación, simplemente corre el script principal:

```
python sub.py
```
La interfaz gráfica te permitirá iniciar y detener la grabación. Las transcripciones y traducciones aparecerán en la ventana principal.

## Notas
Asegúrate de configurar correctamente los dispositivos de entrada de audio para que VOICEMEETER capture el audio del sistema.
Si tienes problemas con la captura de audio, verifica que VOICEMEETER esté configurado correctamente y que el dispositivo de entrada esté seleccionado adecuadamente en el código.


## Desarrolladores

| [<img src="https://avatars.githubusercontent.com/u/163685041?v=4" width=115><br><sub>Michael Martinez</sub>](https://github.com/bkmay1417) |
| :---: |

Copyright (c) 2024 [Michael Martinez] yam8991@gmail.com
