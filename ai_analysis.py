import json
from pathlib import Path


PROMPT_FILE_PATH = Path("docs") / "Beacon_Prompt.md"

REQUIRED_SIGNAL_KEYS = ("theme", "period", "candidates")

USER_PROMPT_PLACEHOLDER = "{signal_extraction.pyが出力したJSONをここに挿入}"


def _validate_signal_json(signal_json: dict) -> None:
    """Signal JSONが最低限必要なキーを持っているか検証する。"""

    for key in REQUIRED_SIGNAL_KEYS:
        if key not in signal_json:
            raise ValueError(f"Signal JSONに必須キー '{key}' がありません。")

    if not isinstance(signal_json["candidates"], list):
        raise ValueError("Signal JSONの'candidates'はリストである必要があります。")

    period = signal_json["period"]

    if "previous" not in period or "current" not in period:
        raise ValueError("Signal JSONの'period'には'previous'と'current'が必要です。")


def _extract_code_block(markdown_text: str, heading: str) -> str:
    """Markdown内の指定した見出し直後にある、最初のコードブロックの中身を取り出す。"""

    heading_index = markdown_text.find(heading)

    if heading_index == -1:
        raise ValueError(f"プロンプトMarkdownに見出し '{heading}' が見つかりません。")

    after_heading = markdown_text[heading_index:]

    first_fence = after_heading.find("```")
    second_fence = after_heading.find("```", first_fence + 3)

    if first_fence == -1 or second_fence == -1:
        raise ValueError(f"見出し '{heading}' の下にコードブロックが見つかりません。")

    code_block = after_heading[first_fence + 3 : second_fence]

    return code_block.strip("\n")


def _load_prompt_parts() -> tuple[str, str]:
    """docs/Beacon_Prompt.mdから、System PromptとUser Promptの下書きを読み込む。"""

    prompt_markdown = PROMPT_FILE_PATH.read_text(encoding="utf-8")

    system_prompt = _extract_code_block(prompt_markdown, "## System Prompt")
    user_prompt_template = _extract_code_block(prompt_markdown, "## User Prompt")

    return system_prompt, user_prompt_template


def _build_user_prompt(user_prompt_template: str, signal_json: dict) -> str:
    """User Promptのプレースホルダーに、実際のSignal JSONを差し込む。"""

    signal_json_text = json.dumps(signal_json, ensure_ascii=False, indent=2)

    return user_prompt_template.replace(USER_PROMPT_PLACEHOLDER, signal_json_text)


def _call_provider(system_prompt: str, user_prompt: str) -> str:
    """AIプロバイダーへプロンプトを送信し、生成された文章を受け取る（未実装）。

    OpenAI・Claude・Gemini・ローカルLLMなど、特定プロバイダーへの接続処理は
    将来この関数の中だけに実装する。generate_report()はこの関数の
    シグネチャ（system_prompt, user_prompt -> str）にのみ依存する。
    """

    raise NotImplementedError("AIプロバイダーへの接続はまだ実装されていません。")


def generate_report(signal_json: dict) -> str:
    """Signal JSONから、AIによるDaily Report用の説明文を生成する。"""

    _validate_signal_json(signal_json)

    system_prompt, user_prompt_template = _load_prompt_parts()
    user_prompt = _build_user_prompt(user_prompt_template, signal_json)

    return _call_provider(system_prompt, user_prompt)
