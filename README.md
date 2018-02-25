Code for running integrated UI in qatar.

Currently, the UI contains: figure search.

3. Other than django and python 2.7, following python modules:
openpyxl,solrpy. 

to run, edit web/params: change 

SOLR_FIGURE_URL = <the url where the Solr server for figure search is running> 

run python manage.py runserver <hostname:port>

