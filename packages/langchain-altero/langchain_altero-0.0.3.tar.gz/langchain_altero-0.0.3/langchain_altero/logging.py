import os


def langsmith(project_name=None, set_enable=True):

    if set_enable:
        result = os.environ.get("LANGCHAIN_API_KEY")
        if result is None or result.strip() == "":
            print(
                "LangChain API Key tidak di set. Catatan: Untuk informasi lebih lanjut, lihat https://wikidocs.net/250954"
            )
            return
        os.environ["LANGCHAIN_ENDPOINT"] = (
            "https://api.smith.langchain.com"  # Endpoint LangSmith API
        )
        os.environ["LANGCHAIN_TRACING_V2"] = "true"  # true: Enabled
        os.environ["LANGCHAIN_PROJECT"] = project_name  # Nama project
        print(f"Mulai penelusuran langsmith.\n[nama project]\n{project_name}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"  # false: Disabled
        print("Penelusuran langsmith dihentikan.")


def env_variable(key, value):
    os.environ[key] = value
