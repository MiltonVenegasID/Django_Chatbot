# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from smtplib import  SMTP
from django.http import JsonResponse, HttpResponse
import pyttsx3
from .AdaptadoresLogicos import *
import wikipedia
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
import threading
from django.contrib.auth.views import LoginView
from .forms import *
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from nltk.sentiment.util import *
from django.contrib.auth.mixins import LoginRequiredMixin
import speech_recognition as sr
import pyotp
from datetime import datetime, timedelta
from django.conf import settings
import openai
from django.core.mail import get_connection, send_mail
from django.core.exceptions import PermissionDenied
import json
import base64
from functools import wraps
import hmac
import hashlib
import jwt
import vertexai
from vertexai.language_models import TextGenerationModel, SafetySetting

stemmer = SnowballStemmer("spanish")
lemmatizer = WordNetLemmatizer()
wikipedia.set_lang('es')
engine = pyttsx3.init()
r = sr.Recognizer()

openai.api_key = getattr(settings, "OPENAI_API_KEY", None)

class CustomChatBot(ChatBot):
    def get_response(self, input_statement, **kwargs):
        if isinstance(input_statement, str):
            input_statement = self.storage.create(
                text=input_statement,
            )
            
        request = kwargs.get('request', None)
        for adapter in self.logic_adapters:
            if hasattr(adapter, 'set_request'):
                adapter.set_request(request)
        
        response = None
        for adapter in self.logic_adapters:
            if adapter.can_process(input_statement):
                response = adapter.process(input_statement)
                if response.confidence >= 0.2:
                    break
        
        if response is None or response.confidence < 0.2:
            fallback_response = generate(input_statement.text)
            response = fallback_response
        
        return response
    
def generate(User_Input):
    vertexai.init(project="dev-atenea-1", location="us-central1")
    model = TextGenerationModel.from_pretrained("gemini-exp-1206")
    responses = model.generate_text(
        User_Input,
        max_output_tokens=2048,
        temperature=1,
        top_p=1,
        safety_settings=safety_settings
    )

    for response in responses:
        print(response.text, end="")

textsi_1 = """Eres una inteligencia artificial enfocada en proveer los servicios de seguridad de transporte que la empresa provee"""

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]

#Delete?
def Chat_GPT(user_text):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}],
        max_tokens=100
    )
    return response.choices[0].message['content'].strip()
    

chatbot = CustomChatBot('IRIS', 
    storage_adapters = [
        
        {'import_path': 'chatterbot.storage.ContextualMemoryStorageAdapter'}
    ],
    comparison_method= [ 
    { 'import_path': 'chatterbot.comparisons.LevenshteinDistance' }
], response_selection = [
    { 'import_path': 'chatterbot.response_selection.get_first_response' }
],     
    logic_adapters=[
    {'import_path': 'mainApp.AdaptadoresLogicos.ClimaApi'},
    {'import_path': 'mainApp.AdaptadoresLogicos.InformacionUsuario'},
    {'import_path': 'mainApp.AdaptadoresLogicos.AyudaBase'},
    {'import_path': 'mainApp.AdaptadoresLogicos.GetApi'},
    {'import_path': 'mainApp.AdaptadoresLogicos.Entendimiento'},
    {'import_path': 'mainApp.AdaptadoresLogicos.PruebaUnit'},
    {'import_path': 'mainApp.AdaptadoresLogicos.Nombre'},   
    {'import_path': 'mainApp.AdaptadoresLogicos.Take_Objects'},
    {'import_path': 'mainApp.AdaptadoresLogicos.locations'},
    {'import_path': 'mainApp.AdaptadoresLogicos.apikeyConjunt'},
    {'import_path': 'mainApp.AdaptadoresLogicos.CuentaEspejo'},
    {'import_path': 'mainApp.AdaptadoresLogicos.UniqueUser'},
    {'import_path': 'mainApp.AdaptadoresLogicos.FallBack'},
    {'import_path': 'mainApp.AdaptadoresLogicos.EditarCuentaEspejo'},
    {'import_path': 'mainApp.AdaptadoresLogicos.MirrorAccountSend'}
]  
)



