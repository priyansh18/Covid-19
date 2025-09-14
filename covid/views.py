from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import joblib
import os

# Load FAQ data
try:
    df = pd.read_csv('cdc_qa.csv', header=0, names=['Questions', 'Answers'])
except FileNotFoundError:
    df = pd.DataFrame(columns=['Questions', 'Answers'])

# Initialize prediction model
MODEL_PATH = 'covid_prediction_model.joblib'

def train_prediction_model():
    """Train a simple prediction model for COVID-19 cases"""
    # This is a placeholder - in a real app, you'd use historical data
    # For now, we'll create some synthetic data
    np.random.seed(42)
    days = 100
    X = np.array(range(days)).reshape(-1, 1)
    y = 1000 * (1 + 0.1 * np.random.randn(days)) * (1 + 0.05 * np.array(range(days)))
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    return model

# Load or train the model
if os.path.exists(MODEL_PATH):
    try:
        prediction_model = joblib.load(MODEL_PATH)
    except:
        prediction_model = train_prediction_model()
else:
    prediction_model = train_prediction_model()


df3 = pd.read_json(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')


from .utils import fetch_covid_data, prepare_chart_data, get_top_countries
from datetime import datetime

@require_http_methods(["GET"])
def indexPage(request):
    """Main dashboard view with COVID-19 statistics and visualizations"""
    try:
        # Fetch real-time COVID-19 data
        covid_data = fetch_covid_data()
        
        if not covid_data:
            raise Exception("Failed to fetch COVID-19 data")
        
        # Prepare data for the template
        global_data = covid_data['global']
        top_countries = get_top_countries(covid_data['countries'])
        
        # Prepare historical data for charts
        historical_data = {}
        if 'historical' in covid_data and covid_data['historical']:
            historical_data = {
                'labels': list(covid_data['historical'].get('cases', {}).keys())[-30:],  # Last 30 days
                'datasets': [
                    {
                        'label': 'Cases',
                        'data': list(covid_data['historical'].get('cases', {}).values())[-30:],
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'tension': 0.3,
                        'fill': True
                    },
                    {
                        'label': 'Recovered',
                        'data': list(covid_data['historical'].get('recovered', {}).values())[-30:],
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.3,
                        'fill': True
                    },
                    {
                        'label': 'Deaths',
                        'data': list(covid_data['historical'].get('deaths', {}).values())[-30:],
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'tension': 0.3,
                        'fill': True
                    }
                ]
            }
        
        # Prepare map data
        map_data = []
        for country in top_countries:
            map_data.append({
                'code': country.get('countryInfo', {}).get('iso2', '').lower(),
                'name': country['country'],
                'value': country['cases'],
                'deaths': country['deaths'],
                'recovered': country['recovered'],
                'active': country['active']
            })
        
        # Prepare context
        context = {
            'global_data': global_data,
            'top_countries': top_countries[:10],  # Top 10 countries
            'chart_data': historical_data,
            'map_data': json.dumps(map_data),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prediction_days': 7  # Default prediction days
        }
        
        return render(request, 'dashboard.html', context)
    
    except Exception as e:
        print(f"Error fetching COVID data: {e}")
        context = {
            'global_data': {
                'cases': 0,
                'today_cases': 0,
                'deaths': 0,
                'today_deaths': 0,
                'recovered': 0,
                'active': 0,
                'critical': 0,
                'affected_countries': 0,
                'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'top_countries': [],
            'chart_data': None,
            'map_data': '[]',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prediction_days': 7,
            'error': 'Unable to fetch COVID-19 data. Please try again later.'
        }
        
        return render(request, 'dashboard.html', context)


def dashboardPage(request):
    # Load confirmed cases data
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', 
        encoding='utf-8', 
        na_values=None
    )
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
    barPlotData = confirmedGlobal[['Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData.columns = ['Country/Region', 'values']
    barPlotData = barPlotData.sort_values(by='values', ascending=False)
    barPlotVals = barPlotData['values'].values.tolist()
    countryNames = barPlotData['Country/Region'].values.tolist()
    dataForMap = mapDataCal(barPlotData, countryNames)
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, countryNames)
    showMap = "True"
    context = {'countryNames': countryNames, 'barPlotVals': barPlotVals,
               'totalCount': totalCount, 'dataForMap': dataForMap, 'showMap': showMap, 'dataForheatMap': dataForheatMap, 'dateCat': dateCat}
    return render(request, 'dashboard.html', context)

InputCovid = []
welcomeResponse = []

def chatbotPage(request):
    """Render the dedicated chatbot page"""
    return render(request, 'chatbot.html')

@csrf_exempt
def chatBot(request):
    if request.method == "POST":
        user_message = request.POST.get('message', '').lower().strip()
        
        # Load FAQ data
        try:
            df = pd.read_csv('cdc_qa.csv')
        except Exception as e:
            return JsonResponse({'response': "I'm having trouble accessing the knowledge base. Please try again later."})
        
        # Predefined responses
        welcome_responses = [
            "Hello! How can I help you with COVID-19 information today?",
            "Hi there! I'm here to provide COVID-19 information. What would you like to know?",
            "Welcome! Ask me anything about COVID-19."
        ]
        
        bye_responses = [
            "Goodbye! Stay safe and take care!",
            "Bye! Remember to follow health guidelines.",
            "Take care! Feel free to come back with more questions."
        ]
        
        # Check for greeting
        greetings = ["hello", "hi", "hey", "greetings", "what's up"]
        if any(greeting in user_message for greeting in greetings):
            return JsonResponse({'response': random.choice(welcome_responses)})
            
        # Check for goodbye
        goodbyes = ["bye", "goodbye", "see you", "take care"]
        if any(goodbye in user_message for goodbye in goodbyes):
            return JsonResponse({'response': random.choice(bye_responses)})
        
        # Process COVID-19 related questions
        try:
            # Initialize and fit the vectorizer
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(df['Questions'].values.astype('U'))
            
            # Transform user input
            user_tfidf = vectorizer.transform([user_message])
            
            # Calculate similarities
            similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
            
            # Get the most similar question
            best_match_idx = similarities.argmax()
            best_similarity = similarities[best_match_idx]
            
            # Set a similarity threshold (adjust as needed)
            if best_similarity > 0.2:  # 20% similarity threshold
                response = df.iloc[best_match_idx]['Answers']
            else:
                response = "I'm not sure I understand. Could you rephrase your question? Here are some things you can ask:\n"
                response += "- What are the symptoms of COVID-19?\n"
                response += "- How does COVID-19 spread?\n"
                response += "- What are the prevention measures for COVID-19?"
                
            return JsonResponse({'response': response})
            
        except Exception as e:
            return JsonResponse({'response': "I'm having trouble processing your request. Please try again later."})
    
    # If not a POST request, return an empty response
    return JsonResponse({'response': 'Invalid request method'})

def mapDataCal(barPlotData, countryNames):

    dataForMap = []

    for i in countryNames:
        try:
            tempdf = df3[df3['name'] == i]
            temp = {}
            temp["code3"] = list(tempdf['code3'].values)[0]
            temp["name"] = i
            temp["value"] = barPlotData[barPlotData['Country/Region']
                                        == i]['values'].sum()
            temp["code"] = list(tempdf['code'].values)[0]
            dataForMap.append(temp)
        except:
            pass
    return dataForMap


def getHeatMapData(confirmedGlobal, countryNames):
    df3 = confirmedGlobal[list(
        confirmedGlobal.columns[1:2])+list(list(confirmedGlobal.columns.values)[-6:-1])]
    dataForheatMap = []
    for i in countryNames:
        try:
            tempdf = df3[df3['Country/Region'] == i]
            temp = {}
            temp["name"] = i
            temp["data"] = [{'x': j, 'y': k} for j, k in zip(
                tempdf[tempdf.columns[1:]].sum().index, tempdf[tempdf.columns[1:]].sum().values)]
            dataForheatMap.append(temp)
        except:
            pass
    dateCat = list(list(confirmedGlobal.columns.values)[-6:-1])
    # print("dateCat",dateCat)
    # print("dataForheatMap",dataForheatMap)
    return dataForheatMap, dateCat


def singleCountry(request):
    countryName = request.POST.get('countryName')
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)
    totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
    barPlotData = confirmedGlobal[[
        'Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData.columns = ['Country/Region', 'values']
    barPlotData = barPlotData.sort_values(by='values', ascending=False)
    barPlotVals = barPlotData['values'].values.tolist()
    countryNames = barPlotData['Country/Region'].values.tolist()
    showMap = "False"
    countryDataSingle = pd.DataFrame(
        confirmedGlobal[confirmedGlobal['Country/Region'] == countryName][confirmedGlobal.columns[4:-1]].sum()).reset_index()
    countryDataSingle.columns = ['country', 'values']
    countryDataSingle['lagVal'] = countryDataSingle['values'].shift(
        1).fillna(0)
    countryDataSingle['incrementVal'] = countryDataSingle['values'] - \
        countryDataSingle['lagVal']
    countryDataSingle['rollingMean'] = countryDataSingle['incrementVal'].rolling(
        window=4).mean()
    countryDataSingle = countryDataSingle.fillna(0)
    datasetsForLine = [{'yAxisID': 'y-axis-1', 'label': 'Daily Cumulated Data', 'data': countryDataSingle['values'].values.tolist(), 'borderColor':'#03a9fc', 'backgroundColor':'#03a9fc', 'fill':'false'},
                       {'yAxisID': 'y-axis-2', 'label': 'Rolling Mean 4 days', 'data': countryDataSingle['rollingMean'].values.tolist(), 'borderColor':'#fc5203', 'backgroundColor':'#fc5203', 'fill':'false'}]
    axisValue = countryDataSingle.index.tolist()
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, countryNames)
    context = {'countryNames': countryNames, 'axisValue': axisValue, 'countryName': countryName, 'barPlotVals': barPlotVals,
               'totalCount': totalCount, 'showMap': showMap, 'datasetsForLine': datasetsForLine, 'dataForheatMap': dataForheatMap, 'dateCat': dateCat}
    return render(request, 'dashboard.html', context)


def prediction(request):
    selectedCountry = "Worldwide"
    imagesAppend = "/static/img/totalp.png"
    imagesAppendR = "/static/img/totalp.png"
    
    try:
        confirmedGlobal = pd.read_csv(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', encoding='utf-8', na_values=None)
        totalCount = confirmedGlobal[confirmedGlobal.columns[-1]].sum()
        barPlotData = confirmedGlobal[[
            'Country/Region', confirmedGlobal.columns[-1]]].groupby('Country/Region').sum()
        barPlotData = barPlotData.reset_index()
        barPlotData.columns = ['Country/Region', 'values']
        barPlotData = barPlotData.sort_values(by='values', ascending=False)
        barPlotVals = barPlotData['values'].values.tolist()
        countryNames = barPlotData['Country/Region'].values.tolist()
    except Exception as e:
        # Fallback data if external API fails
        countryNames = ["US", "India", "Brazil", "Russia", "France", "Turkey", "UK", "Italy", "Argentina"]
        print(f"Error loading COVID data: {e}")
    
    choosedCountry = ["india","argentina","italy","uk","us","france","turkey", "russia", "brazil"]
    if request.method == "POST":
        selectedCountry = request.POST.get('drop1')
        newSelectedCountry = selectedCountry.lower()
        if newSelectedCountry not in choosedCountry:
            imagesAppend = "/static/img/turkeyp.png"
            imagesAppendR = "/static/img/turkeyp.png"
        else:
            imagesAppend = "/static/img/" + newSelectedCountry + "p.png"
            imagesAppendR = "/static/img/" + newSelectedCountry + "r.png"
        return render(request,'prediction.html',{'Country':countryNames,'selectedCountry':newSelectedCountry,'imagesAppend':imagesAppend,'imagesAppendR':imagesAppendR})

    return render(request,'prediction.html',{'Country':countryNames,'selectedCountry':selectedCountry,'imagesAppend':imagesAppend,'imagesAppendR':imagesAppendR})


def vaccination(request):
    imageLeft = ''
    imageRight = ''
    estimatedGraph = False

    if request.method == 'POST':
        if 'dailyv' in request.POST:
            imageLeft = '/static/img/daily1.png'
            imageRight = '/static/img/daily2.png'
        elif 'dailyp' in request.POST:
            imageLeft = '/static/img/dailyp1.png'
            imageRight = '/static/img/dailyp2.png'
        elif 'peoplev' in request.POST:
            imageLeft = '/static/img/people1.png'
            imageRight = '/static/img/people2.png'
        elif 'peoplep' in request.POST:
            imageLeft = '/static/img/peoplep1.png'
            imageRight = '/static/img/peoplep2.png'
        elif 'totalc' in request.POST:
            imageLeft = '/static/img/total1.png'
            imageRight = '/static/img/total2.png'
        elif 'estimate' in request.POST:
            estimatedGraph = True        
        else:
            print("Nothing Clicked")

    if imageLeft == '':
        imageLeft = False
    if imageRight == '':
        imageRight = False

    return render(request,'vaccination.html', {"imageleft":imageLeft,"imageright":imageRight,"estimatedgraph":estimatedGraph})