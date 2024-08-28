import itertools
import os
import pickle
import secrets
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import Extra, root_validator
from langchain_core.retrievers import BaseRetriever
from pinecone import PodSpec, ServerlessSpec
from pinecone.exceptions.exceptions import PineconeException
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone_text.hybrid import hybrid_convex_scale
from pinecone_text.sparse import BM25Encoder
from tqdm.auto import tqdm

from .kiwi_tokenizer import KiwiBM25Tokenizer


def generate_hash() -> str:
    """Generate a 24-digit random HEX value, divide it into 6 digits and concatenate them with a '-'."""
    random_hex = secrets.token_hex(12)
    return "-".join(random_hex[i : i + 6] for i in range(0, 24, 6))


def create_index(
    api_key: str,
    index_name: str,
    dimension: int,
    metric: str = "dotproduct",
    pod_spec=None,
) -> Any:
    """Create and return a Pinecone index."""
    pc = Pinecone(api_key=api_key)
    if index_name not in pc.list_indexes().names():
        if pod_spec is None:
            pod_spec = ServerlessSpec(cloud="aws", region="us-east-1")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=pod_spec,
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    print(f"[create_index]\n{index.describe_index_stats()}")
    return index


def create_sparse_encoder(stopwords: List[str], mode: str = "kiwi") -> BM25Encoder:
    """Create and return a BM25Encoder."""
    bm25 = BM25Encoder(language="english")
    if mode == "kiwi":
        bm25._tokenizer = KiwiBM25Tokenizer(stop_words=stopwords)
    return bm25


def preprocess_documents(
    split_docs: List[Document],
    metadata_keys: List[str] = ["source", "page"],
    min_length: int = 2,
    use_basename: bool = False,
) -> tuple:
    """Preprocesses the document and returns its content and metadata."""
    contents = []
    metadatas = {key: [] for key in metadata_keys}
    for doc in tqdm(split_docs):
        content = doc.page_content.strip()
        if content and len(content) >= min_length:
            contents.append(content)
            for k in metadata_keys:
                value = doc.metadata.get(k)
                if k == "source" and use_basename:
                    value = os.path.basename(value)
                try:
                    metadatas[k].append(int(value))
                except (ValueError, TypeError):
                    metadatas[k].append(value)
    return contents, metadatas


def fit_sparse_encoder(
    sparse_encoder: BM25Encoder, contents: List[str], save_path: str
) -> str:
    """Learn and store the Sparse Encoder."""
    sparse_encoder.fit(contents)
    with open(save_path, "wb") as f:
        pickle.dump(sparse_encoder, f)
    print(f"[fit_sparse_encoder]\nSaved Sparse Encoder to: {save_path}")
    return save_path


def load_sparse_encoder(file_path: str) -> Any:
    """Load the saved sparse encoder."""
    try:
        with open(file_path, "rb") as f:
            loaded_file = pickle.load(f)
        print(f"[load_sparse_encoder]\nLoaded Sparse Encoder from: {file_path}")
        return loaded_file
    except Exception as e:
        print(f"[load_sparse_encoder]\n{e}")
        return None


def upsert_documents(
    index: Any,
    namespace: str,
    contents: List[str],
    metadatas: Dict[str, List[Any]],
    sparse_encoder: BM25Encoder,
    embedder: Embeddings,
    batch_size: int = 32,
):
    """Insert the document into the Pinecone index."""
    keys = list(metadatas.keys())

    for i in tqdm(range(0, len(contents), batch_size)):
        i_end = min(i + batch_size, len(contents))
        context_batch = contents[i:i_end]
        metadata_batches = {key: metadatas[key][i:i_end] for key in keys}

        batch_result = [
            {"context": context, **{key: metadata_batches[key][j] for key in keys}}
            for j, context in enumerate(context_batch)
        ]

        ids = [generate_hash() for _ in range(i, i_end)]
        dense_embeds = embedder.embed_documents(context_batch)
        sparse_embeds = sparse_encoder.encode_documents(context_batch)

        vectors = [
            {
                "id": _id,
                "sparse_values": sparse,
                "values": dense,
                "metadata": metadata,
            }
            for _id, sparse, dense, metadata in zip(
                ids, sparse_embeds, dense_embeds, batch_result
            )
        ]

        index.upsert(vectors=vectors, namespace=namespace)

    print(f"[upsert_documents]\n{index.describe_index_stats()}")


