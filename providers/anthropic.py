import os


API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"

# 料金事故を避けるため、出力トークン数の上限を固定する
#
# この値は「上限」であって「目標」ではない。
# 実際に生成された分だけが課金対象なので、上げてもコストは増えない。
#
# 出力は候補ごとの短いobservation文（JSON構造）のみであり、
# Daily Report全文（Markdown）はここでは生成しないため、
# 実際の出力トークン数は8000よりかなり小さくなる見込み。
MAX_TOKENS = 8000

# AIに返させるtoolの名前。tool_choiceで固定し、必ずこのtoolを
# 1回だけ呼ばせることで、自由形式のMarkdownが返ってくることを防ぐ。
OBSERVATION_TOOL_NAME = "submit_candidate_observations"

# 候補ごとのobservationだけを受け取るtool定義。
# star数・hits数・URL・selection_reasonsといったSignal JSON由来の事実は
# ここに含めない。AIに再出力させないためであり、Python側
# （report_markdown.py）がSignal JSONから直接使用する。
OBSERVATION_TOOL = {
    "name": OBSERVATION_TOOL_NAME,
    "description": (
        "各候補（Repository）について、何が変化したかを短い日本語の観測文として送信する。"
        "star数・hits数・URL・selection_reasonsなど、Signal JSONに含まれる数値や事実は"
        "ここに含めない（Python側が別途Signal JSONから直接使用するため）。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "observations": {
                "type": "array",
                "description": "candidatesに含まれる候補ごとの観測文の配列。",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": (
                                "対象RepositoryのSignal JSON上のname（例: owner/repo）。"
                                "candidatesに存在する値と完全に一致させること。"
                            ),
                        },
                        "observation": {
                            "type": "string",
                            "description": (
                                "その候補について何が変化したかを述べる、"
                                "1〜2文の日本語の観測文。具体的な数値は含めない。"
                            ),
                        },
                    },
                    "required": ["name", "observation"],
                },
            },
        },
        "required": ["observations"],
    },
}


def generate(system_prompt: str, user_prompt: str, model: str) -> list[dict]:
    """Anthropic (Claude) APIへプロンプトを送信し、候補ごとのobservationsを受け取る。

    自由形式のMarkdown全文を生成させるのではなく、tool use（tool_choiceで
    強制）によって構造化データとして受け取る。戻り値は
    [{"name": ..., "observation": ...}, ...] というリストであり、
    Daily Report全文の組み立てはreport_markdown.pyが別途行う。
    """

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
            tools=[OBSERVATION_TOOL],
            tool_choice={
                "type": "tool",
                "name": OBSERVATION_TOOL_NAME,
                "disable_parallel_tool_use": True,
            },
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
        raise RuntimeError(
            "MAX_TOKENSに達したため、tool useの出力が途中で終了した可能性があります。"
        )

    tool_use_blocks = [
        block
        for block in response.content
        if block.type == "tool_use" and block.name == OBSERVATION_TOOL_NAME
    ]

    if not tool_use_blocks:
        raise RuntimeError(
            f"AI応答にtool_useブロック '{OBSERVATION_TOOL_NAME}' が"
            f"含まれていません (stop_reason={response.stop_reason})。"
        )

    observations = tool_use_blocks[0].input.get("observations")

    if not isinstance(observations, list):
        raise RuntimeError(
            "tool useの'observations'がリストではありません。"
        )

    return observations
