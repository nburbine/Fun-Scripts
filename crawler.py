#!/usr/bin/python -u
#
# Nathaniel Burbine and Qiaozhi Zheng
# CS3700 Spring '16
# Project 4
#

import socket
import sys
import Queue

rootpage = '/fakebook/'
    
# Sends a GET request to given URL. Returns full response
def GET(url, csrftoken='', sessionid=''):
    # reset the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('fring.ccs.neu.edu', 80))
    
    # check given args to format GET request
    if len(csrftoken)+len(sessionid)>0:
        request = ('GET '+url+' HTTP/1.1\r\n'
        'Host: fring.ccs.neu.edu\r\n'
        'Connection: keep-alive\r\n'
        'Cookie: csrftoken='+csrftoken+'; sessionid='+sessionid+'\r\n'
        '\r\n')
    else:
        request = ('GET '+url+' HTTP/1.1\r\n'
        'Host: fring.ccs.neu.edu\r\n'
        'Connection: keep-alive\r\n'
        '\r\n')
    
    # send request
    try:
        sock.sendall(request)
    except:
        print 'send failed'
        exit(0)
    
    # Receive response and parse
    data = sock.recv(4096).split('\r\n')
    
    # handle HTTP codes
    # Redirect
    if '301' in data[0] or '302' in data[0]:
        for line in data:
            if 'Location' in line:
                new_loc = line[10:]
                data = GET(new_loc, csrftoken, sessionid)
    # page not found
    elif '404' in data[0]:
        data = ''
    # good
    elif '200' in data[0]:
        pass
    # retry
    elif '500' in data[0]:
        data = GET(url, csrftoken, sessionid)
    return data
    
# Send a POST to given URL
def POST(url, username, password, csrftoken, sessionid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('fring.ccs.neu.edu', 80))
    
    formdata = ('username='+username+
    '&password='+password+
    '&csrfmiddlewaretoken='+csrftoken)
    content_length = len(formdata)
    post = ('POST '+url+' HTTP/1.1\r\n'+
    'Host: fring.ccs.neu.edu\r\n'+
    'Connection: keep-alive\r\n'+
    'Content-Type: application/x-www-form-urlencoded\r\n'+
    'Content-Length: '+str(content_length)+'\r\n'+
    'Cookie: csrftoken='+csrftoken+'; sessionid='+sessionid+'\r\n'+
    '\r\n'
    +formdata+'\r\n')
    
    try:
        sock.sendall(post)
    except:
        print 'send failed'
        exit(0)
    data = sock.recv(4096).split('\r\n')
    return data
    
# Logs in with given username, password. Returns cookies
def login(username, password):
    response = GET(rootpage)
    csrftoken = ''
    sessionid = ''
    for line in response:
        if 'Set-Cookie' in line:
            token = line[12:]
            if 'csrftoken' in token:
                csrftoken = token[10:].split(';')[0]
            else:
                sessionid = token[10:].split(';')[0]
    response = POST('/accounts/login/', username, password, csrftoken, sessionid)
    for line in response:
        if 'Set-Cookie' in line:
            sessionid = line[12:][10:].split(';')[0]
    return (csrftoken, sessionid)
    
# Takes a html page, returns fakebook urls
def get_urls(html):
    urls = []
    for line in html:
        if '/fakebook/' in line:
            x = line.split('\"')
            for url in [string for string in x if '/fakebook/' in string]:
                if len(url) > len('/fakebook/'):
                    urls.append(url)
    return urls
           
# pulls HTML from full HTTP response           
def html_from_http(data):
    index = 0
    for line in data:
        if '<html>' in line:
            index = data.index(line)
    return data[index:]
    
# returns flag from HTML
def FindFLAG(source):
    flag = ''
    for line in source:
        if 'secret_flag' in line:
            x = line.split('FLAG: ')
            flag = x[1][:64]
    return flag
    
# returns HTML associated with given URL
def get_html(url, csrftoken, sessionid):
    return html_from_http(GET(url, csrftoken, sessionid))
    
# returns a list of urls for given profile's friendslist
def get_friendslist_urls(url, csrftoken, sessionid):
    pages = []
    page = url+'friends/1/'
    pages.append(page)
    data = GET(page, csrftoken, sessionid)
    html = html_from_http(data)
    pages.extend([url for url in get_urls(html) if 'friends' in url])
    pages = set(pages)
    return pages
    
# takes a fakebook profile, returns all html associated    
def crawl_page(url, csrftoken, sessionid):
    all_html = []
    all_html.append(get_html(url, csrftoken, sessionid))
    friendslist_pages = get_friendslist_urls(url, csrftoken, sessionid)
    for page in friendslist_pages:
        html = get_html(page, csrftoken, sessionid)
        all_html.append(html)
    return all_html

# Logs in, crawls, finds flags, prints flags
def main(argv=None):
    global sock
    username = sys.argv[1]
    password = sys.argv[2]
    
    secretflags = []
    
    frontierurls = Queue.Queue(0)
    visitedurls = []
    
    (csrftoken, sessionid) = login(username, password)
    
    # Get first set of profiles
    html = html_from_http(GET(rootpage, csrftoken, sessionid))
    for url in [url for url in get_urls(html) if not 'friends' in url]:
        frontierurls.put(url)
    
    # crawl until exhausted or found 5 flags
    while not frontierurls.empty():
        url = frontierurls.get()
        
        if url in visitedurls or not 'fakebook' in url:
            continue
            
        visitedurls.append(url)
        
        html = crawl_page(url, csrftoken, sessionid)
        # Parse all pages of the profile at URL
        for page in html:
            for url in [url for url in get_urls(page) if not 'friends' in url]:
                frontierurls.put(url)
            flag = FindFLAG(page)
            if len(flag) > 0:
                print flag
                secretflags.append(flag)

        if len(secretflags) == 5:
            break

# run main
if __name__ == '__main__':
    main()