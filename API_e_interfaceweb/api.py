# Need to Install libraries
# pip3 install -U spacy
# python3 -m spacy download pt
# pip3 install pyngrok
# pip3 install annoy
# pip3 install pandas
# pip3 install flask
# pip3 install sentence-transformers

import pandas as pd

import spacy
nlp = spacy.load('pt')

from sentence_transformers import SentenceTransformer, LoggingHandler
import numpy as np
import logging

#### Just some code to print debug information to stdout
np.set_printoptions(threshold=100)

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO,
                    handlers=[LoggingHandler()])

# Load Sentence model (based on BERT) from URL
model = SentenceTransformer('distiluse-base-multilingual-cased')

def get_embeddings(sentences):
  global model
  sentence_embeddings = model.encode(sentences)

  v = []
  for sentence, embedding in zip(sentences, sentence_embeddings):
    v.append(embedding)
    
  return v

from annoy import AnnoyIndex
import numpy as np

def knn(df,u,text,k=100):
  embedding = get_embeddings([text])

  result = u.get_nns_by_vector(embedding[0], k, search_k=-1, include_distances=True)
  counter = 0
  z = df.iloc[0][1:14]*0.0
  # print(z)
  sum = 0.0
  for id in result[0]:
    cos = 1.0 - (result[1][counter] / 1.4142135623730951)
    z += df.iloc[id][1:14]*cos
    # print(id, result[1][counter], cos)
    # print(df.iloc[id])
    counter += 1
    sum += cos

  z /= sum
  return z

df_treinamento = pd.read_csv('distiluse-base-multilingual-cased-knn-train.csv')
df_treinamento

u = AnnoyIndex(512, 'angular')
u.load('distiluse-base-multilingual-cased-knn-annoy.ann') # super fast, will just mmap the file

def get_nlp(noticia_nova):
  doc = nlp(noticia_nova)
  sentences = [sent.string.strip() for sent in doc.sents]

  ner = []
  for sentence in sentences:
    for entity in nlp(sentence).ents:
      ner.append((str(entity), str(entity.label_)))

  return ner

def get_category(noticia_nova,k=5):
  global df_treinamento,u
  return knn(df_treinamento,u,noticia_nova,k=k)

## Gerando um endpoint
from pyngrok import ngrok
public_url = ngrok.connect(port=5000)
print('Example: ',public_url+'?text=Exporta%C3%A7%C3%B5es%20brasileiras%20de%20soja%20caem%20em%20mar%C3%A7o+diz+ESAQL+USP')

from flask import Flask,request
from flask import jsonify
# conectando o endpoint com o nosso modelo
# esse execucao trava a celula

app = Flask(__name__)

@app.route("/")
def service():
    try:
        text = request.args.get('text')
        print('text: ',text)
        ner = get_nlp(text)
        category = get_category(text)

        result = {}
        result['ner'] = ner
        result['classification'] = category.to_dict()
        
        #results = " ".join(results)
        print('Output: ',jsonify(result))
        return jsonify(result),200
    except Exception as e:
        print(e)
        print("An exception occurred")
        return str(-1),200

app.run()