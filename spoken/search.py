# import Required Libraries
# Standard Library
import os

# Third Party Stuff
from django.conf import settings
from whoosh import qparser
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.lang.porter import stem

# Spoken Tutorial Stuff
from creation.models import TutorialResource


# Function used to search the query in the index table and display search results and related searches for the user

def search_for_results(userquery, corrected_flag=True):
    try:
        if os.path.exists(settings.SEARCH_INDEX_DIR):
            # open index directory and create object for searcher class
            index_reference = open_dir(settings.SEARCH_INDEX_DIR)
            searcher = index_reference.searcher()

            # Applying stemming on the userquery
            stem(userquery)

            # OrGroup.factory - which is useful better for giving relavance rather
            # than naive term frequency of the words in the query
            og = qparser.OrGroup.factory(0.9)

            # initializing Multifield Parser for searching in the multiple fields
            queryparser = qparser.MultifieldParser(
                ["tags", "foss", "title", "outline"], schema=index_reference.schema, group=og)

            # These Plugins will remove the ability of the user to specify fields to search
            queryparser.remove_plugin_class(qparser.FieldsPlugin)

            # To remove the ability to search for wildcards, which can be harmful to query performance
            queryparser.remove_plugin_class(qparser.WildcardPlugin)

            # can specify a fuzzy term by adding a ~ followed by an optional maximum edit distance (Ex : jav~1)
            queryparser.add_plugin(qparser.FuzzyTermPlugin())

            # Parse the Given Query
            q = queryparser.parse(userquery)

            # For Correcting Spelling with maximum edit distance 3. More than 3 It may affect the performance.
            corrected = searcher.correct_query(q, userquery, maxdist=3)

            # if the corrected query is not matched with the parsed query then it will ask for Did you mean option
            # if the user Entered the query is equal to the suggested query then it will search for the suggested query
            # else the original query of the is user is searched
            corrected_string = None
            if corrected_flag:
                if corrected.query != q:
                    corrected_string = corrected.string

            results = searcher.search(q, terms=True, limit=None)
            ##############################################################################################

            # printing the no.of videos found and their title of the video
            print("%d Videos Found for %s " % (results.scored_length(), userquery))
            if (results.has_matched_terms() and results.scored_length() > 0):
                collection = []
                for hit in results:
                    row = TutorialResource.objects.filter(
                        tutorial_detail_id=hit['VideoId'], language__name='English').first()
                    collection.append(row)
                return collection, corrected_string
            else:
                return None, corrected_string

    # finally close the searcher object
    finally:
        searcher.close()
    return None, None
