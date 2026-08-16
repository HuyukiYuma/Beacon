import os


API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"

# 料金事故を避けるため、出力トークン数の上限を固定する
# （Daily Reportが途中で切れないよう、最後まで生成できる値にしている）
#
# この値は「上限」であって「目標」ではない。
# 実際に生成された分だけが課金対象なので、上げてもコストは増えない。
#
# 新しいモデルではthinking（内部推論）が既定で有効になり、
# max_tokensはthinkingと本文の合計に対する上限として働く。
# 候補が10件を超えるとテンプレート構成の本文だけで2,000トークンを超えるため、
# thinkingの分を含めた余裕を確保している。
MAX_TOKENS = 8000


def generate(system_prompt: str, user_prompt: str, model: str) -> str:
    """Anthropic (Claude) APIへプロンプトを送信し、生成された文章を受け取る。"""

    try:
        import anthropic
    except ImportError as error:
        raise RuntimeError(
            "anthropicパッケージがインストールされていません。"
            "'pip install anthropic' を実行してください。"
        ) from error

    api_key = os.environ.get(API_KEY_ENV_VAR)

    if not api_key:
        raise ValueError(
            f"{API_KEY_ENV_VAR}が設定されていません。.envを確認してください。"
        )

    # APIキー自体は表示しない
    print("AI Provider  : anthropic")
    print(f"AI Model     : {model}")
    print(f"Input length : {len(system_prompt) + len(user_prompt)} characters")

    client = anthropic.Anthropic(api_key=api_key)

    # Beaconは観察レポート用途であり創作ではないため、
    # temperatureは指定せずAnthropic SDKの標準値をそのまま使う。
    # （新しいモデルではtemperature指定自体が400エラーになる場合があり、
    #   AI_MODELは.envで自由に変更できるため、指定しない方が安全）
    try:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.AuthenticationError as error:
        raise RuntimeError(
            "Anthropic APIの認証に失敗しました。ANTHROPIC_API_KEYを確認してください。"
        ) from error
    except anthropic.NotFoundError as error:
        raise RuntimeError(
            f"指定されたモデル '{model}' が見つかりません。AI_MODELを確認してください。"
        ) from error
    except anthropic.APIStatusError as error:
        raise RuntimeError(
            f"Anthropic APIがエラーを返しました (status={error.status_code}): {error.message}"
        ) from error
    except anthropic.APIConnectionError as error:
        raise RuntimeError(
            "Anthropic APIとの通信に失敗しました。ネットワーク接続を確認してください。"
        ) from error

    print(f"Stop reason  : {response.stop_reason}")

    if response.stop_reason == "max_tokens":
        print(
            "Warning: MAX_TOKENSに達したため、出力が途中で終了している可能性があります。"
        )

    text_blocks = [block.text for block in response.content if block.type == "text"]

    return "".join(text_blocks)
