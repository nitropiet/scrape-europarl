#!/usr/bin/env python
"""
    Requirements:
    - requests (installation: pip install requests)
    - lxml (installation: pip install lxml)
"""

import requests
import urllib
import lxml.html
import os
from pathlib import Path
import pdftotext
import re
import sys
from datetime import datetime
import configparser

debug = False

def re_search(findtext, intext, n)->str:
    '''Searches for text, and retrieves n words either side of the text, which are retuned seperatly'''

    if debug:
        print("Searching for: " + findtext)
        print("In: " + intext)
    pattern = r"((\W*\w+){0," + str(n) + "}\W*" + findtext + r"\W*(\W*\w+){0," + str(n) + "})"
    #word = r"\W*\w+?"
    if debug:
        print("14:" + str(datetime.now()))    
    try:
        #match = re.search(r'({}\W*{}\W*{})'.format(word*n,findtext,word*n), intext).groups()
        match = re.search(pattern, intext).groups()[0]
        if debug:
            print("18:" + str(datetime.now()))    
    except Exception as ex:
        print(ex)
        print("Pattern: " + pattern)
        print("Searching for: " + findtext)
        print("In: " + intext)
        sys.exit(1)

    if debug:
        print("15:" + str(datetime.now()))
    if match:
        #result = list(filter(None, match))
        result = match
        if debug:
            print("16:" + str(datetime.now()))
        return result
        #return ' '.join(result)
    else:
        if debug:
            print("17:" + str(datetime.now()))
        return ''
#,  flags=re.IGNORECASE


