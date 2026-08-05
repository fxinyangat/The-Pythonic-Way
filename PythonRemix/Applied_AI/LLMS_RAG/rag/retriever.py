from vector_store import get_collection, query_documents 

def retrieve(query:str, k:int = 5) -> list[dict]:
    col = get_collection()
    
    query_docs = query_documents(collection=col, query_texts=[query], n_results=k)
                                                   

    
    return query_docs[0]
    

    

if __name__ == "__main__":
    print(retrieve("what is the policy on leave", k =3))
