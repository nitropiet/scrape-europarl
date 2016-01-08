import requests
import lxml.html
import os

def download_file(file_name, url):
    #file_name = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return file_name

for i in range(1,1381):
	url = "http://www.europarl.europa.eu/RegistreWeb/search/typedoc.htm?codeTypeDocu=QECR&year=2015&currentPage={0}".format(i)
	html = lxml.html.parse(url)
	title = [i.strip() for i in html.xpath("//div[contains(@class, 'notice')]/p[@class='title']/a/text()")]
	doc = [i.strip() for i in html.xpath("//div[contains(@class, 'notice')]/ul/li/a/@href")]
	q_ref = [i.strip() for i in html.xpath("//div[contains(@class, 'notice')]/div[@class='date_reference']/span[2]/text()")]
	

