# """
#     https://colab.research.google.com/drive/1M4IWS88XN1h2X0Immk9q11MkXw4VmcE4
# """
# from django.conf import settings
# import re
# from urllib.request import urlopen
# from bs4 import BeautifulSoup
# import requests
# from io import BytesIO
# from nltk import word_tokenize
# from scipy import spatial
# import numpy as np
# import requests
# import nltk
# from nltk.corpus import stopwords
# import pickle

# '''
#   Preloaders
# '''
# with open(settings.BASE_DIR+'/static/spoken/embedding/pickled glove 6b 300d.pkl', 'rb') as f:
#     embedding_glove = pickle.load(f)
# stop_words = list(set(stopwords.words('english')))

# def get_links(html_page, url_home):
#   soup = BeautifulSoup(html_page,features="lxml")
#   links = {}
#   for link in soup.findAll('a'):
#     if link.text and link.text not in unwanted :
#       if 'static' in link.get('href'):
#         links[link.text] = link.get('href')
#       else:
#         links[link.text] = url_home+link.get('href')
#   return links


# def encoder_foss(data, p_type):
#   encoded_data = {}
#   if isinstance(data, str):
#     temp = np.zeros(300)
#     for word in word_tokenize(data):
#       word = re.sub('[^A-Za-z0-9]+', ' ', word.lower()).strip()
#       if word and word not in stop_words and not word.isdigit()\
#       and len(word) > 2 and 'http' not in word:
#         try:
#             temp = temp + embedding_glove[word]
#         except KeyError:
#             encoded_data[word] = temp
#     if temp.any():
#       if p_type == 'href':
#         encoded_data[option] = [temp, data[option]]
#       else:
#         encoded_data[data] = [temp, '']
#   else:
#     for option in data:
#       temp = np.zeros(300)
#       count = 0
#       for word in word_tokenize(option):
#         word = re.sub('[^A-Za-z0-9]+', ' ', word.lower()).strip()
#         if word and word not in stop_words and not word.isdigit()\
#         and len(word) > 2 and 'http' not in word:
#           try:
#               temp = temp + embedding_glove[word]
#           except KeyError:
#               encoded_data[word] = temp
#       if temp.any():
#         if p_type == 'href':
#           encoded_data[option] = [temp, data[option]]
#         else:
#           encoded_data[option] = [temp, '']
#   return encoded_data

# def crawler(url_home, url_open):
#   html_page = urlopen(url_open)
#   titles = get_links(html_page, url_home)
#   encoded_data = encoder_foss(titles,'href')
#   return encoded_data

# def get_encoded_keywords(tr_obj):
#   if str(tr_obj.language) == 'English':
#     keywords = tr_obj.outline
#   else:
#     keywords = tr_obj.common_content.keyword
#     keywords = [x.strip().lower() for x in keywords.split(',')]
#     cur_foss = tr_obj.tutorial_detail.foss.foss.lower()
#     if cur_foss in keywords:
#       keywords.remove(cur_foss)
#     if 'scilab' in keywords:
#       keywords.remove('scilab')
#   foss_enc = encoder_foss(keywords, 'normal')
#   return foss_enc

# def alm(tr_obj):
#     foss = tr_obj.tutorial_detail.foss.foss
#     fosses = {
#       'DWSIM'           : dwsim,
#       'DWSIM-3.4'       : dwsim,
#       'eSim'            : esim,
#       'OpenFOAM version 7':openfoam,
#       'OpenModelica'   : openmodellica,
#       'R'               : rsoftware,
#       'Scilab'          : scilab,
#       'QGIS'            : qgis,
#       'Python'          : python,
#       'Python 3.4.3'    : python,
#       'Arduino'         : arduino
#     }
#     if foss in fosses:
#       top_results = fosses[foss](tr_obj)
#       return top_results
#     else:
#       return []
#     return top_results


# def top_results(encoded, fossee_website_encoded):
#   results = [[10000,10000,10000]]
#   for keyword in encoded.keys():
#       for foss_keys in fossee_website_encoded:
#         if [keyword, foss_keys] not in results:
#           euc_dist = spatial.distance.euclidean(encoded[keyword][0], fossee_website_encoded[foss_keys][0])
#           if euc_dist < min(results)[0] and euc_dist > 0 and \
#           isinstance(fossee_website_encoded[foss_keys][1], str):
#             results.append([euc_dist, keyword, foss_keys, fossee_website_encoded[foss_keys][1]])
#   return sorted(results)[0]


# def esim(tr_obj):
#   # Get HTML Content
#   esim = []
#   url_home = 'https://esim.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)

#   # Circuit Simulation  Project
#   url_open = 'https://esim.fossee.in/circuit-simulation-project/completed-circuits'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)
#   esim.append({'head':'Circuit Simulation  Project','data':rec})

#   # Textbook Companion
#   url_open = 'https://esim.fossee.in/completed_books'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)
#   esim.append({'head':'Textbook Companion','data':rec})

