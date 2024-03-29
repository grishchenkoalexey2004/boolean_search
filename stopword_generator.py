from nltk.corpus import stopwords
import codecs

stop_words_ru = set(stopwords.words("russian"))
stop_words_en = set(stopwords.words("english"))


with codecs.open("stop_word_list.txt",mode = "w",encoding="utf-8") as output_file:
    for word in stop_words_en:
        output_file.write(word+"\n")

    for word in stop_words_ru:
        output_file.write(word+"\n")
        
print("finished")