def upsert_documents_parallel(
    index,
    namespace,
    contents,
    metadatas,
    sparse_encoder,
    embedder,
    batch_size=100,  # Reduce batch size
    max_workers=30,
):
    keys = list(metadatas.keys())

    def chunks(iterable, size):
        it = iter(iterable)
        chunk = list(itertools.islice(it, size))
        while chunk:
            yield chunk
            chunk = list(itertools.islice(it, size))

    def process_batch(batch):
        context_batch = [contents[i] for i in batch]
        metadata_batches = {key: [metadatas[key][i] for i in batch] for key in keys}

        batch_result = [
            {
                "context": context[:1000],
                **{key: metadata_batches[key][j] for key in keys},
            }  # Context length limits
            for j, context in enumerate(context_batch)
        ]

        ids = [generate_hash() for _ in range(len(batch))]
        dense_embeds = embedder.embed_documents(context_batch)
        sparse_embeds = sparse_encoder.encode_documents(context_batch)

        vectors = [
            {
                "id": _id,
                "sparse_values": sparse,
                "values": dense,
                "metadata": metadata,
            }
            for _id, sparse, dense, metadata in zip(
                ids, sparse_embeds, dense_embeds, batch_result
            )
        ]

        try:
            return index.upsert(vectors=vectors, namespace=namespace, async_req=False)
        except Exception as e:
            print(f"Error during Upsert: {e}")
            return None

    batches = list(chunks(range(len(contents)), batch_size))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]

        results = []
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="문서 Upsert 중"
        ):
            result = future.result()
            if result:
                results.append(result)

    total_upserted = sum(result.upserted_count for result in results if result)
    print(f"A total of {total_upserted} Vectors have been upserted.")
    print(f"{index.describe_index_stats()}")


def delete_namespace(pinecone_index: Any, namespace: str):
    try:
        # Verify namespace existence
        namespace_stats = pinecone_index.describe_index_stats()
        if namespace in namespace_stats["namespaces"]:
            pinecone_index.delete(delete_all=True, namespace=namespace)
            print(f"All data in namespace '{namespace}' has been deleted.")
        else:
            print(f"The namespace '{namespace}' does not exist.")

    except PineconeException as e:
        print(f"Error working with Pinecone:\n{e}")


def delete_by_filter(pinecone_index: Any, namespace: str, filter: Dict):
    # Attempted deletion with filters
    try:
        pinecone_index.delete(filter=filter, namespace=namespace)
    except PineconeException as e:
        print(f"Error deleting with filters:\n{e}")


def init_pinecone_index(
    index_name: str,
    namespace: str,
    api_key: str,
    sparse_encoder_path: str = None,
    stopwords: List[str] = None,
    tokenizer: str = "kiwi",
    embeddings: Embeddings = None,
    top_k: int = 10,
    alpha: float = 0.5,
) -> Dict:
    """Initializes the Pinecone index and returns the required components."""
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    print(f"[init_pinecone_index]\n{index.describe_index_stats()}")

    try:
        with open(sparse_encoder_path, "rb") as f:
            bm25 = pickle.load(f)
        if tokenizer == "kiwi":
            bm25._tokenizer = KiwiBM25Tokenizer(stop_words=stopwords)
    except Exception as e:
        print(e)
        return {}

    namespace_keys = index.describe_index_stats()["namespaces"].keys()
    if namespace not in namespace_keys:
        raise ValueError(
            f"`{namespace}` was not found in `{list(namespace_keys)}`."
        )

    return {
        "index": index,
        "namespace": namespace,
        "sparse_encoder": bm25,
        "embeddings": embeddings,
        "top_k": top_k,
        "alpha": alpha,
    }


