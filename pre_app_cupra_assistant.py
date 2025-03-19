#CUPRA AI Assistant, entorno PRE, v2 

import streamlit as st 
import time
import re
import os
import uuid
from openai import AzureOpenAI
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos import exceptions
from streamlit_star_rating import st_star_rating

# Configuración de la página
st.set_page_config(
    page_title="CUPRA AI Assistant",
    layout="wide",

)

# CSS para ocultar la barra superior
hide_streamlit_style = """
<style>

@font-face {
            font-family: 'CupraScreen-Book';
            src:url('https://www.cupraofficial.com/etc.clientlibs/cupra-website/components/clientlibs/resources/fonts/otf/Cupra-Regular.otf') format("opentype");
            font-weight: normal; 
            font-style: normal;
        } 

* { 
    font-family: 'CupraScreen-Book', 'sans-serif' !important;
    font-size: 12px !important; 
} 

MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden}

/* Forzar fondo blanco en toda la aplicación */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Asegurar fondo blanco en modo oscuro también */
@media (prefers-color-scheme: dark) {
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
}

/* Asegurar letras color negro dentro del chat */
p, ul, li {
            color: #000000 !important;
        }
        div[data-testid="stChatMessage"] p, 
        div[data-testid="stChatMessage"] ul, 
        div[data-testid="stChatMessage"] li {
            color: #000000 !important;
        }

/*Estilos para el título y calificación */
        .stCaption {
            color: #8B8B8B !important; /* Cambia el color aquí */
            font-size: 14px !important; /* Forzar a 14px */
            font-weight: normal;
            line-height: 1.5;
            margin: 0;
            text-align: left; /* Centrar el texto horizontalmente */
        }

/* Estilo específico para el mensaje de éxito */
        .custom-success {
            color: #329B93 !important; 
            font-weight: normal;
        }
    
div[data-testid="stBottomBlockContainer"] {
        bottom: 0;
        width: 100%;
        background-color: #ffffff !important;  /* Asegura visibilidad */
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
}

 div.stChatMessage {
        background-color: #ffffff !important;
    }

/* Ocultar los iconos predeterminados */
.stChatMessage > div:first-child {
    display: none;
}

/* Asegurar que el contenedor del textarea tenga fondo blanco */
div[data-baseweb="textarea"], div[data-baseweb="base-input"] {
    background-color: #ffffff !important; /* Fuerza el fondo blanco */
    padding: 0 !important; /* Elimina el padding */
    margin: 0 !important; /* Elimina cualquier margen */
    
div[data-baseweb="textarea"], 
div[data-baseweb="base-input"], 
div[data-testid="stChatInputContainer"], 
div.st-emotion-cache-yd4u6l {
    border-radius: 20px !important;       
    box-shadow: none !important;         
    padding: 0 !important;               
    margin: 0 !important;                 
    background-color: #ffffff !important;
    outline: none !important; /
}

div.st-emotion-cache-yd4u6l > div {
    padding: 0 !important;
    margin: 0 !important;
    background-color: #ffffff !important;
}

/* Estilos para el campo de entrada del chat */
textarea[aria-label="Enter your message"] {
    font-family: 'CupraScreen-Book', 'sans-serif' !important; /* Cambia la fuente */
    font-size: 12px !important; 
    color: #000000 !important; /* Cambia el color de la letra negra */
    background-color: #ffffff !important;
    caret-color: #8B8B8B !important; /* Cambia el color del cursor a gris claro */ 
    border: none !important; /* Elimina bordes innecesarios */
    padding: 5px 10px !important; /* Ajusta padding si es necesario */
}

/* Estilos para el placeholder del campo de entrada */
textarea[aria-label="Enter your message"]::placeholder {
    color: #8B8B8B !important; /* Cambia el color del placeholder a gris claro */
    background-color: #ffffff !important;

</style>

"""

# Cargar el estilo CSS en Streamlit
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Obtener la API Keys desde la variables de entorno
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_version = os.getenv("API_VERSION")

if not api_key:
    raise ValueError("API Key no configurada en las variables de entorno")

# Inicialización del cliente Azure OpenAI
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version
)