def borrarIris(request):
    chatbot.storage.drop()
    return JsonResponse({'response': 'Conocimiento de iris eliminado'})


trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train('chatterbot.corpus.custom')

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.loop_running = False
        self.engine.setProperty('rate', self.engine.getProperty('rate') * 0.8)
        self.engine.setProperty('volume', 0.0)

    def speak(self, text):
        if not self.loop_running:
            self.loop_running = True
            self.engine.say(str(text))
            self.engine.runAndWait()
        else:
            raise RuntimeError("El loop ya ha comenzado")
            
    def speak_in_thread(self, text):
        thread = threading.Thread(target=self.speak, args=(text))
        self.loop_running = False
        self.engine.stop()
        thread.start()
        #TODO:
        #FIXME:

tts = TextToSpeech()
    
def fetch_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Tu peticion podria incluir demasiados temas {e.options}"
    except wikipedia.exceptions.PageError:
        return "No pude encontrar información sobre ese tema"
    

def audioOption():
    with sr.Microphone() as source2:
        r.adjust_for_ambient_noise(source2, duration=2)
        audio2 = r.listen(source2)
        

    
def find_similar_response(user_input, chatbot):
    conversation_pairs = chatbot.storage.filter()
    for statement in conversation_pairs:
        question = str(statement.text).strip().lower()
        
        if user_input == question:
            response = statement.in_response_to
            return response    
    return None

def show_spinner(request):
    return JsonResponse({'show_spinner': True})

def hide_spinner(request):
    return JsonResponse({'show_spinner': False})

def extract_single_dash_responses(conversation):
    responses = []
    for line in conversation:
        if isinstance(line, str) and line.startswith('-'):
            responses.append(line.lstrip('- ').strip())
    return responses



def get_bot_response(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        user_input = re.sub(r'[^\w\s\-áéíóúÁÉÍÓÚñÑ]', '', user_input)
        
        if not user_input or not isinstance(user_input, str):
            return JsonResponse({'response': 'Entrada inválida'}, status=400)
            
        preprocessed_input = user_input.lower()

        if len(preprocessed_input) > 100:
            return JsonResponse({'response': 'Por favor, intenta ser más específico'}, status=400)
            
        allowed_keywords = ["investiga", "busca", "búscame", "busca sobre", "investigame", "buscame"]
        
        if any(keyword in user_input.lower() for keyword in allowed_keywords):
            topic = user_input.lower()
            for keyword in allowed_keywords:
                topic = topic.replace(keyword, "")
            topic = topic.strip()
            
            if not topic or len(topic) < 2:
                return JsonResponse({'response': 'Por favor especifica un tema válido'}, status=400)
                
            bot_response = fetch_wikipedia_summary(topic)
            
        else:
            if not preprocessed_input.strip():
                return JsonResponse({'response': 'Entrada inválida'}, status=400)
                
            chatterbot_response = chatbot.get_response(preprocessed_input, request=request)
            bot_response = chatterbot_response
        is_html = bool(re.search(r'<[^>]+>', str(bot_response)))
        
        response_data = {
            'response': str(bot_response),
            'is_html': is_html
        }

        response = JsonResponse(response_data)
        threading.Thread(target=tts.speak, args=(bot_response,)).start()

        return response

    return JsonResponse({'response': 'Solicitud inválida'}, status=400)

User = get_user_model()

def send_otp(self, request):
    cus_host = settings.CUS_HOST
    cus_port = '587'
    cus_username = settings.CUS_USERNAME
    cus_password = settings.CUS_PASSWORD
    cus_use_tls = True
    connection = get_connection(host = cus_host,
                   port = cus_port,
                   username = cus_username,
                   password = cus_password,
                   use_tls  = cus_use_tls)

    totp = pyotp.TOTP(pyotp.random_base32(), interval=120)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=5)
    request.session['otp_valid_date'] = valid_date.isoformat()
    user = User.objects.filter(username=request.session.get('username')).first()
    if not User:
        return False 
    else:
        send_mail(
        'Verificacion de contraseña de una sola vez IRIS',
        f'Tu contraseña de un solo uso es :  {otp}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        connection= connection

        )
        print(f'{otp}')
        return True  

        
