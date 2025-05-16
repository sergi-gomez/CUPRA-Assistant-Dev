#CUPRA AI Assistant, entorno TEST, v2.6, No Publicado: 16/05/2025, funcionalidad Ofertas ESP + cuotas

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
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

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
footer {visibility: hidden;}

/* Forzar fondo blanco en toda la aplicación */
html, body, [data-testid="stAppViewContainer"],[data-testid="stApp"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Forzar texto negro en tablas */
table, thead th, tbody td {
    color: #000000 !important;
}

/* Eliminar padding, margen y ajustar border-radius en textarea y contenedores */
div[data-baseweb="textarea"], 
div[data-baseweb="base-input"], 
div[data-testid="stChatInputContainer"], 
div.st-emotion-cache-yd4u6l, 
textarea[data-testid="stChatInputTextArea"], 
.st-emotion-cache-1yk2xem {
    background-color: #ffffff !important;
    padding: 0px !important;  
    margin: 0px !important;  
    border-radius: 20px !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Asegurar fondo blanco en modo oscuro también */
@media (prefers-color-scheme: dark) {
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

     /* Forzar texto negro en tablas en modo oscuro */
    table, thead th, tbody td {
        color: #000000 !important;
    }

    /* Eliminar padding/margin y forzar border-radius en modo oscuro */
    .st-emotion-cache-x1bvup,
    .st-emotion-cache-hkjmcg {
        padding: 0px !important;
        margin: 0px !important;
        border-radius: 20px !important;
    }
}

/* Asegurar letras color negro dentro del chat */
p, h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
    margin: 0px; /* Margen específico para p */
}
ul {
    color: #000000 !important;
    margin: 5px; /* Margen específico para ul */
}
li {
    color: #000000 !important;
    margin: 5px; /* Margen específico para li */
}
div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] h1, div[data-testid="stChatMessage"] h2, div[data-testid="stChatMessage"] h3, div[data-testid="stChatMessage"] h4, div[data-testid="stChatMessage"] h5, div[data-testid="stChatMessage"] h6 {
    color: #000000 !important;
    margin: 0px; /* Margen específico para p dentro del chat */
}
div[data-testid="stChatMessage"] ul {
    color: #000000 !important;
    margin: 5px; /* Margen específico para ul dentro del chat */
}
div[data-testid="stChatMessage"] li {
    color: #000000 !important;
    margin: 5px; /* Margen específico para li dentro del chat */
}

/*Estilos para el título y calificación */
        .stCaption {
            color: #8B8B8B !important; 
            font-size: 14px !important; 
            font-weight: normal;
            line-height: 1.5;
            margin: 0;
            text-align: left; 
        }

/* Estilo específico para el mensaje de éxito */
        .custom-success {
            color: #329B93 !important; 
            font-weight: normal;
        }
    
