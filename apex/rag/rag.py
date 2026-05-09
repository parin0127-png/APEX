import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_VERBOSITY"] = "error"
import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from  langchain_community.retrievers import BM25Retriever
import logging

logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
embedding = None

def get_embedding():
    global embedding
    if embedding is None:
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return embedding


LANGUAGE_MAP = {
    ".py"       :       Language.PYTHON,
    ".java"     :       Language.JAVA,
    ".js"       :       Language.JS,
    ".html"     :       Language.HTML,
    ".c"        :       Language.C,
    ".cpp"      :       Language.CPP,
    ".ts"       :       Language.TS,
    ".kt"       :       Language.KOTLIN,
    ".cs"       :       Language.CSHARP,
    ".md"       :       Language.MARKDOWN,
    ".scala"    :       Language.SCALA
}

def get_document(folder_path : str) :
    document = []
    for root, dir, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".py" , ".java", ".html", ".js", ".c", ".cpp", ".ts" , ".cs" , ".md" , ".kt" , ".scala")):
                full_path = os.path.join(root,file)
                try :
                    with open(full_path, "r", encoding = "utf-8") as f:
                        content = f.read()
                        
                        rel_path = os.path.relpath(full_path, folder_path)

                        document.append({
                            "content" : f"# File {rel_path}\n # Filename : {file} \n\n" + content,
                            "source" : full_path
                        })
                except Exception as e:
                    pass
    return document

def create_chunks(documents):
    chunks = []
    for doc in documents:
        ext = os.path.splitext(doc['source'])[1].lower()
        language = LANGUAGE_MAP.get(ext)

        if language:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language = language,
                chunk_size = 500,
                chunk_overlap = 50
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size = 500,
                chunk_overlap = 50
            )
        
        split = splitter.create_documents(
            texts = [doc['content']],
            metadatas = [{'source' : doc['source']}]
        )

        chunks.extend(split)

    return chunks

def create_vectorDB(chunks):
    global _vector
    emb = get_embedding()
    if os.path.exists(".vector_index"):
        try:
            if _vector is not None:
                _vector = None
            import gc, shutil
            gc.collect()
            shutil.rmtree(".vector_index", ignore_errors=True)
        except Exception:
            pass
    return Chroma.from_documents(
        documents = chunks,
        embedding = emb,
        persist_directory = ".vector_index"
    )
    
_bm25 = None
_vector = None
_query_cache = {}
def search_code(vectorDB , query : str, k : int = 3):
    key = query.lower().strip()
    if key in _query_cache:
        return _query_cache[key]
    
    bm25_result = _bm25.invoke(query)[:k]
    vector_result = _vector.invoke(query)[:k]
    seen = set()
    combined = []

    for doc in bm25_result + vector_result:
        uid = doc.metadata['source'] + doc.page_content[:50]
        if uid not in seen:
            seen.add(uid)
            combined.append(doc)

    outputs = f"Found in {', '.join(set(doc.metadata['source'] for doc in combined))} \n\n"
    for doc in combined[:k] :
        outputs += f"\n # Source {doc.metadata['source']}"
        outputs += doc.page_content
        outputs += "\n--------\n"

    final = outputs[:1600]
    _query_cache[key] = final
    return final
    

def indexing(folder_path : str):
    global _bm25, _vector

    document = get_document(folder_path)
    if len(document) == 0:
        return None
    
    chunk = create_chunks(document)
   
    vectorDB = create_vectorDB(chunk)
    
    
    _bm25 = BM25Retriever.from_documents(chunk)
    _bm25.k = 3

    
    _vector = vectorDB.as_retriever(search_kwargs = {"k" : 3})

    return vectorDB