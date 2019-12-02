#import Required Libraries
from builtins import str
import re
import os
import urllib.request, urllib.parse, urllib.error
import unicodedata
import MySQLdb as db
from whoosh import qparser, query
from whoosh.fields import *
from bs4 import BeautifulSoup
from whoosh.query import Term
from whoosh.lang.porter import stem
from whoosh.analysis import StandardAnalyzer
from whoosh.index import open_dir, create_in
from whoosh.qparser import QueryParser, MultifieldParser
from datetime import datetime
from config import *
# Give Values of the Database Environment Variables
HOST = 'localhost'
USER = DB_USER
PASSWORD = DB_PASS
DB = DB
# check_index variable is used to check whether the index tables are already present or not in the system
check_index = None

# Extracting present time from datetime class
present_time = datetime.now()
date_f = '%Y-%m-%d %H:%M:%S'

# if index folder is not exist then create the index folder and define schema
# and create index tables using the schema and set check_index variable value to 1
if not os.path.exists("index"):
	os.mkdir("index")
	schema = Schema(title=TEXT(stored=True,field_boost=2.0), VideoId=ID(stored=True), outline=TEXT(analyzer=analysis.StemmingAnalyzer(),stored=True,spelling=True),tags=KEYWORD(stored=True), foss=KEYWORD(stored=True), updated=TEXT(stored=True))
	ix = create_in("index", schema)
	check_index = 1

#open the index directory and initialize the writer object of writer class
ix = open_dir("index")
searcher=ix.searcher()
parser = QueryParser("VideoId", schema=ix.schema)

 

try:
	
	# Establish the database connection and invoke cursor module
	connection = db.Connection(host=HOST, user=USER, passwd=PASSWORD, db=DB) 
	dbhandler = connection.cursor()
	
	# Query to get the required fields from three tables those are 
	# creation_tutorialdetail, creation_tutorialresource, 
	# creation_tutorialcommoncontent and execute the query and store the results
	query = """SELECT creation_tutorialdetail.tutorial,
creation_tutorialresource.outline,creation_tutorialresource.timed_script,
creation_tutorialcommoncontent.keyword,creation_tutorialdetail.id,
creation_tutorialresource.created,creation_tutorialresource.updated,
creation_fosscategory.foss FROM creation_tutorialdetail INNER JOIN 
creation_tutorialresource ON creation_tutorialdetail.id = 
creation_tutorialresource.tutorial_detail_id INNER JOIN 
creation_tutorialcommoncontent ON 
creation_tutorialcommoncontent.tutorial_detail_id=creation_tutorialdetail.id 
INNER JOIN creation_fosscategory ON 
creation_fosscategory.id=creation_tutorialdetail.foss_id where 
creation_tutorialresource.language_id=22 AND 
(creation_tutorialresource.status=1 OR creation_tutorialresource.status=2)""" 
	dbhandler.execute(query)
	result = dbhandler.fetchall()
	##############################################################################
	
	# Variables used for displaying the no.of documents newly created and updated documents
	cr_count = 0
	up_count = 0
	
	# Loop over all the results obtained
	for item in result:
		update_difference = None
		not_found = None
		#print check_index, not_found, update_difference
		# Calculate the difference between present date and created and updated fields in the database
		if not check_index:
			video_id = str(item[4])
			video_q = parser.parse(video_id)
			sresult = searcher.search(video_q)
			not_found = True
			if sresult.scored_length() > 0:
				for hit in sresult:
					if hit["VideoId"] == video_id:
						not_found = False
						update_difference = datetime.strptime(hit["updated"], date_f) - item[6]
						update_difference = update_difference.days
		#print check_index, not_found, update_difference
		# if the created date or updated date is 1 then that means the video is recently added or modified 
		if update_difference or not_found or check_index:
			writer = ix.writer()
			#Extract the required fields and store in variables
			title=item[0]
			script=""
			text=""
			outline=item[1]
			
			# Split the given text by non-alphanumeric character and remove 1 or 2 letter words
			# and Join those words. It may take some comparable time but to store clean representation we used this
			# and it doesn't effect the search performance (it may be fast compared to other)  
			splitter=re.compile('[^a-z,A-Z,0-9,_,+,#,@,&,$]*')
			words=[s.lower() for s in splitter.split(outline)
				if len(s)>2 and len(s)<20]
			outline = ' '.join(words)
			words = item[3].replace(', ', ' ').replace(',', ' ').strip()
			word_o=[s.lower() for s in splitter.split(words)
				if len(s)>2 and len(s)<20]
			keywords = ' '.join(word_o)
			words=[s.lower() for s in splitter.split(item[7])
				if len(s)>0 and len(s)<20]
			foss = ' '.join(words)
			words=[s.lower() for s in splitter.split(title)
				if len(s)>0 and len(s)<20]
			title = ' '.join(words)
			
			# And converting the obtained text to unicode (Whoosh only accepts unicode)
			text = text.strip()
			title = str(title)
			videoid = str(item[4])
			keywords = keywords.strip()
			foss = foss.strip()
			outline = outline.strip()
			updated = str(item[6])
			
			
			try:
				# If the created date is more than one then that means we need to update the document
				# So then delete the previous document by videoid and add the document and increment
				# count of updated documents
				if update_difference:
					print(("Updating %s for indexing" % title))
					writer.delete_by_term("VideoId", videoid)
					up_count=up_count+1
				# if index table is not present then add all the documents to index tables
				# Else add the document to the index table ( Newly added Video)
				else:
					print(("Adding %s for indexing" % title))
					cr_count=cr_count+1
				writer.add_document(title=title, VideoId=videoid, tags=keywords, outline=outline, foss=foss, updated=updated)
				
				# Finally Commit() save the added documents to index
				writer.commit()
			except Exception as e:
				print(("Write exception: ", e))
				break
	
	# Print the no.of documents added/ Updated
	print((cr_count,"documents Added and ",up_count," documents Updated"))  
		
# Handling Exception		
except Exception as e:
	print(e)

