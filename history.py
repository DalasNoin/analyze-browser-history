import pandas as pd
import numpy as np
from urllib.parse import urlparse
from datetime import datetime,timedelta

class History:
    def __init__(self,path_to_hist : str):
        dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

        self.hist = pd.read_csv("hist.txt",
                           "|",
                           parse_dates = ["date"],
                           date_parser=dateparse,
                           names = ["date","url"],
                           header = None,
                           error_bad_lines = False)
        
        parser = lambda u: urlparse(u).netloc
        self.hist["url"] = self.hist["url"].apply(parser)
        self.hist["duration"] = self.get_duration()
        self.hist["date_only"] = self.get_date_only()
        
    def get_duration(self):
        Series = pd.Series(np.array(self.hist["date"][:-1])-np.array(self.hist["date"][1:]))
        Series[Series>timedelta(minutes=15)] = timedelta(minutes=5)
        return Series
    
    def get_date_only(self):
        return self.hist["date"].apply(lambda x: x.date())
    
    def get_total_duration(self,date,url = None,divide_seconds_by = 3600):
        if url == None:
            try:
                return self.hist.groupby(["date_only"]).get_group((date))["duration"].sum().total_seconds()/divide_seconds_by
            except Exception:
                return 0.0
        else:
            try:
                return self.hist.groupby(["date_only","url"]).get_group((date,url))["duration"].sum().total_seconds()/divide_seconds_by
            except Exception:
                return 0.0
            
    def get_n_days(self,n=10):
        dates = []
        for i in range(0,n):
            dates.append((datetime.now() - timedelta(days=i)).date())
        return dates
    
    def get_time_for(self,n=10,url=None):
        time_spend=[]
        for date in self.get_n_days(n=n):
            time_spend.append(self.get_total_duration(date,url))
        return time_spend
    
    def duration_by_urls(self):
        df = self.hist.groupby(["url"])["duration"].sum()
        seconds = df.apply(lambda x:x if type(x) is int else x.total_seconds())
        top = seconds.sort_values(ascending=False)
        return top

import matplotlib.pyplot as plt

path = "hist.txt"

def plot_url(history,url,n=10):
    fig,ax = plt.subplots()
    ax.bar(np.arange(n),history.get_time_for(n=n,url=url))
    ax.grid()
    ax.set_xlabel("Date = Today - x")
    ax.set_ylabel("Hours")
    ax.set_title(url)
    fig.savefig(url[:-4]+".pdf",format="pdf")

def example_usage():
    history = History(path)
    #generate pie chart for top10 urls visited
    fig,ax = plt.subplots()
    fig.set_size_inches(8,5)
    ax.set_title("Most Visited Urls")
    ax.pie(history.duration_by_urls()[:10],labels = history.duration_by_urls().index[:10])
    fig.savefig("piecharttop10.pdf",format="pdf")

    #generate bar chart for time spend on youtube over 10 days
    plot_url(history,"www.youtube.com")
    
if __name__ == "__main__":
    example_usage()