# Inicialización del cliente Cosmos DB
CONNECTION_STRING = 'AccountEndpoint=https://cosno-sea-vx3-cupravirtualassist-test.documents.azure.com:443/;AccountKey=Cuc1in30WjRhHHcRYGtrQ2GZqzp5Sg1s94MZhaoARFKtZsvmcH0vOVVq6M6Yb5TOE2hsR2LFPeEPACDbL9eUOA==;' 
DATABASE_NAME = os.getenv('COSMOS_DB_DATABASE_NAME')
CONTAINER_NAME = os.getenv('COSMOS_DB_CONTAINER_NAME')

# Conexión a Cosmos DB
cosmos_client = CosmosClient.from_connection_string(CONNECTION_STRING)
database = cosmos_client.create_database_if_not_exists(id=DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)

# Función para eliminar anotaciones del texto
def clean_annotations(text):
    return re.sub(r'【.*?†source】', '', text)

# Función para inicializar el thread_id en la sesión
def ensure_single_thread_id():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    return st.session_state.thread_id

# Función para limpiar texto y asegurarse de que esté en UTF-8
def clean_text(text):
    try:
         # Convertimos cualquier carácter que no sea compatible con UTF-8
        return text.encode('utf-8').decode('utf-8') # Simplemente nos aseguramos que esté en UTF-8
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text # Si hay un error de codificación/decodificación, devolvemos el texto tal cual

# Tiempo fijo a sumar por cada mensaje enviado por el usuario (en segundos)
USER_ACTIVE_FIXED_TIME = 5

def update_user_active_time():
    """
    Cada vez que el usuario envía un mensaje, se suma un tiempo fijo.
    """
    st.session_state["user_active_time"] = st.session_state.get("user_active_time", 0) + USER_ACTIVE_FIXED_TIME
    print(f"[LOG] Usuario: se sumaron {USER_ACTIVE_FIXED_TIME} segundos de tiempo activo.")


def update_assistant_active_time(assistant_start_time):
    """
    Se debe llamar cuando el asistente finaliza su respuesta.
    Calcula el tiempo transcurrido desde assistant_start_time hasta ahora y lo acumula.
    """
    end_time = time.time()
    assistant_active = end_time - assistant_start_time
    st.session_state["assistant_active_time"] = st.session_state.get("assistant_active_time", 0) + assistant_active
    print(f"[LOG] Asistente: activo sumado = {assistant_active:.2f} s")


def get_total_active_time():
    """
    Retorna la suma del tiempo activo del usuario y del asistente (solo de la interacción actual), en segundos.
    """
    user_time = st.session_state.get("user_active_time", 0)
    assistant_time = st.session_state.get("assistant_active_time", 0)
    total = user_time + assistant_time
    return total

def get_existing_duration(thread_id):
    try:
        item = container.read_item(item=thread_id, partition_key=thread_id)
        return item.get("duration_seconds", 0)
    except exceptions.CosmosResourceNotFoundError:
        return 0

def save_conversation_in_cosmos(thread_id, conversation, rating, current_interaction_time):
    """
    Suma el tiempo de la interacción actual a la duración previa (almacenada en Cosmos) y lo guarda.
    Se utiliza el rating persistente (si ya fue asignado) para que no se reinicie.
    """
    previous_duration = get_existing_duration(thread_id)
    new_total = previous_duration + current_interaction_time

    print(f"[LOG] Duración anterior iteracion (acumulado): {previous_duration:.2f} segundos")
    print(f"[LOG] Duración total del thread: {new_total:.2f} segundos")

    # Prioriza el rating persistente, si existe
    final_rating = st.session_state.get("persistent_rating", rating)

    conversation_data = {
        'id': thread_id,
        'conversation': conversation,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rating':  final_rating,  # Se añade el rating persistente (si existe)
        'duration_seconds': round(new_total, 2)  # Tiempo total acumulado para este thread
    }
    try:
        container.upsert_item(body=conversation_data)
        print("Conversación guardada exitosamente en Cosmos DB.")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error al guardar la conversación en Cosmos DB: {e.message}")


