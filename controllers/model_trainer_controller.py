import math
from textblob import TextBlob as tb
from classes import SearchTerm

pre_mapped_words = dict()

def tf(word, blob):
	return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
	if word in pre_mapped_words:
		return pre_mapped_words[word]
	else:
		pre_mapped_words[word] = sum(1 for blob in bloblist if word in blob.words)
		return pre_mapped_words[word]

def idf(word, bloblist):
	return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)

def calculate_tfidf_all_docs(list_of_docs):
	if len(list_of_docs) == 0:
		return
	bloblist = [ tb(doc.full_text_no_stop) for doc in list_of_docs]
	for index in range(len(bloblist)):
		words_checked = []
		for word in bloblist[index].words:
			if word not in words_checked:
				SearchTerm.SearchTerm(tfidf = tfidf(word, bloblist[index], bloblist), 
					word = word, document = list_of_docs[index])
				words_checked.append(word)
	return