class ScrapeProcess:
    def ScrapeProcess(self, processName, processParams):
        self.ProcessName = processName
        self.ProcessParams = processParams

    def Process(self):
        base_url = "https://www.europarl.europa.eu/committees/en/documents/search?committeeMnemoCode=&textualSearchMode=TITLE&textualSearch=&documentTypeCode=&reporterPersId=&procedureYear=&procedureNum=&procedureCodeType=&peNumber=&sessionDocumentDocTypePrefix=&sessionDocumentNumber=&sessionDocumentYear=&documentDateFrom={datefrom}&documentDateTo={dateto}&meetingDateFrom=&meetingDateTo=&performSearch=true&term=9&page={i}"

        
        i=-1
        downloaded_file_count = 0
        keyword_hit_count = 0
        while True:
            i = i + 1
            self.ProcessParams["pageid"] = i
            formatted_url = urllib.parse.quote_plus(base_url.format_map(self.ProcessParams))
            content = urllib.request.urlopen(formatted_url).read()
            htmldoc = lxml.html.fromstring(content)
            #print('  Searching on results page number: ' + str(i))
            #next page

            
            #no results
            result_error = htmldoc.find_class(self.ProcessParams['NoResultHTMLClass'])
            if result_error:
                if 'No result - please modify search' in result_error[0].text_content():
                    print("No documents found")
                    break
            if i > 100:
                print("More than " + str(i) + " pages deep, cancelling out of concern for your health")
                break

            for doc_hdr in htmldoc.find_class(self.ProcessParams['ResultItemHTMLClass']):
                doc_title = doc_hdr.find_class('erpl_document-title')[0].find_class('t-item')[0].text_content()
                doc_date = doc_hdr.find_class('erpl_document')[0].find_class('erpl_document-header')[0].find_class('erpl_document-subtitle-fragment')[0].text_content()
                hrefs = doc_hdr.xpath(".//a[@href[contains(., 'pdf')]]")
                #print("    " + doc_title + "    " + doc_date)
                found_words = False
                words_found = ''
                file_location = ''
                for d in hrefs:
                    if debug:
                        print("1:" + str(datetime.now()))
                    file_url = d.get('href')
                    file_name = os.path.join(os.getcwd(),'data' + '\\' + "tmp" + '\\' + file_url.split('/')[-1])
                    if debug:
                        print("2:" + str(datetime.now()))
                    downloaded_file = self.download_file(file_name, file_url)
                    if debug:
                        print("3:" + str(datetime.now()))
                    #print("      Downloaded: " + downloaded_file)
                    downloaded_file_count = downloaded_file_count + 1
                    if debug:
                        print("4:" + str(datetime.now()))
                    retval = self.checkforfile(downloaded_file, self.ProcessParams['Keywords'])
                    if debug:
                        print("5:" + str(datetime.now()))
                    if retval != '':
                        #print("Found: " + retval)
                        keyword_hit_count = keyword_hit_count + 1
                        found_words = True
                        if file_location == '':
                            file_location = downloaded_file
                        else:
                            file_location = file_location + ';' + downloaded_file
                        if words_found == '':
                            words_found = retval
                        else:
                            words_found = words_found + ';' + retval
                    else: 
                        #if no keyword matches found then delete file
                        os.remove(downloaded_file)
                
                if found_words:
                    strfound = str(words_found.encode('ascii', 'replace'))
                    #if keyword matches found, log data
                    #print("\n\n" + str(datetime.now()) + "\n\n")
                    print("\n\n")
                    print("Document Titled: " + doc_title)
                    print("Document Date: " + doc_date)
                    print("Found " + strfound)
                    print("Saved location " + downloaded_file)
                    

        #print("Downloaded "+ str(downloaded_file_count) + " file(s)")
        #print("Found "+ str(keyword_hit_count) + " match(es)")


    def download_file(self, file_name, url):
    #make sure folder exists before downloading
        folder_name = file_name.replace(file_name.split('\\')[-1], '')
        Path(folder_name).mkdir(parents=True, exist_ok=True)

      #NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
        return file_name


    def checkforfile(filename, keywordlist):

        found_keywords = ''

        # Load your PDF
        with open(filename, "rb") as f:
            if debug:
                print("6:" + str(datetime.now()))
            pdf = pdftotext.PDF(f)
            if debug:
                print("7:" + str(datetime.now()))
        # Read all the text into one string
        #doc_text = "\n\n".join(pdf)
        for keyword in keywordlist.split(','):
            if debug:
                print("8:" + str(datetime.now()) + "    keyword: "+ keyword)
            pagenum = 0
            for doc_text in pdf:
                pagenum = pagenum + 1
                if debug:
                    print("9:" + str(datetime.now()) + "     page:" + str(pagenum))
                # try to find a match
                startpos = 0
                keywordlen = 0
                while startpos != -1:
                    if debug:
                        print("10:" + str(datetime.now()))
                    startpos = doc_text.lower().find(keyword.lower(), startpos + keywordlen + 1)
                    if debug:
                        print("11:" + str(datetime.now()))
                    if startpos >= 0:
                        foundval = doc_text[startpos:startpos+len(keyword)]
                        keywordlen = len(foundval)
                        if debug:
                            print("12:" + str(datetime.now()))
                        match_results = re_search(foundval, doc_text[max(0,startpos-250):min(startpos+250, len(doc_text))], 5)
                        if debug:
                            print("13:" + str(datetime.now()))
                        if match_results:
                            match_results = match_results.replace(chr(13)," ").replace(chr(2)," ").replace(chr(10)," ").replace("  ", " ").strip(" ")
                            built_string = foundval + " in [" + match_results + ']' + " on (Page " + str(pagenum) + ")"
                            if found_keywords == '':
                                found_keywords = built_string
                            else:
                                found_keywords = '\n'.join([found_keywords, built_string])
                    
        return found_keywords


def main():
    mycfg = configparser.ConfigParser(allow_no_value=True)
    mycfg.optionxform=str
    mycfg.read('config\\config.ini')

    for prcs in mycfg['Processes']:
        try:
            if not mycfg['Processes'].getboolean(prcs, fallback=True):
                #skip process
                print ("Skipping Process " + prcs)
                next
        except:
            pass
        if not mycfg.has_section(prcs):
            #section does not exist
            print ("Process " + prcs + " does not exists")
            next
        
        print("Processing " + prcs)
        #get section
        myparams = dict(mycfg[prcs])
        scraper = ScrapeProcess(prcs, myparams)

        scraper.Process()
        


#documents
main()
print("Done")