class Inicio(LoginView):
    template_name = 'start.html'
    form_class = AuthenticationForm
    
    def logout(request):
        logout(request)
        return redirect('index')
    
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'start.html', {'form': form})

    def post(self, request):
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    request.session['username'] = username
                    request.session['logged_in_via_login_view'] = True
                    send_otp(self, request)
                    return redirect('ruleOTP')  
                    
                else:
                    form.add_error(None, 'Incorrect username or password')
                    

        
        
class OTPView(View):
    def get(self, request):
        request.user.id
        error_message = None
        if request.session.get('logged_in_via_login_view') and request.session.get('username'):
            form = OTPForm(request.POST or None)
            otp = request.session.get('otp')
            print(otp)
            return render(request, 'OTP.html', {'form': form, 'error_message': error_message})
        elif not request.session.get('username'):
            return redirect('index')
        else:
            raise PermissionDenied()
    
    def post(self, request):
        form = OTPForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            otp = form.cleaned_data['otp']
            username = request.session.get('username')
            otp_secret_key = request.session.get('otp_secret_key')
            otp_valid_date = request.session.get('otp_valid_date')

            if otp_secret_key and otp_valid_date:
                valid_until = datetime.fromisoformat(otp_valid_date)
                if datetime.now() < valid_until:
                    totp = pyotp.TOTP(otp_secret_key, interval=120)
                    if totp.verify(otp):
                        user = get_object_or_404(User, username=username)
                        login(request, user)
                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        request.session.pop('logged_in_via_login_view', None)
                        return redirect('Iris') 
                    else:
                        error_message = f'Codigo OTP invalido. {otp}, {totp}'
                else:
                    error_message = 'El codigo OTP ha expirado, por favor solicite uno nuevo.'
            else:
                error_message = 'No se ha solicitado un codigo OTP.'

        return render(request, 'OTP.html', {'form': form, 'error_message': error_message})

   
class Iris(LoginRequiredMixin, View):
    def get(self, request, *args,  **kwargs):
        request.user.id
        if request.user.is_authenticated:
            return render(request, 'CuentasFantasma/proceso.html')
        else:
            return PermissionDenied()

def create_jwt_token(select_id, algorithm="HS256"):
    payload = {
        #Usar request en vez de user_id, tal vez si coloco la informacion del usuario una vez se logea
        "user_id": select_id,
        "exp": datetime.now() + timedelta(hours = 1),
        "iat": datetime.now()
    }
    #secret_key = settings from php
    #TODO
    token = jwt.encode(payload, settings.SECRET_KEY_JWT, algorithm=algorithm)
    print(token)
    return token

