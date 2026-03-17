from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import pandas as pd
import json
import random
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import fetch_covid_data, get_top_countries

# Load FAQ data once at startup
try:
    FAQ_DF = pd.read_csv('cdc_qa.csv', header=0, names=['Questions', 'Answers'])
except FileNotFoundError:
    FAQ_DF = pd.DataFrame(columns=['Questions', 'Answers'])


@require_http_methods(["GET"])
def indexPage(request):
    try:
        covid_data = fetch_covid_data()
        if not covid_data:
            raise Exception("Failed to fetch COVID-19 data")

        global_data = covid_data['global']
        top_countries = get_top_countries(covid_data['countries'])

        context = {
            'global_data': global_data,
            'top_countries': top_countries[:10],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        return render(request, 'dashboard.html', context)

    except Exception as e:
        print(f"Error fetching COVID data: {e}")
        context = {
            'global_data': {
                'cases': 0, 'todayCases': 0, 'deaths': 0, 'todayDeaths': 0,
                'recovered': 0, 'todayRecovered': 0, 'active': 0, 'critical': 0,
                'affectedCountries': 0, 'casesPerOneMillion': 0, 'deathsPerOneMillion': 0,
            },
            'top_countries': [],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': 'Unable to fetch COVID-19 data. Please try again later.',
        }
        return render(request, 'dashboard.html', context)


def chatbotPage(request):
    return render(request, 'chatbot.html')


@csrf_exempt
def chatBot(request):
    if request.method != "POST":
        return JsonResponse({'response': 'Invalid request method'})

    user_message = request.POST.get('message', '').lower().strip()
    if not user_message:
        return JsonResponse({'response': 'Please enter a message.'})

    # Greetings
    greetings = ["hello", "hi", "hey", "greetings", "what's up"]
    if any(g in user_message for g in greetings):
        return JsonResponse({'response': random.choice([
            "Hello! How can I help you with COVID-19 information today?",
            "Hi there! I'm here to provide COVID-19 information. What would you like to know?",
            "Welcome! Ask me anything about COVID-19.",
        ])})

    # Goodbyes
    goodbyes = ["bye", "goodbye", "see you", "take care"]
    if any(g in user_message for g in goodbyes):
        return JsonResponse({'response': random.choice([
            "Goodbye! Stay safe and take care!",
            "Bye! Remember to follow health guidelines.",
            "Take care! Feel free to come back with more questions.",
        ])})

    # FAQ matching via TF-IDF
    try:
        if FAQ_DF.empty:
            return JsonResponse({'response': "I'm having trouble accessing the knowledge base. Please try again later."})

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(FAQ_DF['Questions'].values.astype('U'))
        user_tfidf = vectorizer.transform([user_message])
        similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()

        best_idx = similarities.argmax()
        if similarities[best_idx] > 0.2:
            response = FAQ_DF.iloc[best_idx]['Answers']
        else:
            response = (
                "I'm not sure I understand. Could you rephrase your question? Here are some things you can ask:\n"
                "- What are the symptoms of COVID-19?\n"
                "- How does COVID-19 spread?\n"
                "- What are the prevention measures for COVID-19?"
            )

        return JsonResponse({'response': response})

    except Exception:
        return JsonResponse({'response': "I'm having trouble processing your request. Please try again later."})


def prediction(request):
    selectedCountry = "Worldwide"
    imagesAppend = "/static/img/totalp.png"

    # Fallback country list
    countryNames = ["US", "India", "Brazil", "Russia", "France", "Turkey", "UK", "Italy", "Argentina"]

    try:
        confirmedGlobal = pd.read_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
            encoding='utf-8', na_values=None
        )
        barPlotData = confirmedGlobal[['Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
        barPlotData = barPlotData.reset_index()
        barPlotData.columns = ['Country/Region', 'values']
        barPlotData = barPlotData.sort_values(by='values', ascending=False)
        countryNames = barPlotData['Country/Region'].values.tolist()
    except Exception as e:
        print(f"Error loading COVID data: {e}")

    available_countries = ["india", "argentina", "italy", "uk", "us", "france", "turkey", "russia", "brazil"]

    if request.method == "POST":
        selectedCountry = request.POST.get('drop1', 'Worldwide')
        country_key = selectedCountry.lower()
        if country_key in available_countries:
            imagesAppend = f"/static/img/{country_key}p.png"
        else:
            imagesAppend = "/static/img/turkeyp.png"

    return render(request, 'prediction.html', {
        'Country': countryNames,
        'selectedCountry': selectedCountry,
        'imagesAppend': imagesAppend,
    })


def vaccination(request):
    imageLeft = False
    imageRight = False
    estimatedGraph = False

    if request.method == 'POST':
        button_map = {
            'dailyv': ('/static/img/daily1.png', '/static/img/daily2.png'),
            'dailyp': ('/static/img/dailyp1.png', '/static/img/dailyp2.png'),
            'peoplev': ('/static/img/people1.png', '/static/img/people2.png'),
            'peoplep': ('/static/img/peoplep1.png', '/static/img/peoplep2.png'),
            'totalc': ('/static/img/total1.png', '/static/img/total2.png'),
        }

        for key, (left, right) in button_map.items():
            if key in request.POST:
                imageLeft = left
                imageRight = right
                break
        else:
            if 'estimate' in request.POST:
                estimatedGraph = True

    return render(request, 'vaccination.html', {
        'imageleft': imageLeft,
        'imageright': imageRight,
        'estimatedgraph': estimatedGraph,
    })


def handler404(request, exception):
    return render(request, '404.html', status=404)
