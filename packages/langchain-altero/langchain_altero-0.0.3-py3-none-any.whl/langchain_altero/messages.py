from langchain_core.messages import AIMessageChunk


def stream_response(response, return_output=False):
    """
    Mengalirkan respons dari model AI dan mengeluarkannya saat memproses setiap bagian.

    Fungsi ini mengulang setiap item dalam iterable `response`. Jika item tersebut merupakan instance dari `AIMessageChunk`,
    mengekstrak dan mengeluarkan isi potongan tersebut. Jika item berupa string, fungsi ini akan mengeluarkan string secara langsung. Secara opsional, fungsi
    mengembalikan string gabungan dari semua potongan respons.

    Parameter
    - respons (dapat diulang): Iterable dari potongan respons, yang dapat berupa objek atau string `AIMessageChunk`.
    - return_output (bool, opsional): Jika Benar, fungsi mengembalikan string respons terkait sebagai string. Nilai defaultnya adalah False.

    Nilai yang dikembalikan:
    - Sebuah string: Jika `return_output` bernilai True, string respons yang digabungkan; jika tidak, tidak ada yang dikembalikan.
    """
    answer = ""
    for token in response:
        if isinstance(token, AIMessageChunk):
            answer += token.content
            print(token.content, end="", flush=True)
        elif isinstance(token, str):
            answer += token
            print(token, end="", flush=True)
    if return_output:
        return answer