def send_to_api(apiReturn, data, select_id):
    jwt_token = create_jwt_token(select_id)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'{jwt_token}' 
    }
    
    test = json.dumps(headers)
    print(test)
    try:
        response = requests.Request(method="POST", url=apiReturn, json=data, headers = headers)
        session = requests.Session()
        prep = response.prepare()
        full_request = f"""
        --- Prepared Request ---
        URL: {prep.url}
        Headers:
        {prep.headers}
        
        Body:
        {prep.body}
        """
        print(full_request)
        new_res = session.send(prep)
        if new_res.status_code == 200:
            return new_res.json()  
        else:
            print(f"Request failed with status code {response.status_code}")
            print(f"Response text: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def verify_api_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        stored_token = request.session.get('api_token')
        if not stored_token:
            return JsonResponse({'error': 'Invalid session'}, status=401)
        
        signature = hmac.new(settings.SECRET_KEY.encode(), stored_token.encode(), hashlib.sha256).hexdigest()
        print(signature)
        return func(request, *args, **kwargs)
    return wrapper

def CreateSubAccount(request):
    if request.method == 'POST':
        token = base64.b64encode(settings.SECRET_KEY.encode()).decode()
        get_user = settings.GET_USER_OBJECTS
        get_user += request.user.username
        req_response = requests.get(get_user)
        req_data = req_response.json()
        
        if isinstance(req_data, list) and len(req_data) > 0:
            index = next((i for i, item in enumerate (req_data) if item['username'] == request.user.username), None)
            
        if index != -1:
            user_id = req_data[index]
            select_id = user_id.get('user_id')
        try:
            data = json.loads(request.body)
            selected_imeis = data.get('Imei', '')
            if len(selected_imeis) > 0:
                selected_date = data.get('expire_dt')
                selected_name = data.get('name')
                formData = {key: value for key, value in data.items() if key != 'Imei'}
                data['token'] = token
                request.session['api_token'] = token
                aglome = datetime.now().strftime('%Y-%m-%d')
                apiReturn = settings.API_SHARE
                Construct_name= f'DEV_{aglome}_{select_id}'
                constr_name = {"name": Construct_name}
                expire_add = {"expire": False}
                
                #Testeando envio de metodo post 
                data = {
                    "message": "request",
                    "data":{
                            "active": True,
                            "share_id": "",
                            "user_id": select_id,
                            "email": "",
                            "phone": "",
                            "expire": True,
                            **formData,
                            "imei": selected_imeis.split(',') if selected_imeis else []},
                    "key": "hashpartial"
                }
                

                if selected_date == "" or selected_date == None:
                    data['data'].update(expire_add)

                if selected_name == "" or selected_name == None:
                    data['data'].update(constr_name)

                response = send_to_api(apiReturn, data, select_id)
                if response is not None:
                    return JsonResponse({'response': 'Cuenta espejo creada con éxito'})
            else:
                print("No hay IMEIS")
                return JsonResponse({'response': 'No se selecciono imei'})
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        else:
            return JsonResponse({'error': 'Tu peticion no ha sido verificada, por favor contacta a soporte'}, status=401)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#FIX
def EditSubAccount(request):
    if request.method == 'POST':
        get_user = settings.GET_USER_OBJECTS
        get_user += request.user.username
        req_response = requests.get(get_user)
        req_data = req_response.json()
        
        if isinstance(req_data, list) and len(req_data) > 0:
            index = next((i for i, item in enumerate(req_data) if item['username'] == request.user.username), None)
            
            if index is not None:
                user_id = req_data[index]
                select_id = user_id.get('user_id')
                
                active_mirror_accounts = []  
                for account in req_data:
                    if account.get('active'): 
                        active_mirror_accounts.append({
                            'share_id': account.get('share_id'),
                            'selected_name': account.get('selected_name'),
                        })
                
                return JsonResponse({'Cuentas espejo activas': active_mirror_accounts})
        
        return JsonResponse({'error': 'No se encontraron cuentas espejo activas'}, status=404)

def LinkSubAccount(request):
    endpoint = "https://atlantida2.mx/index.php?su="
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expected_format = {
                "message": "update",
                "data": {
                    
                }
            }
        except:
            return JsonResponse({'error': 'Tu peticion no ha sido verificada, por favor'})
    
class Med(View):
    def get(self, request):
        formR  = TestRegister()
        return render(request, 'Inicio/lol.html', {'form': formR})
    
    def post(self, request):
        formR =  TestRegister(request.POST)
        if formR.is_valid():
            formR.save()
            return redirect('index')
        else:
            return render(request, 'Inicio/lol.html', {'form': formR})


class VistaRegistro(View):
    def get(self, request):
        form = CustomUserCreationForm()  
        return render(request, 'registro.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('index') 
        else:
            return render(request, 'registro.html', {'form': form})
    