div[data-testid="stBottomBlockContainer"] {
        bottom: 0;
        width: 100%;
        background-color: #ffffff !important;
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

/* Ajustar los estilos del campo de entrada */
textarea[aria-label="Enter your message"] {
    font-family: 'CupraScreen-Book', 'sans-serif' !important; 
    font-size: 12px !important; 
    color: #000000 !important; 
    background-color: #ffffff !important;
    caret-color: #8B8B8B !important; 
    border: none !important;
    padding: 5px 10px !important;
}

/* Estilos para el placeholder del campo de entrada */
textarea[aria-label="Enter your message"]::placeholder {
    color: #8B8B8B !important;
    background-color: #ffffff !important;
}

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

    # Añadir los mensajes sin el campo "role", agrupando a dos (user + assistant)
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
    return '<img src="https://www.cupraofficial.com/content/dam/public/cupra-website/piramide.svg" width="32" height="32" alt="icono" style="display:block;">'

# Genera la respuesta del asistente en tiempo real
def stream_generator(prompt, thread_id, assistant_id):
        
        # Resetea el tiempo activo de la interacción actual
        st.session_state["current_user_active"] = USER_ACTIVE_FIXED_TIME  # se suma una vez al enviar el mensaje
        update_user_active_time()  # Esto suma 5s a la variable global, pero también podrías registrar de forma separada

        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

        with st.spinner("Un momento.. generando la respuesta..."):
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
        st.session_state["current_assistant_active"] = interaction_assistant_time

        # Actualiza la variable global acumulada
        update_assistant_active_time(assistant_start_time)

        # Imprime el total de la interacción actual
        current_interaction_total = USER_ACTIVE_FIXED_TIME + interaction_assistant_time
        print(f"[LOG] Tiempo de interacción actual (Usuario + Asistente): {current_interaction_total:.2f} s")

# Asegura que cada hilo tenga su ID único
def ensure_single_thread_id():
        if "app1_thread_id" not in st.session_state:
            thread = client.beta.threads.create()
            st.session_state.app1_thread_id = thread.id
        return st.session_state.app1_thread_id

def extract_all_models_and_prices(url, base_url="https://www.cupraofficial.es/ofertas"):
    """Extrae modelos, descripciones, precios, tipo de precio y enlaces de la página de ofertas."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error al obtener datos de la página: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    offers = soup.find_all("section", class_="cmp-offer-cards-item")

    engine_type_map = {
        "gasolina": "Gasolina",
        "hibrido": "Híbrido (mHEV)",
        "hibrido-enchufable": "Híbrido enchufable (PHEV)",
        "electrico": "Eléctrico",
        # añade más si aparecen otros
    }

    models_and_prices = {}
    for offer in offers:
        # Extrae datos robustos de los atributos del section
        engine_type = offer.get("data-engine", "").strip().lower()
        engine_type_pretty = engine_type_map.get(engine_type, engine_type.capitalize())
        offer_engine = offer.get("data-offer-engine", "").strip()
        offer_type = offer.get("data-type", "").strip()
        offer_price = offer.get("data-offer-price", "").strip()

        # Extrae los datos visuales del HTML
        model_name_tag = offer.find("h2", class_="cmp-title__text")
        description_tag = offer.find("div", class_="cmp-text")
        price_number_tag = offer.find("span", class_="cmp-price__number")
        price_currency_tag = offer.find("span", class_="cmp-price__currency")
        price_suffix_tag = offer.find("span", class_="cmp-price__suffix")
        info_link_tag = offer.find("a", class_="cmp-button", title="Más información")

        # --- Lógica robusta para el precio ---
        if offer_price:
            price_clean = offer_price.replace(".", "").replace(",", ".")
        elif price_number_tag:
            price_raw = price_number_tag.text.strip().replace("\n", "")
            price_clean = re.sub(r"[^\d,]", "", price_raw).replace(",", ".")
        else:
            price_clean = ""

        price_currency = price_currency_tag.text.strip() if price_currency_tag else "€"
        price_suffix = price_suffix_tag.text.strip() if price_suffix_tag else ""
        info_link = info_link_tag["href"] if info_link_tag else "#"

        if not info_link.startswith("http"):
            info_link = base_url + info_link

        # Detectar si es cuota mensual o precio fijo
        price_type = "fijo"
        for campo in [price_currency.lower(), price_suffix.lower(), description_tag.text.lower() if description_tag else ""]:
            if "mes" in campo:
                price_type = "cuota"
                break

        if model_name_tag and description_tag:
            model_name = model_name_tag.text.strip()
            description = description_tag.text.strip()
            # DEBUG print
            print(f"[DEBUG] Modelo: {model_name} | engine_type: '{engine_type_pretty}' | offer_engine: '{offer_engine}' | offer_type: '{offer_type}' | price: '{price_clean}' | price_currency: '{price_currency}' | price_suffix: '{price_suffix}'")
            models_and_prices[model_name] = {
                'description': description,
                'price': price_clean,
                'price_type': price_type,
                'price_suffix': price_suffix,
                'price_currency': price_currency,
                'info_link': info_link,
                'engine_type': engine_type_pretty,
                'offer_engine': offer_engine,
                'offer_type': offer_type
            }

    return models_and_prices

def search_web(query, models_and_prices):
    """Busca modelos y precios relacionados con la consulta del usuario y diferencia cuota mensual y precio fijo."""
    query_normalized = unidecode(query.lower())

    # --- Filtrado por tipo de motor ---
    engine_types = {
        "gasolina": ["gasolina", "petrol"],
        "eléctrico": ["eléctrico", "electrico", "bev", "100% electrico", "100% eléctrico"],
        "híbrido": ["híbrido", "hibrido", "mhev"],
        "hibrido enchufable": ["phev", "híbrido enchufable", "hibrido enchufable"],
    }
    selected_engine_type = None
    for key, keywords in engine_types.items():
        if any(word in query_normalized for word in keywords):
            selected_engine_type = key
            break

    filtered_models_and_prices = models_and_prices
    if selected_engine_type:
        keywords = engine_types[selected_engine_type]
        filtered_models_and_prices = {
            model: data for model, data in models_and_prices.items()
            if any(
                kw in unidecode(data.get('engine_type', '').lower())
                for kw in keywords
            )
        }
        if not filtered_models_and_prices:
            return f"No se han encontrado ofertas para modelos con motor {selected_engine_type} en este momento."
    # --- FIN Filtrado por tipo de motor ---

    busca_cuota = any(word in query_normalized for word in ["cuota", "mes", "precio mensual"])
    busca_barato = any(word in query_normalized for word in ["barato", "más barato", "mas barato", "barata", "baratos", "baratas"])
    busca_caro = "caro" in query_normalized

    matched_models = []

    if busca_barato or busca_caro:
        # Separar modelos por tipo de precio
        models_with_prices_fijo = []
        models_with_prices_cuota = []
        for model, data in filtered_models_and_prices.items():
            try:
                price = float(data['price'].replace(',', '').replace('.', ''))  # Convertir precio a número
                if data['price_type'] == "fijo":
                    models_with_prices_fijo.append((model, price, data))
                elif data['price_type'] == "cuota":
                    models_with_prices_cuota.append((model, price, data))
            except ValueError:
                continue

        # Encontrar el modelo más barato/caro para cada tipo
        cheapest_fijo = min(models_with_prices_fijo, key=lambda x: x[1], default=None)
        cheapest_cuota = min(models_with_prices_cuota, key=lambda x: x[1], default=None)
        most_expensive_fijo = max(models_with_prices_fijo, key=lambda x: x[1], default=None)
        most_expensive_cuota = max(models_with_prices_cuota, key=lambda x: x[1], default=None)

        if busca_barato:
            formatted_data = (
                "Los precios pueden variar según la configuracion. "
                "Actualmente de las ofertas disponibles el modelo más barato es:\n\n"
                "Nota: Se muestran por separado el modelo más barato con precio fijo y el más barato con cuota mensual, si existen ambos.\n\n"
            )
            if cheapest_fijo:
                model, price, data = cheapest_fijo
                formatted_data += (
                    f"•{model} {data['description']}\n"
                    f"\t•Desde: {data['price']} {data.get('price_currency','')} {data['price_suffix']}\n"
                )
                if data.get('offer_type'):
                    formatted_data += f'\t•Tipo de financiación: [{data["offer_type"]}](https://www.cupraofficial.es/servicios-financieros)\n'
                formatted_data += f"\t•[Más información]({data['info_link']})\n\n"
            
            if cheapest_cuota:
                model, price, data = cheapest_cuota
                formatted_data += (
                    f"•{model} {data['description']}\n"
                    f"\t•Por: {data['price']} {data.get('price_currency','')} {data['price_suffix']}\n"
                )
                if data.get('offer_type'):
                    formatted_data += f'\t•Tipo de financiación: [{data["offer_type"]}](https://www.cupraofficial.es/servicios-financieros)\n'
                formatted_data += f"\t•[Más información]({data['info_link']})\n\n"
            if not cheapest_fijo and not cheapest_cuota:
                formatted_data += "No se encontraron modelos con precios disponibles.\n"
            return formatted_data

        elif busca_caro:
            formatted_data = (
                "Los precios pueden variar según la configuracion. "
                "Actualmente de las ofertas disponibles el modelo más caro es:\n\n"
                "Nota: Se muestran por separado el modelo más caro con precio fijo y el más caro con cuota mensual, si existen ambos.\n\n"
            )
            if most_expensive_fijo:
                model, price, data = most_expensive_fijo
                formatted_data += (
                    f"•{model} {data['description']}\n"
                    f"\t•Desde: {data['price']} {data.get('price_currency','')} {data['price_suffix']}\n"
                )
                if data.get('offer_type'):
                    formatted_data += f'\t•Tipo de financiación: [{data["offer_type"]}](https://www.cupraofficial.es/servicios-financieros)\n'
                formatted_data += f"\t•[Más información]({data['info_link']})\n\n"
            
            if most_expensive_cuota:
                model, price, data = most_expensive_cuota
                formatted_data += (
                    f"•{model} {data['description']}\n"
                    f"\t•Por: {data['price']} {data.get('price_currency','')} {data['price_suffix']}\n"
                )
                if data.get('offer_type'):
                    formatted_data += f'\t•Tipo de financiación: [{data["offer_type"]}](https://www.cupraofficial.es/servicios-financieros)\n'
                formatted_data += f"\t•[Más información]({data['info_link']})\n\n"
            if not most_expensive_fijo and not most_expensive_cuota:
                formatted_data += "No se encontraron modelos con precios disponibles.\n"
            return formatted_data

    # Lógica existente para buscar modelos relacionados con la consulta
    for model, data in filtered_models_and_prices.items():
        model_normalized = unidecode(model.lower())
        model_words = model_normalized.split()
        if any(word in query_normalized for word in model_words) or not any(word in query_normalized for word in model_words):
            if busca_cuota:
                if data['price_type'] == "cuota":
                    matched_models.append(model)
            else:
                matched_models.append(model)

    if matched_models:
        formatted_data = (
            "Los precios pueden variar según la configuración. Actualmente están disponibles las siguientes ofertas:\n\n"
        )
    else:
        formatted_data = (
            "No se han encontrado ofertas para el modelo solicitado en este momento.\n"
            "Puedes encontrar todas las ofertas disponibles [aqui](https://www.cupraofficial.es/ofertas). "
            "Si necesitas más información o deseas configurar un modelo específico, no dudes en preguntar."
        )
        return formatted_data

    for model in matched_models:
        data = filtered_models_and_prices[model]
        formatted_data += f"•{model} {data['description']}\n"
        if data['price_type'] == "cuota":
            formatted_data += f"\t• Por: {data['price']} {data.get('price_currency','')} {data['price_suffix']}\n"
        else:
            formatted_data += f"\t• Desde: {data['price']} {data['price_suffix']}\n"
        # Añadir tipo de financiación como enlace si existe
        if data.get('offer_type'):
            formatted_data += f'\t•Tipo de financiación: [{data["offer_type"]}](https://www.cupraofficial.es/servicios-financieros)\n'
        if data['price_type'] == "cuota" and data['price_suffix']:
            detalles = data['price_suffix'].split('|')
            for detalle in detalles:
                detalle = detalle.strip()
                if detalle:
                    formatted_data += f"\t• {detalle}\n"
        formatted_data += f"\t• [Más información]({data['info_link']})\n\n"

    formatted_data += (
        "Puedes encontrar todas las ofertas disponibles [aqui](https://www.cupraofficial.es/ofertas). "
        "Si necesitas más información o deseas configurar un modelo específico, no dudes en preguntar."
    )

    return formatted_data

def convert_links(text):
    # Casos tipo [https://url](https://url)
    same_url_pattern = r'\[(https?://[^\]]+)\]\(\1\)'
    text = re.sub(same_url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

    # Casos tipo [Texto](https://url)
    markdown_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    text = re.sub(markdown_pattern, r'<a href="\2" target="_blank">\1</a>', text)

    # URLs sueltas
    url_pattern = r'(?<!href=")(https?://[^\s<]+)'
    text = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

    return text

def app1():
    
    #Assistant ID de PROD
    #assistant_id = os.getenv('assistant_id')

    #Assistant ID de TEST
    assistant_id = os.getenv('assistant_id_test')

    # Extraemos los modelos y precios de la página web una vez
    url = "https://www.cupraofficial.es/ofertas"
    models_and_prices = extract_all_models_and_prices(url)
    
    if isinstance(models_and_prices, str):
        st.error(models_and_prices)  # Si hubo un error en la extracción
        return

    # Inicializamos las variables de tiempo activo, si aún no existen
    if "user_active_time" not in st.session_state:
        st.session_state["user_active_time"] = 0
    if "assistant_active_time" not in st.session_state:
        st.session_state["assistant_active_time"] = 0

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
                "content": "👋 ¡Hola! Soy el Asistente Virtual de CUPRA. ¿En qué puedo ayudarte hoy? Si tienes curiosidad por conocer nuestros últimos modelos, necesitas ayuda o simplemente quieres hacer una pregunta, ¡estoy aquí para ayudarte! No necesito ningún dato personal para ayudarte, así que por favor, no lo compartas."})

        st.session_state.app1_start_chat = False

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
                        <div style="background-color: #F0F0F0; padding: 12px; 
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
                        <div style="background-color: #D3D3D3; padding: 12px; 
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
                                        
    # Entrada del usuario
    prompt = st.chat_input("Enter your message", max_chars=100)

    if prompt:
        thread_id = ensure_single_thread_id()

        # Extraer el historial de mensajes recientes
        last_messages = [msg["content"] for msg in st.session_state.app1_messages[-2:]]  # Últimos 2 mensajes

        # Detectar si el usuario ha preguntado sobre precios anteriormente
        recent_price_query = any("precio" in msg.lower() or "Por precio:" in msg for msg in last_messages)

        # Detectar si la consulta es sobre precios o modelos (solo la pregunta actual)
        related_to_prices = any(word in prompt.lower() for word in ["precio", "coste", "cuesta", "cuota", "vale", "oferta", "barato", "caro"])

        if related_to_prices:
            car_data_text = search_web(prompt, models_and_prices)
        else:
            car_data_text = None

        # Construir el mensaje para el chatbot
        if car_data_text:
            user_prompt = (
                f"{prompt}\n\n"
                "IMPORTANTE: A continuación se proporciona información oficial sobre ofertas y modelos extraída del sitio web de CUPRA España. "
                "Debes indicar al inicio de todas las respuestas: Los precios pueden variar según la configuración. Actualmente las oferta disponibles es..."
                "Incluye *toda* esta información en tu respuesta sin omitir ni modificar nada:\n\n"
                f"{car_data_text}"
            )
        else:
            user_prompt = prompt  # Si no hay coincidencias, solo pasa el mensaje original
        
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
            cleaned_response = ""  
            icon_svg = get_icon_svg().strip() 

            for chunk in stream_generator(user_prompt, thread_id, assistant_id):
                response = chunk
                cleaned_response = clean_annotations(response)

                # Convertir las URLs en enlaces clicables
                cleaned_response_with_links = convert_links(cleaned_response)
                
                response_placeholder.markdown(f"""
                    <div style="max-width: 95%; margin-left: -10px; overflow-wrap: break-word; display: flex; 
                            align-items: flex-end; flex-direction: row; gap: 5px; margin-bottom: -10px;">
                        <div style="width: 32px; height: 32px; flex-shrink: 0;">{icon_svg}
                        </div>
                        <div style="background-color: #F0F0F0; padding: 12px; 
                                border-radius: 20px 20px 20px 0px; border: 0px solid #D1D1D1; 
                                flex-grow: 1;">
                            <p style='font-size:12px !important; color:#000000 !important; line-height:1.5; margin:0; text-align:left; white-space: normal;'>
                                {cleaned_response_with_links}

                """, unsafe_allow_html=True)
        
            response = cleaned_response_with_links

        # Añadir la respuesta al historial
        st.session_state.app1_messages.append({"role": "assistant", "content": response})

        # Guardar la conversación actual
        save_conversation_history(st.session_state.app1_messages)

        print(f"Assistant: {response}")
        print(f"Assistant (cleaned): {cleaned_response}")

    # Mostrar las estrellas después de la tercera iteración y si no se ha puntuado antes
    if (len(st.session_state.app1_messages) == 7) or ((len(st.session_state.app1_messages) == 9) and (not st.session_state.get("star_rating_given", False))):

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
                st.markdown("<p class='stCaption'> 🌟 ¿Te ha resultado útil mi ayuda? Valora tu experiencia.</p>", unsafe_allow_html=True)

                # Widget de calificación
                stars = st_star_rating("", maxValue =5, defaultValue =0, dark_theme=False, size=20, customCSS = "div {background-color: #ffffff !important;}", key="star_rating" )

                # Actualizar estado si el usuario califica
                if stars > 0:
                    st.markdown('<div class="custom-success">✅ ¡Gracias por tu feedback! Podemos seguir hablando si tienes más preguntas o inquietudes.</div>', unsafe_allow_html=True)

                    # Actualizar estado
                    if len(st.session_state.app1_messages) == 7:
                        st.session_state["star_rating_given"] = True

                    # Guarda el rating de forma persistente (y no se reinicia)
                    st.session_state["persistent_rating"] = stars  

                    thread_id = ensure_single_thread_id()

                    # Actualizar la última respuesta con el rating
                    if st.session_state.app1_messages and len(st.session_state.app1_messages) > 0:
                        st.session_state.app1_messages[-1]["rating"] = stars  

                    save_conversation_history(st.session_state.app1_messages)

def main():
   
    app1()

if __name__ == '__main__':
    main()