# EPUB-Sorter
depends on three epub parsers : 
- [ebooklib](https://github.com/aerkalov/ebooklib)
- [epub_meta](https://github.com/paulocheque/epub-meta)
- [and parts of lectors epub parser](https://github.com/BasioMeusPuga/Lector)

it gathers the metadata from whichever parser can actually parse the epub

```
D:\oldBooks\Raymond Feist - [The Riftwar Saga 04] - A Darkness at Sethanon.epub
->
D:\newBooks\Raymond Feist\A Darkness at Sethanon\Raymond Feist - [The Riftwar Saga 04] - A Darkness at Sethanon.epub
               ^Author           ^Title                    ^Original File Name
```

## Installation:

```
git clone https://github.com/ismaelcompsci/EPUB-Sorter.git
pip install -r requirements.txt
```

## Usage:
```python
# To move books to the new directory
sorter = EpubSorter(r"/home/Downloads",r"/home/Downloads/sorted")
sorter.start_book_sorter()
```
or
```python
# To copy books to the new directory
sorter = EpubSorter(r"/home/Downloads",r"/home/Downloads/sorted", copy_file=True)
sorter.start_book_sorter()
```

### TODO
- [ ] Use isbn the get accurate metadata
- [ ] fix lectors author metadata
- [ ] package into a pip package
 