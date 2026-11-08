import tiktoken


def analyze_tokens(text: str, model_name: str = "gpt-4o") -> dict[str, int | list[int]]:
    """Metni verilen modelin tokenizer'ı ile token parçalarına ayırır ve analiz eder."""
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)

    return {
        "char_count": len(text),
        "token_count": len(tokens),
        "token_ids": tokens,
    }


if __name__ == "__main__":
    english_text = (
        "FastAPI with SQLAlchemy async engine provides scalable backend solutions."
    )
    turkish_text = "FastAPI ve asenkron SQLAlchemy altyapısı ölçeklenebilir backend "
    "çözümleri sunar."

    en_res = analyze_tokens(english_text)
    tr_res = analyze_tokens(turkish_text)

    print("--- ENGLİSH TEXT ANALYZER ---")
    print(f"Karakter Sayısı : {en_res['char_count']}")
    print(f"Token Sayısı    : {en_res['token_count']}")
    print(f"Token ID'leri   : {en_res['token_ids']}\n")

    print("--- TURKISH TEXT ANALYZER ---")
    print(f"Karakter Sayısı : {tr_res['char_count']}")
    print(f"Token Sayısı    : {tr_res['token_count']}")
    print(f"Token ID'leri   : {tr_res['token_ids']}")
