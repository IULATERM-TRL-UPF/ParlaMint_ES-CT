import spacy
nlp = spacy.load("ca_core_news_trf")
text = 'iniciï dient honorables'
doc = nlp(text)
a = [i.lemma_ for i in doc]
nlp.remove_pipe("lemmatizer")
lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "lookup", "overwrite": True})
nlp.initialize()
doc = nlp(text)                                
b = [i.lemma_ for i in doc]
print(b)