#   # Lab Migration
#   url_open = 'https://esim.fossee.in/lab_migration/completed_labs'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)
#   esim.append({'head' : 'Lab Migration','data' :rec})

#   # Circuit Design and Simulation Marathon using eSim
#   url_open = 'https://esim.fossee.in/hackathon/completed-circuits'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)
#   esim.append({'head' : 'Circuit Design and Simulation Marathon','data' : rec})

#   # Mixed Signal Circuit Design and Simulation Hackathon
#   url_open = 'https://esim.fossee.in/mixed-signal-design-marathon/download/completed-circuit'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)
#   esim.append({'head':'Mixed Signal Circuit Design and Simulation','data':rec})

#   # Pspice to kicad converted files
#   url_open = 'https://esim.fossee.in/pspice-to-kicad/list'
#   esim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, esim_encoded)

#   # Completed Pspice to Kicad circuits
#   url_open = 'https://esim.fossee.in/circuit-simulation-project/completed-circuits/pspice-to-kicad'
#   esim_encoded = crawler(url_home, url_open)
#   rec1 = top_results(foss_encoded, esim_encoded)
#   rec_kicad = [rec,rec1]
#   esim.append({'head' : 'Pspice to kicad circuits',
#               'data'  :   sorted(rec_kicad)[0]})
#   return esim

# def dwsim(tr_obj):
#   dwsim = []
#   url_home = 'https://dwsim.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)

#   # Flowsheeting Project
#   url_open = 'https://dwsim.fossee.in/flowsheeting-project/completed-flowsheet'
#   dwsim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, dwsim_encoded)
#   dwsim.append({'head':'Flowsheeting Project','data':rec})

#   # Custom Modeling
#   url_open = 'https://dwsim.fossee.in/custom-model/completed-custom-models'
#   dwsim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, dwsim_encoded)
#   dwsim.append({'head':'Custom Modeling','data':rec})

#   # Textbook Companion
#   url_open = 'https://dwsim.fossee.in/textbook-companion/completed-books'
#   dwsim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, dwsim_encoded)
#   dwsim.append({'head':'Textbook Companion','data':rec})

#   # Lab Migration
#   url_open = 'https://dwsim.fossee.in/lab-migration/completed-labs'
#   dwsim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, dwsim_encoded)
#   dwsim.append({'head':'Lab Migration','data':rec})

#   # Resources
#   url_open = 'https://dwsim.fossee.in/lab-migration/completed-labs'
#   dwsim_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, dwsim_encoded)
#   dwsim.append({'head':'Extra Resources','data':rec})

#   return dwsim

# def openfoam(tr_obj):
#   openfoam = []
#   url_home = 'https://cfd.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)
  
#   #Case Study Project
#   url_open = 'https://cfd.fossee.in/case-study-project/completed-case-studies'
#   openfoam_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openfoam_encoded)
#   openfoam.append({'head':'Case Study Project','data':rec})

#   # Textbook Companion
#   url_open = 'https://cfd.fossee.in/textbook-companion/completed-books'
#   openfoam_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openfoam_encoded)
#   openfoam.append({'head':'Textbook Companion','data':rec})

#   # Lab Migration
#   url_open = 'https://cfd.fossee.in/lab-migration/completed-labs'
#   openfoam_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openfoam_encoded)
#   openfoam.append({'head':'Lab Migration','data':rec})

#   # Research Migration Project
#   url_open = 'https://cfd.fossee.in/research-migration-project/completed-research-migration'
#   openfoam_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openfoam_encoded)
#   openfoam.append({'head':'Research Migration Project','data':rec})

#   return openfoam

# def openmodellica(tr_obj):
#   openmodellica = []
#   url_home = 'https://om.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)
  
#   # Flowsheeting Project
#   url_open = 'https://om.fossee.in/chemical/flowsheeting-project/completed-flowsheet'
#   openmodellica_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openmodellica_encoded)
#   openmodellica.append({'head':'Flowsheeting Project','data':rec})
  
#   # Power System Simulation Project
#   url_open = 'https://om.fossee.in/powersystems/pssp/completed-pssp'
#   openmodellica_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openmodellica_encoded)
#   openmodellica.append({'head':'Power System Simulation Project','data':rec})

#   # Textbook Companion
#   url_open = 'https://om.fossee.in/textbook-companion/completed-books'
#   openmodellica_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, openmodellica_encoded)
#   openmodellica.append({'head':'Textbook Companion','data':rec})

#   return openmodellica


# def scilab(tr_obj):
#   scilab = []
#   url_home = 'https://scilab.in'
#   foss_encoded = get_encoded_keywords(tr_obj)
  

#   # Scilab Textbook Companion
#   url_open = 'https://scilab.in/Completed_Books'
#   scilab_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, scilab_encoded)
#   scilab.append({'head':'Scilab Textbook Companion','data':rec})

#   # XCOS Textbook Companion
#   url_open = 'https://scilab.in/xcos-textbook-companion/completed-books'
#   scilab_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, scilab_encoded)
#   scilab.append({'head':'XCOS Textbook Companion','data':rec})

