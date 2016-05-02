from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser, FuzzyTermPlugin
from whoosh.query import *


def search(table_name):

    ix = open_dir("index")
    with ix.searcher() as searcher:
        # query = And(
        #     [Term("content", table_name.decode("utf-8"))])
        query = MultifieldParser(
            ["title", "path", "content"], schema=ix.schema)
        #query.add_plugin(FuzzyTermPlugin())
        q = query.parse(table_name.decode("utf-8"))
        results = searcher.search(q, limit=None, terms=True)
        if len(results) > 0:
            for r in results:
                print("\n\t".join([r["path"], r["title"]]))
                for h in r.matched_terms():
                    print(h)
        else:
            corrector = searcher.corrector("content")
            print("Nope")
            print("Here's some suggestions:")
            suggestions = corrector.suggest(
                table_name.decode("utf-8"), limit=20)
            for s in suggestions:
                print(s)


if __name__ == "__main__":
    table_name = raw_input("Table?:  ")
    search(table_name)
