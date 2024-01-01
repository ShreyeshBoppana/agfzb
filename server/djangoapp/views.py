from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
import logging
import json,requests
from cloudant.client import Cloudant

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
from django.contrib.messages import success

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    # Redirect superuser to logout page with superuser name in the URL
                    desired_url = reverse('djangoapp:logout') + f'?superuser_name={user.username}'
                    return HttpResponseRedirect(desired_url)
                else:
                    # Redirect other users to a different page
                    return HttpResponseRedirect(reverse('djangoapp:index'))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'djangoapp/login.html', {'form': form})


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def custom_logout(request):
    # Get the superuser name if the user is authenticated
    superuser_name = request.user.username if request.user.is_authenticated and request.user.is_superuser else None

    # Check if the user is authenticated before logging out
    if request.user.is_authenticated:
        logout(request)

    return render(request, 'djangoapp/logout.html', {'superuser_name': superuser_name})

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def create_superuser(request):
    if request.method == 'POST':
        # Get superuser details from the form
        superuser_username = request.POST.get('superuser_username')
        superuser_password = request.POST.get('superuser_password')
        superuser_first_name = request.POST.get('superuser_first_name')
        superuser_last_name = request.POST.get('superuser_last_name')

        # Check if the superuser already exists
        if User.objects.filter(username=superuser_username).exists():
            messages.error(request, 'Superuser with this username already exists.')
        else:
            # Create a new superuser with the provided details
            User.objects.create(
                username=superuser_username,
                password=make_password(superuser_password),
                first_name=superuser_first_name,
                last_name=superuser_last_name,
                is_superuser=True,
                is_staff=True,
            )

            # Display success message
            messages.success(request, 'Superuser created successfully.')

            # Optionally, you can automatically log in the new superuser
            # call_command('createsuperuser', interactive=False, username=superuser_username, email='', stdout=request)

    return render(request, 'djangoapp/create_superuser.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    credentials = {
        "COUCH_USERNAME": "ab981cfb-e733-47e6-8485-ad9006c44a9e-bluemix",
        "IAM_API_KEY": "HSTZ31wV2O8kj6DgM_EfE3BfjTMmbEvFjn6EvdYdPrm4"
    }

    # Connect to Cloudant with IAM authentication
    client = Cloudant.iam(
        account_name=credentials["COUCH_USERNAME"],
        api_key=credentials["IAM_API_KEY"],
        connect=True
    )

    # Get a list of all databases
    all_dbs = client.all_dbs()

    # Create a dictionary to store data
    response_data = {"dbs": all_dbs, "data": {}}

    # Extract data from each database
    for db_name in all_dbs:
        database = client[db_name]
        documents = [doc for doc in database]
        response_data["data"][db_name] = documents

    d=response_data["data"]["dealerships"]

    # Close the Cloudant connection
    client.disconnect()

    # Create HttpResponse
    response = HttpResponse(json.dumps(d), content_type="application/json")
    
    return response



def get_reviews(request , id):
    credentials = {
        "COUCH_USERNAME": "ab981cfb-e733-47e6-8485-ad9006c44a9e-bluemix",
        "IAM_API_KEY": "HSTZ31wV2O8kj6DgM_EfE3BfjTMmbEvFjn6EvdYdPrm4"
    }

    # Connect to Cloudant with IAM authentication
    client = Cloudant.iam(
        account_name=credentials["COUCH_USERNAME"],
        api_key=credentials["IAM_API_KEY"],
        connect=True
    )

    # Get a list of all databases
    all_dbs = client.all_dbs()

    # Create a dictionary to store data
    response_data = {"dbs": all_dbs, "data": {}}

    # Extract data from each database
    for db_name in all_dbs:
        database = client[db_name]
        documents = [doc for doc in database]
        response_data["data"][db_name] = documents

    d=response_data["data"]["reviews"]

    j=json.loads(json.dumps(d))


    d=dict()

    for entry in j:
        if entry.get('id') == id:
            d=entry

    # Close the Cloudant connection
    client.disconnect()

    # Create HttpResponse
    response = HttpResponse(json.dumps(d), content_type="application/json")
    
    return response

'''def get_sentiment(request):
    url = 'https://sn-watson-sentiment-bert.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/SentimentPredict'
    myobj = { "raw_document": { "text": "I am happy" } }
    header = {"grpc-metadata-mm-model-id": "sentiment_aggregated-bert-workflow_lang_multi_stock"}
    response = requests.post(url, json = myobj, headers=header)
    f=json.loads(response.text)
    label = f['documentSentiment']['label']
    score = f['documentSentiment']['score']
    d={}
    d['label']=label
    d['score']=score
    response = HttpResponse(json.dumps(d), content_type="application/json")
    
    return response'''


def get_sentiment(request , id):
    credentials = {
        "COUCH_USERNAME": "ab981cfb-e733-47e6-8485-ad9006c44a9e-bluemix",
        "IAM_API_KEY": "HSTZ31wV2O8kj6DgM_EfE3BfjTMmbEvFjn6EvdYdPrm4"
    }

    # Connect to Cloudant with IAM authentication
    client = Cloudant.iam(
        account_name=credentials["COUCH_USERNAME"],
        api_key=credentials["IAM_API_KEY"],
        connect=True
    )

    # Get a list of all databases
    all_dbs = client.all_dbs()

    # Create a dictionary to store data
    response_data = {"dbs": all_dbs, "data": {}}

    # Extract data from each database
    for db_name in all_dbs:
        database = client[db_name]
        documents = [doc for doc in database]
        response_data["data"][db_name] = documents

    d=response_data["data"]["reviews"]

    j=json.loads(json.dumps(d))


    d=dict()

    for entry in j:
        if entry.get('id') == id:
            d=entry.get('review')

    # Close the Cloudant connection
    client.disconnect()

    s=str(d)
    # Create HttpResponse


    url = 'https://sn-watson-sentiment-bert.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/SentimentPredict'
    myobj = { "raw_document": { "text": s } }
    header = {"grpc-metadata-mm-model-id": "sentiment_aggregated-bert-workflow_lang_multi_stock"}
    response = requests.post(url, json = myobj, headers=header)
    '''f=json.loads(response.text)
    label = f['documentSentiment']['label']
    score = f['documentSentiment']['score']
    d={}
    d['label']=label
    d['score']=score'''
    response = HttpResponse(response, content_type="application/json")
    
    return response