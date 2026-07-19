import os


API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"


def generate(system_prompt: str, user_prompt: str, model: str) -> str:
    """Anthropic (Claude) APIへプロンプトを送信し、生成された文章を受け取る。

    実際のSDK呼び出しはまだ実装していない。
    """

    api_key = os.environ.get(API_KEY_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"{API_KEY_ENV_VAR}が設定されていません。.envを確認してください。"
        )

    raise NotImplementedError("Anthropic APIへの実際の接続はまだ実装されていません。")
