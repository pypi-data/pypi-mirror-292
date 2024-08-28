# langchain-altero

Berbagai paket Python utilitas yang digunakan dalam tutorial LangChain Bahasa Indonesia.

Paket-paket ini menyediakan fungsionalitas tambahan yang mungkin tidak nyaman saat menggunakan LangChain.

## Overview

`langchain_altero` adalah versi lokal dari library [`langchain-teddynote`](https://github.com/teddylee777/langchain-teddynote), yang dirancang untuk menjadi sumber terbuka di bawah lisensi AGPL-3.0. Pustaka ini telah diadaptasi agar lebih sesuai dengan kebutuhan audiens khusus kami sambil mempertahankan fungsionalitas inti dari paket `langchain-teddynote` yang asli.

## install

```bash
pip install langchain-altero
```

## Penggunaan

### Output streaming

Menyediakan fungsi `stream_response` untuk output streaming.

```python
from langchain_altero.messages import stream_response
from langchain_openai import ChatOpenAI

# Membuat sebuah objek
llm = ChatOpenAI(
    temperatur = 0.1, # kreativitas (0.0 ~ 2.0)
    model_name = "gpt-4o-mini", # nama model
    api_key=api_key # api key openai
)
answer = llm.stream("Tolong beritahu saya 10 tempat terindah di Indonesia dan alamatnya!")

# hanya untuk output streaming
stream_response(jawaban)

# jika Anda ingin mendapatkan jawaban yang outputnya sebagai return value
# final_answer = stream_response(answer, return_output=True)
```
Output
```
1.**Bali**
    - **Alamat:** Bali, Indonesia
    - Deskripsi: Terkenal dengan pantainya yang indah, budaya yang kaya, dan pemandangan alam yang menakjubkan.
```
### Jejak LangSmith

```python
# Mengatur penelusuran LangSmith. https://smith.langchain.com
# Mengasumsikan variabel-variabel lingkungan telah diatur.
from langchain_altero import logging

# Masukkan nama proyek.
logging.langsmith(“Masukkan nama proyek Anda”)
```
Output
```
Mulai menelusuri LangSmith.
[nama proyek]
(nama proyek yang Anda masukkan)
```

### Menerapkan pengaturan pengkodean load_prompt

```python
from langchain_altero.prompts import load_prompt

# setel pengodean ke UTF-8 (default)
load_prompt(“prompts/capital.yaml”, encoding=“utf-8”)

# Pada Windows, ubah pengodean ke cp949.
load_prompt(“prompts/capital.yaml”, encoding=“cp949”)
```

## License

Proyek ini dilisensikan di bawah Lisensi AGPL-3.0 - lihat file [LICENSE](./LICENSE) untuk detail lebih lanjut.