#   # Lab Migration
#   url_open = 'https://scilab.in/lab_migration/completed_labs'
#   scilab_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, scilab_encoded)
#   scilab.append({'head':'Lab Migration','data':rec})

#   # FOSSEE Scilab Toolbox
#   url_open = 'https://scilab.in/fossee-scilab-toolbox'
#   scilab_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, scilab_encoded)
#   scilab.append({'head':'FOSSEE Scilab Toolbox','data':rec})

#   return scilab

# def qgis(tr_obj):
#   qgis = []
#   url_home = 'https://qgis.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)

#   # Mapathon 2021
#   url_open = 'https://qgis.fossee.in/mapathon-submissions'
#   qgis_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, qgis_encoded)
#   qgis.append({'head':'Mapathon 2021','data':rec})
#   return qgis


# def python(tr_obj):
#   python = []
#   url_home = 'https://tbc-python.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)

#   # Textbook Companion
  
#   url_open = 'https://tbc-python.fossee.in/browse-books'
#   python_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, python_encoded)
#   python.append({'head':'Textbook Companion','data':rec})

#   return python

# def arduino(tr_obj):
#   arduino = []
#   # url_home = 'https://floss-arduino.fossee.in/resources'
#   # foss_encoded = get_encoded_keywords(tr_obj)

#   # Resources Page
#   url_open = 'https://floss-arduino.fossee.in/resources'
#   # arduino_encoded = crawler(url_home, url_open)
#   # rec = top_results(foss_encoded, arduino_encoded)
#   # use above when there are enough good links
#   rec = [0.0, '', '', 'https://floss-arduino.fossee.in/']
#   arduino.append({'head':'Resources','data':rec})

#   return arduino

# def rsoftware(tr_obj):
  
#   r = []
#   url_home = 'https://r.fossee.in'
#   foss_encoded = get_encoded_keywords(tr_obj)

#   # Case Study Project
#   url_open = 'https://r.fossee.in/case-study-project/completed-case-studies'
#   r_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, r_encoded)
#   r.append({'head':'Case Study Project','data':rec})

#   # Textbook Companion
#   url_open ='https://r.fossee.in/textbook-companion/completed-books'
#   r_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, r_encoded)
#   r.append({'head':'Textbook Companion','data':rec})

#   # Lab Migration
#   url_open ='https://r.fossee.in/lab-migration/completed-labs'
#   r_encoded = crawler(url_home, url_open)
#   rec = top_results(foss_encoded, r_encoded)
#   r.append({'head':'Lab Migration','data':rec})

#   return r

# unwanted = ['\n\n','Home', 'Resources', 'Downloads', 'Forum', ' forum','forums','Testimonials','Fellowship 2022',
#  'News & Events', 'NCCPS-2018 Proceedings', 'News', 'Events', 'Contact Us', 'Login', 'Flowsheeting Project',
#  'Procedure', 'Submission Guidelines', 'Flowsheeting Proposal', 'Completed Flowsheets','Flowsheets in Progress',
#  'Internship Forms','Honorarium', 'Flowsheeting Project Ideas', 'Prizes', 'Custom Modeling Project',
#  'Textbook Companion Project','contact', 'Lab Migration Project', 'Spoken Tutorial', ' ', 'Features',
#  '\nClick here to view stats', 'Click here to view stats','https://dwsim.fossee.in/flowsheeting-project', 'click here',
#  'contact-esim (at) fossee(dot)in . ', 'Source Code', 'Contact us','Converted Files', 'TBC Certificates',
#  'Books In Progress','Completed Books','Download Codes', 'Book Proposal', 'Completed Labs',
#  'Creative Commons Attribution-ShareAlike 4.0 International License','Click Here','FOSSEE',
#  'FOSSEE forum','Spoken Tutorial forum','Detail', 'here', 'CFD Facebook ', ' Facebook ','CFD Twitter ','Case Study Project',
#  'Publications','Research Migration Project','Research Migration Proposal','Search','R on Garuda Cloud',
#  'Research Migration Forms','Research Migration in Progres', 'Chemical Engineering',
#  'OpenModelica Twitter ','OpenModelica Facebook ','R Twitter ','R Facebook ','Team',
#  'Spoken Tutorials','FLOSS', 'FLOSS-Arduino Books','about-us','Case Study Forms','Conference',
#  'Case Study Certificates','R Programming','Labs in progress','TBC Code Search','Inria','Books in Progress',
#  ' Twitter ','Click here','FAQs','Scilab on NVLI Cloud','Scilab Enterprises',
#  'FOT Workshop','Workshop Statistics','https//scilab.in/',
#  'Coding Guidelines','Xcos Textbook Companion Project','Examples for Lecture Demonstration ','FOSSEE Examples for Lecture Demonstration ','TBC Code Search','Scilab Textbook Companion Project',
#  'Click here to view stats','CFD(OpenFOAM)','DWSIM','OpenModelica','Osdag','Python','R','Scilab','eSim',
#  'Mapathon submissions','QGIS Facebook ','QGIS Twitter ','About us']
 