class PineconeKiwiHybridRetriever(BaseRetriever):
    """
    A hybrid searcher class that combines Pinecone and Kiwi.

    This class uses both dense and sparse vectors to search for documents.
    It utilizes Pinecone indexes and Kiwi tokenizers to perform effective hybrid search.

    Parameters:
        embeddings (Embeddings): Embedding model to convert documents and queries into dense vectors.
        sparse_encoder (Any): Encoder that converts documents and queries into sparse vectors (e.g. BM25Encoder)
        index (Any): Pinecone index object to use for searching
        top_k (int): Maximum number of documents to return as search results (default: 10)
        alpha (float): Parameter to adjust the weight of dense and sparse vectors (between 0 and 1, default: 0.5), when set to alpha=0.75, (0.75: Dense Embedding, 0.25: Sparse Embedding)
        namespace (Optional[str]): Namespace to use within the Pinecone index (default: None)
    """

    embeddings: Embeddings
    sparse_encoder: Any
    index: Any
    top_k: int = 10
    alpha: float = 0.5
    namespace: Optional[str] = None

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator(allow_reuse=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """
        Method to check if the required packages are installed.

        Returns:
            Dict: A dictionary of values that passed the validation.
        """
        try:
            from pinecone_text.hybrid import hybrid_convex_scale
            from pinecone_text.sparse.base_sparse_encoder import \
                BaseSparseEncoder
        except ImportError:
            raise ImportError(
                "Could not import pinecone_text python package. "
                "Please install it with `pip install pinecone_text`."
            )
        return values

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **search_kwargs,
    ) -> List[Document]:
        """
        The main method to retrieve relevant documents for a given query.

        Args:
            query (str): The search query.
            run_manager(CallbackManagerForRetrieverRun): Callback manager.
            **search_kwargs: Additional search parameters

        Returns:
            List[Document]: List of related documents
        """
        alpha = self._get_alpha(search_kwargs)
        dense_vec, sparse_vec = self._encode_query(query, alpha)
        query_params = self._build_query_params(
            dense_vec, sparse_vec, search_kwargs, include_metadata=True
        )

        query_response = self.index.query(**query_params)
        # print("namespace", self.namespace)

        documents = self._process_query_response(query_response)

        # Perform a rerank if the Rerank option is present
        if (
            "search_kwargs" in search_kwargs
            and "rerank" in search_kwargs["search_kwargs"]
        ):
            documents = self._rerank_documents(query, documents, **search_kwargs)

        return documents

    def _get_alpha(self, search_kwargs: Dict[str, Any]) -> float:
        """
        Method to get the alpha value.

        Args:
            search_kwargs (Dict[str, Any]): Search parameters.

        Returns:
            Float: The alpha value
        """
        if (
            "search_kwargs" in search_kwargs
            and "alpha" in search_kwargs["search_kwargs"]
        ):
            return search_kwargs["search_kwargs"]["alpha"]
        return self.alpha

    def _encode_query(
        self, query: str, alpha: float
    ) -> Tuple[List[float], Dict[str, Any]]:
        """
        Method to encode a query.

        Args:
            query (str): The query to encode.
            alpha (float): The alpha value to use for hybrid scaling.

        Returns:
            Tuple[List[float], Dict[str, Any]]: Tuple of dense and sparse vectors
        """
        sparse_vec = self.sparse_encoder.encode_queries(query)
        dense_vec = self.embeddings.embed_query(query)
        dense_vec, sparse_vec = hybrid_convex_scale(dense_vec, sparse_vec, alpha=alpha)
        sparse_vec["values"] = [float(s1) for s1 in sparse_vec["values"]]
        return dense_vec, sparse_vec

    def _build_query_params(
        self,
        dense_vec: List[float],
        sparse_vec: Dict[str, Any],
        search_kwargs: Dict[str, Any],
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Method to configure query parameters.

        Args:
            dense_vec (List[float]): Dense vector
            sparse_vec (Dict[str, Any]): Sparse vector
            search_kwargs (Dict[str, Any]): Search parameters
            include_metadata (bool): Whether to include metadata.

        Returns:
            Dict[str, Any]: Configured query parameters
        """
        query_params = {
            "vector": dense_vec,
            "sparse_vector": sparse_vec,
            "top_k": self.top_k,
            "include_metadata": include_metadata,
            "namespace": self.namespace,
        }

        if "search_kwargs" in search_kwargs:
            kwargs = search_kwargs["search_kwargs"]
            query_params.update(
                {
                    "filter": kwargs.get("filter", query_params.get("filter")),
                    "top_k": kwargs.get("top_k")
                    or kwargs.get("k", query_params["top_k"]),
                }
            )

        return query_params

    def _process_query_response(self, query_response: Dict[str, Any]) -> List[Document]:
        """
        Method to process the query response.

        Args:
            query_response (Dict[str, Any]): Pinecone query response.

        Returns:
            List[Document]: A list of processed documents
        """
        return [
            Document(
                page_content=r.metadata["context"],
                metadata={
                    "page": r.metadata.get("page"),
                    "source": r.metadata.get("source"),
                    "score": r.get("score"),
                },
            )
            for r in query_response["matches"]
        ]

    def _rerank_documents(
        self, query: str, documents: List[Document], **kwargs
    ) -> List[Document]:
        """
        Method to reorder the retrieved documents.

        Args:
            query (str): The search query.
            documents (List[Document]): List of documents to reorder
            **kwargs: Additional parameters

        Returns:
            List[Document]: A list of reordered documents
        """
        print("[rerank_documents]")
        rerank_model = kwargs.get("rerank_model", "bge-reranker-v2-m3")
        top_n = kwargs.get("top_n", len(documents))

        rerank_docs = [
            {"id": str(i), "text": doc.page_content} for i, doc in enumerate(documents)
        ]

        result = self.index.inference.rerank(
            model=rerank_model,
            query=query,
            documents=rerank_docs,
            top_n=top_n,
            return_documents=True,
        )

        # Reorganize the article list based on the reordered results
        reranked_documents = []
        for item in result:
            original_doc = documents[int(item["id"])]
            reranked_doc = Document(
                page_content=original_doc.page_content,
                metadata={**original_doc.metadata, "rerank_score": item["score"]},
            )
            reranked_documents.append(reranked_doc)

        return reranked_documents