# Función para guardar el historial de conversaciones solo en Cosmos DB
def save_conversation_history(all_messages, rating=None):
   
    # Generar un nuevo thread_id único para cada hilo de conversación
    thread_id = ensure_single_thread_id()

    # Crear la entrada para el hilo de conversación con el thread_id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

     # Si ya se ha guardado un rating de forma persistente, se usa ese valor.
    if "persistent_rating" in st.session_state:
        rating = st.session_state["persistent_rating"]
    else:
        # Si aún no se ha puntado, se lee el rating temporal
        rating = st.session_state.get("star_rating", None) if "star_rating_given" in st.session_state else None

    
        
    #Obtenemos el tiempo de la interacción actual (usuario + asistente)
    current_interaction_time = get_total_active_time()

    thread_entry = {
        "thread_id": thread_id,
        "timestamp": timestamp,
        "rating": rating,  
        "messages": []
}

    # Añadir los mensajes sin el campo "role", agrupando de a dos (user + assistant)
    user_message = None
    
    for idx, msg in enumerate(all_messages):
        if msg["role"] == "user":
            user_message = clean_text(msg["content"])
        elif msg["role"] == "assistant" and user_message:
            assistant_message = clean_text(msg["content"])

            thread_entry["messages"].append({
                "User": user_message,
                "Assistant": assistant_message,
            })
            user_message = None

    # Suma el tiempo actual a la duración previa y guarda en Cosmos DB
    save_conversation_in_cosmos(thread_id, thread_entry["messages"], rating, current_interaction_time)
    
    # Reinicia los contadores para la próxima interacción
    st.session_state["user_active_time"] = 0
    st.session_state["assistant_active_time"] = 0

def get_icon_svg():
    return """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <mask id="mask0_2212_1797" style="mask-type:alpha" maskUnits="userSpaceOnUse" x="4" y="4" width="24" height="23">
    <rect x="4" y="4" width="24" height="23" fill="#D9D9D9"/>
    </mask>
    <g mask="url(#mask0_2212_1797)">
    <rect x="-5" y="-4" width="42" height="38.5219" fill="url(#pattern0_2212_1797)"/>
    </g>
    <defs>
    <pattern id="pattern0_2212_1797" patternContentUnits="objectBoundingBox" width="1" height="1">
    <use xlink:href="#image0_2212_1797" transform="scale(0.00078125 0.000851789)"/>
    </pattern>
<image id="image0_2212_1797" width="1280" height="1174" preserveAspectRatio="none" xlink:href="data:image/png;base64,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"/>
</defs>
</svg>"""

