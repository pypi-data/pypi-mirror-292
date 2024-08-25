# Bangla keyword extractor
This is keyword extractor that support both Bangla and English languages. For the keyword extraction from rake, we used **Rake** algorithm and for keyword extraction from pagerank, we used this [research paper](https://www.researchgate.net/publication/335819660_Keyword_Extraction_from_Bengali_News).

For using this `bangla-keyword-extractor` library, you need to,
Install using pip
```commandline
pip install bangla-keyword-extractor
```
For extracting keywords
```commandline
from bangla_keyword_extractor.keyword_extractor import KeywordExtractor

text = "এটি একটি নমুনা বাক্য।"
extractor = KeywordExtractor(text, max_keywords = 5)
print(extractor.get_keywords_using_rake())
print(extractor.get_keywords_using_pagerank())
```
