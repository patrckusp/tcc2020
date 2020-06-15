import os
import pathlib
import json
import spacy

nlp = spacy.load('pt_core_news_sm')
rootdir = pathlib.Path().absolute()
for root, dirs, files in os.walk(rootdir):
    for name in files:
        if name.endswith((".json")):
            full_path = os.path.join(root, name)
            with open(full_path, encoding='utf-8-sig') as json_file:
                text = json_file.read()
                json_data = json.loads(text)
                doc = nlp(json_data['content'])
                sentences = [sent.string.strip() for sent in doc.sents]
                entities_counter = 0
                json_data['entities'] = {}
                json_data['entities'][entities_counter] = ''
                for sentence in sentences:
                    doc = nlp(sentence)
                    json_data['entities'][entities_counter] = "["
                    for entity in doc.ents:
                        if(json_data['entities'][entities_counter]!='['):
                            json_data['entities'][entities_counter]+= ', '
                        json_data['entities'][entities_counter] += "(" + entity.text + ", " + entity.label_ + ")"
                    json_data['entities'][entities_counter] += "]"
                    entities_counter += 1
            with open(full_path, 'w') as updated_json_file:
                json.dump(json_data, updated_json_file, indent=4)
            print('JSON updated with extracted entities: ' + full_path)
                