def app1():
    
    assistant_id = "asst_jQQLtHX9AxVVCNLuFYRJEJq7"  
  
    # Inicializamos las variables de tiempo activo, si aún no existen
    if "user_active_time" not in st.session_state:
        st.session_state["user_active_time"] = 0
    if "assistant_active_time" not in st.session_state:
        st.session_state["assistant_active_time"] = 0

    # Asegura que cada hilo tenga su ID único
    def ensure_single_thread_id_app1():
        if "app1_thread_id" not in st.session_state:
            thread = client.beta.threads.create()
            st.session_state.app1_thread_id = thread.id
        return st.session_state.app1_thread_id

    
    # Genera la respuesta del asistente en tiempo real
    def stream_generator(prompt, thread_id):
        
        # Resetea el tiempo activo de la interacción actual
        st.session_state["current_user_active"] = USER_ACTIVE_FIXED_TIME  # se suma una vez al enviar el mensaje
        update_user_active_time()  # Esto suma 5s a la variable global, pero también podrías registrar de forma separada

        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

        with st.spinner("Wait..Generating response..."):
            stream = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                stream=True
            )

        response_text = ""
        interaction_assistant_time = 0
        assistant_start_time = time.time()  # Inicio de la respuesta del asistente
        for event in stream:
            if event.data.object == "thread.message.delta":
                for content in event.data.delta.content:
                    if content.type == 'text':
                        response_text += content.text.value
                        yield response_text
                        time.sleep(0.02)
        
        # Mide el tiempo de respuesta del asistente
        interaction_assistant_time = time.time() - assistant_start_time
        # Si quisieras registrar este valor por separado:
        st.session_state["current_assistant_active"] = interaction_assistant_time

        # Actualiza la variable global acumulada
        update_assistant_active_time(assistant_start_time)

        # Imprime el total de la interacción actual
        current_interaction_total = USER_ACTIVE_FIXED_TIME + interaction_assistant_time
        print(f"[LOG] Tiempo de interacción actual (Usuario + Asistente): {current_interaction_total:.2f} s")

        # Inicializa el historial del chat
    if 'app1_start_chat' not in st.session_state:
        st.session_state.app1_start_chat = True

    if st.session_state.app1_start_chat:
        if "app1_messages" not in st.session_state:
            st.session_state.app1_messages = []

        # Obtener el timestamp actual
        current_time = datetime.now().strftime("%Y-%m-%d")

        st.markdown(
            f"<p style='font-size:12px; color:#000000; margin:0; text-align:left;'>{current_time}</p>",
            unsafe_allow_html=True,
            )

        # Mostrar el mensaje de bienvenida solo una vez y asegurarse de que permanezca
        if len(st.session_state.app1_messages) == 0:  # Solo si el historial está vacío
            st.session_state.app1_messages.append({
                "role": "assistant", 
                "content": "👋 Hello! I´m CUPRA AI Assistant, your virtual assistant. How can I help you today? If you're curious about our latest models, need assistance, or just have a question, I'm here to help! For my use, I don't need any personal information, so please don't share it."
            })

        st.session_state.app1_start_chat = False
    show_star_rating = False  # Para habilitar el star rating a partir de la tercera iteración

    # Muestra el historial del chat (sin incluir la respuesta actual)
    for idx, message in enumerate(st.session_state.app1_messages):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Mostrar la respuesta con el mismo formato que la primera vez
                icon_svg = get_icon_svg().strip()  # Asegurar que el SVG se usa directamente
                st.markdown(f"""
                    <div style="max-width: 95%; margin-left: -10px; overflow-wrap: break-word; display: flex; 
                            align-items: flex-end; flex-direction: row; gap: 5px; margin-bottom: -20px;">
                        <div style="width: 32px; height: 32px; flex-shrink: 0;">{icon_svg}</div>
                        <div style="background-color: #F0F0F0; padding: 10px; 
                                border-radius: 20px 20px 20px 0px; border:0px solid #D1D1D1; 
                                flex-grow: 1;">
                            <p style="font-size:12px; color:#000000; background-color:#F0F0F0; 
                                line-height:1.5; margin:0; text-align:left; border-radius:5px; 
                                padding:0px; white-space:normal;word-wrap: break-word;">
                                    {clean_annotations(message['content'])}
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                   
            else:
                # Mensaje del usuario (A la derecha)
                st.markdown(f"""
                    <div style="max-width: 75%; margin-left: auto; overflow-wrap: break-word; display: flex; 
                            align-items: flex-end; flex-direction: row-reverse; gap: 5px; margin-bottom: -20px;">
                        <div style="background-color: #D3D3D3; padding: 10px; 
                                border-radius: 20px 20px 0px 20px; border: 0px solid #A4C8F0; 
                                flex-grow: 1;">
                            <p style="font-size:12px; color:#000000; background-color:#D3D3D3; 
                                line-height:1.5; margin:0; text-align:left; border-radius:5px; 
                                padding:0px; white-space:normal; word-wrap: break-word;">
                                    {clean_annotations(message['content'])}
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                                        
        if idx == 3 and "star_rating_given" not in st.session_state:
            show_star_rating = True

    # Entrada del usuario
    prompt = st.chat_input("Enter your message", max_chars=100)

    if prompt:
        thread_id = ensure_single_thread_id_app1()

        # Mostrar el mensaje del usuario
        with st.chat_message("user"):
            st.markdown(f"""
                <div style="max-width: 75%; margin-left: auto; overflow-wrap: break-word; display: flex; 
                        align-items: flex-end; flex-direction: row-reverse; gap: 5px; margin-bottom: -20px;">
                    <div style="background-color: #D3D3D3; padding: 10px; 
                            border-radius: 20px 20px 0px 20px; border: 0px solid #A4C8F0; 
                            flex-grow: 1;">
                        <p style="font-size:12px; color: #000000; background-color: #D3D3D3; 
                        line-height:1.5; margin:0; text-align:left; border-radius:5px; 
                        padding:0px; white-space:normal; word-wrap: break-word;">
                            {prompt}
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.session_state.app1_messages.append({"role": "user", "content": prompt})
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response = ""
            cleaned_response = ""  # Inicializa la variable para evitar errores
            icon_svg = get_icon_svg().strip()  # Asegurar que el SVG se usa directamente

            for chunk in stream_generator(prompt, thread_id):
                response = chunk
                cleaned_response = clean_annotations(response)
                
                response_placeholder.markdown(f"""
                    <div style="max-width: 95%; margin-left: -10px; overflow-wrap: break-word; display: flex; 
                            align-items: flex-end; flex-direction: row; gap: 5px; margin-bottom: -10px;">
                        <div style="width: 32px; height: 32px; flex-shrink: 0;">{icon_svg}</div>
                        <div style="background-color: #F0F0F0; padding: 10px; 
                                border-radius: 20px 20px 20px 0px; border: 0px solid #D1D1D1; 
                                flex-grow: 1;">
                            <p style='font-size:12px !important; color:#000000 !important; line-height:1.5; margin:0; text-align:left; white-space: normal;'>
                                {cleaned_response}
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
            response = cleaned_response  # Asegurar que la variable response sea consistente

        # Añadir la respuesta al historial
        st.session_state.app1_messages.append({"role": "assistant", "content": response})

        # Guardar la conversación actual
        save_conversation_history(st.session_state.app1_messages)

        print(f"Assistant: {response}")
        print(f"Assistant (cleaned): {cleaned_response}")

    # Mostrar las estrellas después de la tercera iteración y si no se ha puntuado antes
    if show_star_rating and not st.session_state.get("star_rating_shown", False):
        # Contenedor compacto
        with st.container():
            # Estilo CSS personalizado para ajustar el espaciado
            st.markdown(
                """
                <style>
                iframe.stCustomComponentV1 {
                    margin: 0 !important; /* Elimina márgenes */
                    padding: 0 !important; /* Elimina paddings */
                    height: 26px !important; /* Ajusta la altura para que sea precisa */
                    display: block !important; /* Asegura que el iframe se renderice correctamente */
                }
                .compact-success {
                    margin-top: -10px; /* Ajusta el espacio entre el iframe y el mensaje */
                }
                </style>
                """,
                unsafe_allow_html=True,
                )

            with st.container():
                st.markdown("<p class='stCaption'> 🌟Is the CUPRA AI Assistant helping you? Please rate your experience</p>", unsafe_allow_html=True)

                # Widget de calificación
                stars = st_star_rating("", maxValue =5, defaultValue =0, dark_theme=False, size=20, customCSS = "div {background-color: #ffffff !important;}", key="star_rating" )

                # Actualizar estado si el usuario califica
                if stars > 0:
                    st.markdown('<div class="custom-success">✅ Thank you for your feedback! We can continue talking if you have any further questions or concerns.</div>', unsafe_allow_html=True)

                    # Actualizar estado
                    st.session_state["star_rating_given"] = True
                    # Guarda el rating de forma persistente (y no se reinicia)
                    st.session_state["persistent_rating"] = stars  
                    st.session_state["star_rating_shown"] = True
                    thread_id = ensure_single_thread_id_app1()

                    # Actualizar la última respuesta con el rating
                    if st.session_state.app1_messages and len(st.session_state.app1_messages) > 0:
                        st.session_state.app1_messages[-1]["rating"] = stars  # Añadir rating a la última respuesta

                    save_conversation_history(st.session_state.app1_messages)

                # Incrementar el contador de tiempo
                if "star_rating_timer" not in st.session_state:
                    st.session_state["star_rating_timer"] = 0
                st.session_state["star_rating_timer"] += 1

    # Ocultar las estrellas si el contador alcanza el límite
    if "star_rating_timer" in st.session_state and not st.session_state.get("star_rating_shown", False):  
        if st.session_state["star_rating_timer"] > 1:  # Ejemplo: después de 2 iteraciones
            st.session_state["star_rating_shown"] = True  # Ocultar el widget
            del st.session_state["star_rating_timer"]  # Limpiar el contador

def main():
   
    app1()

if __name__ == '__main__':
    main()