from flask import Flask, render_template, request
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/keyword", methods=['POST', 'GET'])
def keyword():

    keyword = request.form.get('keyword')

    if not keyword:
        return render_template('keyword_search.html', error="No keyword provided.")

    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list = [keyword]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m')

    # Get interest over time
    trends = pytrends.interest_over_time()


    # Check if trends data is available
    if trends.empty:
        return render_template('keyword_search.html', error="No trend data found for the given keyword.")

    plt.figure(figsize=(12, 6))
    plt.plot(trends.index, trends[keyword])
    plt.xlabel('Date', fontsize=24)
    plt.ylabel('Interest Over Time', fontsize=24)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Set major ticks to each month
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # Generate the plot
    plt.xticks(rotation=45, ha='right', fontsize=18)  # Rotate x-axis labels for readability
    plt.yticks(fontsize=18)
    plt.tight_layout()  # Adjust layout for better fit

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    return render_template('keyword_search.html', plot_url=plot_url, keyword=keyword)




@app.route("/trends", methods=['POST', 'GET'])
def trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    trending = pytrends.trending_searches(pn='united_states')
    trending_list = []
    if not trending.empty:
        for trend in trending[0]:
            trending_list.append(trend)
    return render_template('trends.html', trending_list=trending_list)


if __name__ == "__main__":
    app.run(debug=True)


