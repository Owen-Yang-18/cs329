from elit_tokenizer import EnglishTokenizer
tokenizer = EnglishTokenizer()

text = 'Welcome to the world of "Computational Linguistics"! We\'ll have lots of fun this semester.'
sentences = tokenizer.decode(text, segment=2)

for sentence in sentences:
    print(sentence.tokens)
    print(sentence.offsets)