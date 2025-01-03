from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import re
import requests
from mainApp.models import *
import pandas as pd
import geocoder
import json
from Crypto.Hash import MD5
from datetime import datetime, timedelta
import hashlib
from django.conf import settings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jwt
from django.http import HttpResponse
        


class FallBack(LogicAdapter):
    def __init__(self,chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def can_process(self, statement):
        words = ['codigoamarillo', '350', 'cntas espejo']
        return any(word in statement.text.lower() for word in words)

    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        arr = np.array(['Solicitud de cuentas espejo', 'Revisar Equipos', 'Informacion acerca de mi cuenta'])
        selected_options = np.random.choice(arr, size=3, replace=False)  
        
        response = f"""
            Lo lamento, no pude entender tu solicitud, ¿alguno de estas opciones va más de acuerdo a lo que necesitas?
            <br>
            <div class="Structure">
                <button class="select-adapter" data-value="{selected_options[0]}">{selected_options[0]}</button>
                <br>
                <button class="select-adapter" data-value="{selected_options[1]}">{selected_options[1]}</button>
                <br>
                <button class="select-adapter" data-value="{selected_options[2]}">{selected_options[2]}</button>
            </div>
        """
        response_statement = Statement(text=response)
        response_statement.confidence = 1
        return response_statement
class InformacionUsuario(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.keywords = np.array(['Informacion de mi usuario', 'Info usuario', 'Informacion usuario'])

    def set_request(self, request):
        self.request = request

    def can_process(self, statement):
        input_text = statement.text.lower()
        return self._calculate_similarity(input_text) > 0.6
    
    def _calculate_similarity(self, input_text):
        vectorizer = TfidfVectorizer()
        transform = vectorizer.fit_transform(self.keywords)
        vectors = vectorizer.transform([input_text])
        cosine_similarities = cosine_similarity(vectors, transform).flatten()
        return max(cosine_similarities)
    

    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'user_id': user.id,
                'nombre': user.first_name,
                'correo': user.email,
                'contraseña':  user.password,

            }
            response_text = f"Eres \nNombre: {context['nombre']}, Correo: {context['correo']}"
        else:
            response_text = "No has iniciado sesión."

        response_statement = Statement(text=response_text)
        response_statement.confidence = 1
        return response_statement
    
class CuentaEspejo(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.keywords = np.array(['Realizar cuenta espejo', 'Solicitud de cuentas espejo'])
        
    def set_request(self, request):
        self.request = request

    def can_process(self, statement):
        input_text = statement.text.lower()
        return self._calculate_similarity(input_text) > 0.6
    
    def _calculate_similarity(self, input_text):
        vectorizer = TfidfVectorizer()
        transform = vectorizer.fit_transform(self.keywords)
        vectors = vectorizer.transform([input_text])
        cosine_similarities = cosine_similarity(vectors, transform).flatten()
        return max(cosine_similarities)
    
    
    def process(self, input_statement, additional_response_selection_parameters = None,  **kwargs):
        root_url = "https://atlantida2.mx"
        forced_string = "/index.php?su="
        user = self.request.user
        get_user_objects = settings.GET_USER_OBJECTS
        get_user_objects += user.username
        object_response = requests.get(get_user_objects)
        object_response.raise_for_status()
        object_data_api = object_response.json()
        print(object_data_api)
        if isinstance(object_data_api, list) and len(object_data_api) > 0:
            index_object = next((i for i, item in enumerate(object_data_api)
                        if item.get('username') == user.username and 
                           item.get('email') ==  user.email))
        else:
            html_Conj = "No se encontraron datos de tu cuenta"
            response_statement = Statement(text = html_Conj)
            response_statement.confidence = 1
            return response_statement
            
        if index_object != 1:
            objects_user = object_data_api[index_object]
            nameFromImei = [obj.get('name') for obj in objects_user.get('objects', [])]
            Imei = [obj.get('imei') for obj in objects_user.get('objects', [])]
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        to_hash = f'{user.email}{current_time}'
        hashed = hashlib.md5()
        hashed.update(to_hash.encode('utf-8'))  
        transformed_hash = hashed.hexdigest().upper()
        Agglomerated_string = root_url +  forced_string + transformed_hash
        html_Conj = "Para poder entregar un acceso a tu cuenta espejo, por favor llena el siguiente formulario \n"
        html_Conj += "<form id='mirrorAccountForm'>"
        table_html = '<div class="tableContainer">'
        table_html += '<div style="position: relative;"><input id="SearchTable" type="text" onkeyup="Searcher()"><i class="medium material-icons" id="SearchIcon">search</i></div>'
        table_html += '<table class="sortable" id="TableForMA">'
        table_html += '<thead><tr><th id="add_sr">Añadir</th><th>Nombre</th><th>IMEI</th></tr></thead>'
        table_html += '<tbody id="TableCreateMA">'
        
        for index, (name, imei) in enumerate(zip(nameFromImei, Imei)):
            
            table_html += '<tr>'
            table_html += f'<td><input type="checkbox" name="Imei" class="check" value="{imei}"></td>'
            table_html += f'<td class="middleTd">{name}<p value="{name}"></td>'
            table_html += f'<td>{imei}<p value="{imei}"></td>'
            table_html += '</tr>'
            
        table_html += '</tbody></table><div id="pagination"></div></div>'
        
        
        html_Conj += table_html
            
        html_Conj += f'''
            <br>
            <label for="expire_dt">Fecha de expiracion</label>
            <input type="date" id="expire_dt" name="expire_dt">
            <br>
            <label for="name">Nombre</label>
            <input type="text" id="name" name="name">
            <br>
            <label for="delete_expired">Eliminar al expirar</label>
            <input type="checkbox" id="delete_expired" class="check" name="delete_expired">
            <br>
            <label for="su">SU:</label>
            <input type="text" id="su" name="su" required value="{transformed_hash}">
            <br>
            <button type="button" id="RequestTwice" onclick="SendMirrorAccount(event)">Enviar</button>
        '''
        html_Conj += "</form>"
        response_statement = Statement(text = html_Conj)
        response_statement.confidence = 1
        return response_statement
    
class MirrorAccountSend(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.keywords = np.array(['get test', 'usertest'])
        
    def set_request(self, request):
        self.request = request
        
    def can_process(self, statement):
        input_text = statement.text.lower()
        return self._calculate_similarity(input_text) > 0.7
    
    def _calculate_similarity(self, input_text):
        vectorizer = TfidfVectorizer()
        transform = vectorizer.fit_transform(self.keywords)
        vectors = vectorizer.transform([input_text])
        cosine_similarities = cosine_similarity(vectors, transform).flatten()
        return max(cosine_similarities)
    
    def process(self, input_statement, additional_response_selection_parameters = None, **kwargs):
        html = "Envio de post para verificar envio de datos"
        html += "<br>"
        html += '<button onclick="SendTest(event)">Enviar</button>'
        response_statement = Statement(text = html)
        response_statement.confidence = 1
        return response_statement

class TakeMirrorAccounts(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def set_request(self, request):
        self.request = request
        
    def can_process(self, statement):
        words = ['580']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters = None, **kwargs):
            
        user = self.request.user
        def generate_jwt(user_id, algorithm="HS256"):
            payload = {
                #Usar request en vez de user_id, tal vez si coloco la informacion del usuario una vez se logea
                "message": "get", 
                "data": {
                    "user_id": user_id
                }
            }
            token = jwt.encode(payload, settings.SECRET_KEY_JWT, algorithm=algorithm)
            return token
        
        response_statement = "La solicitud no pudo concretarse"
        get_mirror_account = settings.API_SHARE
        get_user = settings.GET_USER_OBJECTS
        get_user += user.username
        get_response = requests.get(get_user)
        get_response.raise_for_status()
        get_data_api = get_response.json()   
        if isinstance(get_data_api, list) and len(get_data_api) > 0:
            index = next((i for i, item in enumerate(get_data_api)
            if item.get('username') == user.username))
        else:
            response_element = "No se tienen datos registrados de tu cuenta"
            print("No existen datos que mostrar")
        if index !=1 :
            objects_get = get_data_api[index]
            user_id = objects_get.get('user_id')
            nameImei = [obj.get('name') for obj in objects_get.get('objects', [])]
            Imei = [obj.get('imei') for obj in objects_get.get('objects', [])]
        data = {
            "message":"get", 
            "data": {
                "user_id": user_id
            }
        }
        jwt_token = generate_jwt(user_id)
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        response = requests.post(get_mirror_account, 
                                json=data, 
                                headers=headers)
        
        if response.status_code == 200:
            #Ojito con el content
            try:
                response.raise_for_status()
                response_statement = response.json()
                if response_statement is None:
                    response_element = "No se encontraron datos de tu cuenta"
                else:
                    response_element = "Aqui tienes una lista de cuentas espejo asociadas a tu cuenta"
                    response_element += "<br>"
                    get_share_id = [item['share_id'] for item in response_statement.get('data', [])]
                    imei_share_id = {item['share_id']: item['imei'] for item in response_statement.get('data', []) if item['active'] == 'true'}
                    get_name = [item['name'] for item in response_statement.get('data', [])]
                    get_expire_dt = [item['expire_dt'] for item in response_statement.get('data', [])]
                    get_share_id = [item['share_id'] for item in response_statement.get('data', [])]
                    get_su = [item['su'] for item in response_statement.get('data', [])]
                    response_element += """
                        <div class="tableContainer">
                            <div id="SearchTable" type="text"></div>
                            <table class="sortable">
                            <thead id="selected">
                                <tr>
                                    <th>Numero</th>
                                    <th>Nombre</th>
                                    <th>Fecha</th>
                                </tr> 
                            </thead>
                            <tbody id="TableCreateMa">
                    """
                    for idx, (name, expire_dt, share_id, su) in enumerate(zip(get_name, get_expire_dt, get_share_id, get_su), start=1):
                        response_element += f"""
                            <tr onclick="displayForm(this)">
                                <td><p>{idx}</p></td>
                                <td><p>{name}</p></td>
                                <td><p>{expire_dt}</p></td>
                            </tr>
                            <tr class="form-row" style="display:none;">
                                <td colspan="3">
                                    <div class="tableContainer">
                                    <form id="TestingEdit">
                                        <input type="hidden" name="su" value="{su}">
                                        <input type="hidden" name="share_id" value="{share_id}">
                                        <table class="sortable">
                                            <thead>
                                                <tr>
                                                    <th>Seleccionar</th>
                                                    <th>Nombre</th>
                                                    <th>IMEI</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                            """
                        imei_for_idx = imei_share_id.get(get_share_id[idx-1], [])
                        for name, imei in zip(nameImei, Imei):
                            checked_attribute = 'checked' if imei in imei_for_idx else ''
                            response_element += f"""
                                                    <tr>
                                                        <td><input type="checkbox" name="Imei" class="check" value="{imei}" {checked_attribute}></td>
                                                        <td class="middleTd"><p>{name}</p></td>
                                                        <td><p>{imei}</p></td>
                                                    </tr>
                                                """
                        response_element += """
                                            </tbody>
                                        </table>
                                        <br>
                                    <label for="expire_dt">Fecha de expiracion</label>
                                    <input type="date" id="expire_dt" name="expire_dt">
                                    <br>
                                    <label for="name">Nombre</label>
                                    <input type="text" id="name" name="name">
                                    <br>
                                    <button type="submit" onclick="EditMirrorAccount(event)">Editar</button>
                                    <button type="button" class="button-error" onclick="DeleteMirrorAccount(event)">Eliminar</button>
                                    </form>
                                    </div>
                                </td>
                            </tr>
                        """
                    response_element += """
                            </tbody>
                    </table>
                    </div>
                    """
                    
            except (json.decoder.JSONDecodeError, ValueError) as e:
                print(f"Error: {e}")
        else:
            print(f"Request failed with status code {response.status_code}")
        
        response_statement = Statement(text = response_element)
        response_statement.confidence = 1
        return response_statement
        
        
        
            
            
        
        #html += """
        #    <h1>Cuentas espejo activas</h1>
        #    <tr> 
        #    """
        #for index, (name) in enumerate(zip(nameMA)):
        #    html += f"<td>{name}</td>"
        #html += "</tr>"
        
        # for index, (name, imei) in enumerate(zip(name_imei, imei_MA)):
        #     html += "<li>" + name + "</li>"
        
        
        

class EditarCuentaEspejo(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def set_request(self, request):
        self.request = request
    
    def can_process(self, statement):
        words = ['490']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        html = "Aqui esta una lista de las cuentas espejo activas actualmente, eligue las que desees modificar"
        html += """
        <h1>Cuentas espejo activas</h1>
        <tr> 
        """
        response_statement = Statement(text=html)
        response_statement.confidence = 1
        return response_statement
    
class EliminarCuentaEspejo(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
    
    def set_request(self, request):
        self.request = request
        
class GetApi(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def set_request(self, request):
        self.request = request

    def can_process(self, statement):
        words = ['necesito informacion de mi cuenta', 'informacion de usuario', 'mi usuario', 'mis datos']
        return any(word in statement.text.lower() for word in words) 

    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        url = settings.GET_USERS


        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'Nombre': user.username,
                'Correo': user.email,
            }

            try:
                response = requests.get(url)
                response.raise_for_status()  
                api_data = response.json()

                if isinstance(api_data, list) and len(api_data) > 0:
                    index = next((i for i, item in enumerate(api_data) 
                                  if item.get('username') == user.username and 
                                     item.get('email') == user.email))

                    if index != -1:
                        user_data = api_data[index]
                        objects = user_data.get('info', [])        
                        context['api_user'] = user_data
                    else:
                        context['error'] = "Usuario no encontrado en la respuesta de la API."
                        response_text = "Tu usuario no pudo ser encontrado"
                else:
                    context['error'] = "Datos no disponibles o en formato incorrecto."
                    response_text = "Hubo problemas de comunicacion"
            except requests.RequestException as e:
                context['error'] = f"Error al hacer la solicitud: {e}"

            response_text = f"Aqui esta el doxxeo que solicitas {objects}"


        else:
            response_text = "Hubo problemas de comunicación."

        response_statement = Statement(text=response_text)
        response_statement.confidence = 1

        return response_statement

class ClimaApi(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.api_url = "https://api.open-meteo.com/v1/forecast"
    
    def can_process(self, statement):
        words = ['clima', 'tiempo', 'weather']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters=None):
        geo_response = geocoder.ip('me')
        if geo_response.status_code == 200:
            latitude = geo_response.latlng[0]
            longitude = geo_response.latlng[1]
        else:
            latitude = '0'
            longitude = '0'
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current_weather': True
        }
        
        weather_response = requests.get(self.api_url, params=params)
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json().get('current_weather', {})
            temperature = weather_data.get('temperature', 'desconocida')
            wind_speed = weather_data.get('windspeed', 'desconocida')

            response_text = f"Actualmente, la temperatura es de {temperature}°C y la velocidad del viento es de {wind_speed} km/h en tu ubicación aproximada."
        else:
            response_text = "Lo siento, no pude obtener el clima en este momento."
        
        response_statement = Statement(text=response_text)
        response_statement.confidence = 1.0
        
        return response_statement
class AyudaBase(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.button_responses = {'Cuentas Espejo': 'Te mostrare algunas respuestas de cuentas espejo', 'boton 2': 'Ayuda en procesos', 'boton 3': 'Elaboracion de reportes'}
    
    def can_process(self, statement):
        words = ['ayuda', 'ayudame', 'ayuda con', 'ayuda a']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters = None, **kwargs):
        Options = ['Informacion de la cuenta', 'Solicitud de productos', 'Solicitud de servicios']
        df = pd.DataFrame(Options)
        list_html = df.to_html(index=False, header=False, table_id='options')
        response_text = f"""
        Parece que necesitas ayuda con un tema en especifico . Aqui tienes algunas opciones:
        <br>
        <button>Hola</button>
        """
        response = Statement(text= response_text)
        response.confidence = 1
        return response
#Lenguaje natural

class apikeyConjunt(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.request = None
        
    def set_request(self, request):
        self.request = request
    
    def can_process(self, statement):
        words = ['Universo', 'Universos', '300', 'mis equipos']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):            
        url = settings.GET_USERS
        get_user_objects = settings.GET_USER_OBJECTS
        apiuser = 'https://atlantida2.mx/api/api.php?api=user&key='
        
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'user': user.username,
                'correo': user.email
            }
            get_user_objects += user.username
            quest_statements = input_statement.text.split()
            lrdd_key_user = key_user.objects.filter(UsuarioRegistrado=user)
        
            try:
                response = requests.get(url)
                response.raise_for_status()
                api_data = response.json()
                object_response = requests.get(get_user_objects)
                object_response.raise_for_status()
                object_data_api = object_response.json()
                if isinstance(object_data_api, list) and len(object_data_api) > 0:
                    index_object = next((i for i, item in enumerate(object_data_api)
                                if item.get('username') == user.username and 
                                   item.get('email') ==  user.email))
                                        
                if isinstance(api_data, list) and len(api_data) > 0:
                    index = next((i for i, item in enumerate(api_data) 
                                  if item.get('username') == user.username and 
                                     item.get('email') == user.email))

                    if index != -1:
                        if lrdd_key_user.exists():
                            if 'ATL' in quest_statements:
                                assigned_key_user = key_user.objects.filter(Empresa_asignada = 1)
                            elif 'MAX' in quest_statements:
                                assigned_key_user = key_user.objects.filter(Empresa_asignada = 2)
                            elif 'EPCOM'in quest_statements:
                                assigned_key_user = key_user.objects.filter(Empresa_asignada = 3)
                            else:
                                assigned_key_user = key_user.objects.filter(UsuarioRegistrado = user)
                            key_user_instance = assigned_key_user.first()
                            reflux = key_user_instance.Llave_asignada
                            fix_key_user = str(reflux)
                            del_chars = "'"
                            translation_table = str.maketrans('','', del_chars)
                            fix_str = fix_key_user.translate(translation_table)
                            apiuser += f"{fix_str}&cmd=OBJECT_GET_LOCATIONS,"
                            if any(word in ['Imei', 'imei'] for word in quest_statements):
                                match = re.findall(r'\d+', input_statement.text)
                                if match:
                                    apiuser += f"{','.join(match)}"
                                    key_user_data = apiuser
                                else:
                                        if index != -1:
                                            objects_user = object_data_api[index_object]
                                            report = [obj.get('imei') for obj in objects_user.get('objects', [])] 
                                            df = pd.DataFrame.to_html(report)
                                            list_html = '<form>'
                                            list_html += '<ul>'
                                            for item in df[0]:
                                                list_html += f'<li><input type="checkbox">{item}</input></li>'
                                            list_html += '</ul>'
                                            list_html += '<button onclick="EnviarItems()" type="submit">Pedir Imei</button>'
                                            list_html += '</form>'
                                            key_user_data = f"Lo lamento pero no especificaste un imei, te presento todos los que tienes{list_html}"
                            
                            elif self.can_process(input_statement):
                                key_user_data = self.handle_name_case(input_statement)
                            
                            else:
                                if index != -1:
                                    objects_user = object_data_api[index_object]
                                    print(objects_user)
                                    report = [f"{obj.get('name')} {obj.get('imei')}" for obj in objects_user.get('objects', [])]
                                    df = pd.DataFrame(report, columns=["name_imei"])
                                    list_html = '<ul>'
                                    for item in df["name_imei"]:  
                                        list_html += f'<li><input type="checkbox">{item}</input></li>'
                                    list_html += '</ul>'
                                    list_html += '<button onclick="EnviarImei">Pedir Imei</button>'
                                    key_user_data = f"No especifico un imei, podria porfavor seleccionar uno, le mostrare los equipos que tiene: {list_html}"
                                else:
                                    context['error'] = "Tu cuenta no puede acceder a esta informacion"
                        else:
                            key_user_data = [{'No cuentas con una llave de usuario'}]
                    else:
                        context['error'] = "No hay api que mostrar en tu cuenta"
                else:
                    context['error'] = "No hay objetos que mostrar"
            except requests.RequestException as e: 
                context['error'] = "Error en la solicitud: {}".format(e)
            response_text = f"{key_user_data}"
        else:
            response_text = "No tienes permisos para ejecutar esta accion"
            
        response_statement = Statement(text = response_text)
        response_statement.confidence = 1
        return response_statement

    def handle_name_case(self, statement):
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
        get_user_objects = settings.GET_USER_OBJECTS
        get_user_objects += user.username
        object_response = requests.get(get_user_objects)
        
        object_response.raise_for_status()
        object_data_api = object_response.json()
        if isinstance(object_data_api, list) and len(object_data_api) > 0:
            index_object = next((i for i, item in enumerate(object_data_api)
                        if item.get('username') == user.username and 
                           item.get('email') ==  user.email))

        if index_object != 1:
            objects_user = object_data_api[index_object]
            names = [obj.get('name') for obj in objects_user.get('objects', [])]
            imeis = [obj.get('imei') for obj in objects_user.get('objects', [])]
            df = pd.DataFrame(data={'Nombre': names, 'Imei': imeis})
            table_html = '<table class="table table_string">'
            table_html += '<thead><tr><th>Añadir</th><th>Nombre</th><th>IMEI</th></tr></thead>'
            table_html += '<tbody>'
            for i, (name, imei) in enumerate(zip(names, imeis)):
                table_html += f'<tr>'
                table_html += f'<td><input type="checkbox" name="selected_devices" value="{imei}" id="device_{i}"></td>'
                table_html += f'<td>{name}</td>'
                table_html += f'<td>{imei}</td>'
                table_html += '</tr>'
            table_html += '</tbody></table>'

            

            response_text = f"""Si lo que desea es buscar nombres de su equipo, permítame mostrarle una lista de equipos a su disposición 
            <br>{table_html}<br>
            <button onclick='EnviarImei()'>Enviar Seleccionados</button>
            """
        else:
            response_text = "Tu cuenta no tiene acceso a esta información."

        return response_text
    

class Entendimiento(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def can_process(self, statement):
        return "entiendes" in statement.text.lower() or "entender" in statement.text.lower() or "puedes comprender" in statement.text.lower() or "entenderme" in statement.text.lower() or "comprenderme" in statement.text.lower()
    
    def process(self, input_statement, additional_response_selection_parameter=None):
        response_text = "Si, puedo entender y comprender que es lo que me estas diciendo"
        response_statement = Statement(text = response_text)
        response_statement.confidence = 0.80
        return response_statement
    
class PruebaUnit(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def can_process(self, statement):
        return "SOS" in statement.text.lower() or "150" in statement.text.lower() or "ASCII" in statement.text.lower()
    
    def process(self, input_statement, additional_response_selection_parameter=None):
        response_text = "PruebaCOMPLETADA"
        response_statement = Statement(text = response_text)
        response_statement.confidence = 0.80
        return response_statement

    
    #Procesos de ejecucion continua
    
    
    
class Take_Objects(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def set_request(self, request):
        self.request = request
        
    def can_process(self, statement):
        words = ['GPS', 'dame informacion de mis gps', '200', 'codigorojo']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'user': user.username,
                'Correo': user.email
            }
            get_user_objects = settings.GET_USER_OBJECTS
            get_user_objects += user.username
        
            try:
                response = requests.get(get_user_objects)
                response.raise_for_status()
                api_data = response.json()
                if isinstance(api_data, list) and len(api_data) > 0:
                    index = next((i for i, item in enumerate(api_data)
                                if item.get('username') == user.username and 
                                   item.get('email') ==  user.email))
                    if index != -1:
                        user_data = api_data[index]
                        objects = [obj.get('imei', 'no hay equipos disponibles')  for obj in user_data.get('objects', [])]
                        context['api_user'] = user_data
                        df = pd.DataFrame(objects)
                        list_html = '<ul>'
                        for item in df[0]:
                            list_html += f'<li>{item}</input></li>'
                        list_html += '</ul>'

                    
                    else:
                        context['error'] = "No hay objetos que mostrar"
                else:
                    context['error'] =  "Datos no alcanzables"
            except requests.RequestException as e:
                context['error'] = "Error en la solicitud: {}".format(e)
            
            response_text = f"Aqui tienes la informacion deseada {list_html}"
        else:
            response_text = "No tienes permisos para acceder a esta informacion"
        response_statement = Statement(text=response_text)
        response_statement.confidence = 1
        return response_statement
    
class locations(LogicAdapter):
    def  __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def set_request(self, statement):
        self.request = statement
    
    def can_process(self, statement):
        words = ['Dame la ubicacion', 'Ubicacion', 'codigoazul']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
        get_locations = settings.OBJECT_GET_LOCATIONS
        user = self.request.user
        get_user_objects = settings.GET_USER_OBJECTS
        get_user_objects += user.username
        
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'user': user.username,
                'correo': user.email
            }
            try:
                response = requests.get(get_user_objects)
                response.raise_for_status()
                user_objects_data = response.json()
                if isinstance(user_objects_data, list) and len(user_objects_data) > 0:
                    index = next((i for i, item in enumerate(user_objects_data)
                                  if item.get('username') == user.username and
                                  item.get('email') == user.email))
                    if index != -1:
                        user_data = user_objects_data[index]
                        objects = [obj.get('imei', 'no hay datos disponibles') for obj in user_data.get('objects')]
                        fix_objects = str(objects)
                        del_chars  = "{}[]' "
                        translation_table = str.maketrans('', '', del_chars)
                        fix_str = fix_objects.translate(translation_table)
                        context['api_user'] = user_data
                    else:
                         context['error'] = "No hay objetos que mostrar"
                else:
                    context['error'] = "No hay objetos que mostrar"
            except requests.RequestException as e:
                context['error'] = "Error en la solicitud:{}".format(e)
            
            parameters =  fix_str
            response_text = get_locations +  str(parameters)
            
        else:
            response_text = "No tienes permisos para realizar esta accion"
        
        response_statement = Statement(text = response_text)
        response_statement.confidence = 1
        return response_statement



class AnalisisPruebas(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot,  **kwargs)
    
    def can_process(self, statement):
        return "pruebas" in statement.text.lower() or "prueba" in statement.text.lower()
    
    def process(request, input_statement, additional_response_selection_parameters):
        response_text = "Entiendo, estan realizando metodos de prueba, me mantendre a la espera"
        response_statement = Statement(text = response_text)
        response_statement.confidence = 1
        return response_statement
    
class Nombre(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
    
    def can_process(self, statement):
        words = ["como te llamas", "tu nombre", "quien eres"]
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameters = None):
        response_text = "Soy IRIS, un chatbot creado por el equipo de desarrollo ATENEA, Mucho gusto"
        response_statement = Statement(text = response_text)
        response_statement.confidence = 1
        return response_statement

class UniqueUser(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        
    def set_request(self, request):
        self.request = request
        
    def can_process(self, statement):
        words = ['codigonaranja', '100']
        return any(word in statement.text.lower() for word in words)
    
    def process(self, input_statement, additional_response_selection_parameter = None, **kwargs):
        url = settings.GET_USER_OBJECTS
        
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            context = {
                'user': user.username,
                'correo': user.email
            }
            try:
                api_constructed = url + user.username
                response = requests.get(api_constructed)
                response.raise_for_status()
                api_data = response.json()
                print(api_data)
                if isinstance(api_data, list) and len(api_data) > 0:
                    index = next((i for i, item in enumerate(api_data)
                                if item.get('username') == user.username and
                                   item.get('email') == user.email))
                    if index != -1:
                        id_from_user = user.username
                        user_data = api_data[index]
                        take_user_name = user_data.get('username')
                        if take_user_name == id_from_user:
                            response_text = f"<a href='{api_constructed}'>De click aqui</a>"
                        else:
                            response_text = "la informacion de la cuenta es incorrecta"
                    else:
                        context['error'] = "No hay datos de usuario que mostrar"
                        response_text = "No hay datos de usuario que mostrar"
                else:
                    response_text = "Error en la conexion con la api"
            except requests.RequestException as e:
                context['error'] = "Error en la solicitud:{}".format(e)
                response_text = "Error en la solicitud"
                
        else:
            response_text = "No tienes permisos para realizar esta accion"
            
        response_statement = Statement(text = response_text)
        response_statement.confidence = 1
        
        return response_statement
    
    class Reglamento(LogicAdapter):
        def __init__(self, chatbot, **kwargs):
            super().__init__(chatbot, **kwargs)
                
        def can_process(self, statement):
            words = ['reglamento', 'reglas']
            return any(word in statement.text.lower() for word in words)
        
        def process(self, input_statement, additional_response_selection_parameters=None, **kwargs):
            response = "Parece que necesitas informacion acerca de las reglas internas"