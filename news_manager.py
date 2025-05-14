import requests

def get_news(api_key, country_code=None, topic=None):
    """
    Get news using NewsData.io API
    """
    try:
        if topic:
            # For topic-based news
            url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={topic}&language=en"
        else:
            # For country-based news
            url = f"https://newsdata.io/api/1/news?apikey={api_key}&country={country_code}&language=en"

        response = requests.get(url)
        news_data = response.json()

        if response.status_code == 200 and news_data.get('status') == 'success':
            articles = []
            for article in news_data['results'][:5]:  # Get top 5 articles
                title = article.get('title', '')
                description = article.get('description', '')
                if title and description:
                    articles.append(f"Title: {title}\nDescription: {description}\n")
            return articles
        return None
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return None

# Country code mapping for NewsData.io
country_code_mapping = {
    'india': 'in',
    'united states': 'us',
    'united kingdom': 'gb',
    'australia': 'au',
    'canada': 'ca',
    'germany': 'de',
    'france': 'fr',
    'italy': 'it',
    'japan': 'jp',
    'russia': 'ru',
    'china': 'cn',
    'brazil': 'br',
    'mexico': 'mx',
    'spain': 'es',
    'south korea': 'kr'
} 