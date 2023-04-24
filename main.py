import pyodide_http
pyodide_http.patch_all() 

import re

import js
from pyodide.ffi import create_proxy

from astroquery.mast import Observations

hinput = Element("input")
hinfo = Element("infotext")
hccheck = Element("coordcheckbox")

re_table_url = re.compile('<td>(http.*?)</td>')
def table_url_sub(m):
    return '<td><a href="' + m.group(1) + '">LINK</a></td>'
    
re_table_masturl = re.compile('<td>(mast:HST.*?)</td>')
def table_masturl_sub(m):
    masturl =  m.group(1)
    suburl = masturl.replace('mast:HST', 'https://mast.stsci.edu/portal/Download/file/HST')
    return '<td><a href="' + suburl + '">LINK</a></td>'

@create_proxy
def query(qrystr):
    # create_proxy turns it into js for use with setTimeout - see below
    if len(qrystr) == 0:
        hinfo.element.innerHTML = 'No search string entered'
        return
    if hccheck.element.checked:
        result = Observations.query_region(qrystr)
    else:
        result = Observations.query_object(qrystr)

    hinfo.element.innerHTML = f'Search complete, {len(result)} observations found.'

    htable = Element("resulttable")
    result.remove_column('s_region')
    
    tabstr = '\n'.join(result.pformat_all(html=True, tableid='resulttable'))
    #htable.element.outerHTML = tabstr    

    sub1 = re_table_url.subn(table_url_sub, tabstr)[0]
    #htable.element.outerHTML = sub1
    sub2 = re_table_masturl.subn(table_masturl_sub, sub1)[0]
    htable.element.outerHTML = sub2

def invoke_query():
    # This is a separate function from query because if you don't do this,
    # the next line doesn't work - it seems the element doesn't get updated
    # until the function ends, so why have to asynchronously invoke the 
    # query function
    hinfo.element.innerHTML = 'Running search...'

    # replace this with something webworker-y when that's supported by pyscript
    js.setTimeout(query, 1, hinput.element.value)
