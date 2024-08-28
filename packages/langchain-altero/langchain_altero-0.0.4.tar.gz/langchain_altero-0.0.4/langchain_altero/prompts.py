import numpy as np
import yaml
from langchain_core.example_selectors.base import BaseExampleSelector
from langchain_core.prompts import loading
from langchain_core.prompts.base import BasePromptTemplate


def load_prompt(file_path, encoding="utf8") -> BasePromptTemplate:
    """
    Memuat pengaturan prompt berdasarkan jalur file.

    Fungsi ini membaca pengaturan prompt dalam format YAML dari jalur file yang diberikan,
    dan memuat prompt berdasarkan pengaturan tersebut.

    Parameter
    file_path (str): Jalur ke file pengaturan prompt.

    Returns:
    object: Mengembalikan objek prompt yang dimuat..
    """
    with open(file_path, "r", encoding=encoding) as f:
        config = yaml.safe_load(f)

    return loading.load_prompt_from_config(config)


class CustomExampleSelector(BaseExampleSelector):
    """
    Class ini memilih contoh yang paling mirip dengan teks masukan.
    Class ini menggunakan model embedding OpenAI untuk melakukan precompute representasi vektor dari contoh,
    dan memilih contoh yang paling mirip berdasarkan cosine similarity antara input teks dan contoh.

    Atribut:
        example (list): Daftar contoh yang menjadi dasar pemilihan.
        embedding_model (object): Model embedding untuk mengubah teks menjadi vektor.
        search_key (str): Key value untuk dibandingkan dengan teks masukan dalam contoh.
    """

    def __init__(self, examples, embedding_model, search_key="instruction"):
        """ 
        Lakukan inisialisasi daftar contoh, embedding model, dan search key.

        Arg:
            examples (list): Daftar data contoh.
            embedding_model (object): Model yang akan dihitung embeddingnya.
            search_key (str): Key untuk digunakan saat membandingkan contoh dengan input.
        """
        self.examples = examples
        self.embedding_model = embedding_model
        self.search_key = search_key
        # Lakukan pre-compute embedding untuk semua contoh.
        self.example_embeddings = [
            (example, self.embedding_model.embed_query(example[search_key]))
            for example in examples
        ]

    def cosine_similarity(self, vec1, vec2):
        """Hitung Cosine similarity antara dua vektor."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def add_example(self, example):
        """Tambahkan contoh baru ke daftar contoh."""
        self.examples.append(example)

    def select_examples(self, input_variables, k=1):
        """
        Pilih contoh yang paling mirip dengan variabel input yang diberikan.
        
        Arg:
            input_variables (dict): Variabel input untuk memilih contoh.
            k (int): Jumlah contoh yang akan dipilih.
            
        Returns:
            list: Daftar contoh yang paling mirip dengan input teks.
        """
        # Hitung embedding dari input teks.
        input_text = input_variables[self.search_key]
        input_embedding = self.embedding_model.embed_query(input_text)

        # Hitung cosine similarity antara input teks dan contoh.
        similarities = []
        for example, example_embedding in self.example_embeddings:
            similarity = self.cosine_similarity(input_embedding, example_embedding)
            similarities.append((example, similarity))

        # Urutkan contoh berdasarkan similarity.
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Pilih k contoh yang paling mirip.
        return [example for example, _ in similarities[:k]]
