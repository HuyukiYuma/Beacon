import importlib
import json
import os
from pathlib import Path
from typing import NamedTuple


PROMPT_FILE_PATH = Path("docs") / "Beacon_Prompt.md"
ENV_FILE_PATH = Path(".env")
PROVIDERS_DIRECTORY = Path("providers")

REQUIRED_SIGNAL_KEYS = ("theme", "period", "candidates")

USER_PROMPT_PLACEHOLDER = "{signal_extraction.pyが出力したJSONをここに挿入}"

# signal_extraction.pyのselect_candidatesが付与する理由コード。
# ここで新しい理由コードを追加することはない（判定ロジック側の変更に追従するだけ）。
KNOWN_SELECTION_REASONS = (
    "new_repository",
    "increased_keyword_hits",
    "top_star_growth",
    "multiple_keyword_matches",
)


def count_selection_reasons(candidates: list[dict]) -> dict[str, int]:
    """候補のselection_reasonsを、既知の理由コードごとに集計する。

    副作用のない純粋関数。「どの候補がどの理由に該当するか」という判定
    （signal_extraction.pyのselect_candidates）には一切関与せず、既に
    候補へ記録された理由コードを数えるだけ。

    未知の理由コード（KNOWN_SELECTION_REASONSにないもの）が含まれていた場合は、
    黙って無視せずValueErrorを送出する。件数が静かに欠落するとSummaryが
    実態と食い違うため（CLAUDE.mdの「Do not silently catch unexpected errors」
    にも従う）。
    """

    counts = {reason: 0 for reason in KNOWN_SELECTION_REASONS}

    for candidate in candidates:
        for reason in candidate["selection_reasons"]:
            if reason not in counts:
                raise ValueError(f"未知のselection_reasonsコードです: '{reason}'")

            counts[reason] += 1

    return counts


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


def _load_env_file() -> None:
    """.envファイルを読み込み、まだ設定されていない環境変数として反映する。"""

    if not ENV_FILE_PATH.exists():
        return

    for line in ENV_FILE_PATH.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue

        key, _, value = stripped_line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _list_available_providers() -> list[str]:
    """providers配下に実装されている、利用可能なプロバイダー名の一覧を返す。"""

    return sorted(
        path.stem
        for path in PROVIDERS_DIRECTORY.glob("*.py")
        if path.stem != "__init__"
    )


def _load_provider_module(provider_name: str):
    """AI_PROVIDERに対応する、providers配下のモジュールを読み込む。"""

    module_name = f"providers.{provider_name}"

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        # providers.<name>自体が存在しない場合のみ、分かりやすいエラーに変換する。
        # provider内部の依存モジュール不足によるModuleNotFoundErrorはそのまま伝える。
        if error.name != module_name:
            raise

        available_providers = ", ".join(_list_available_providers())
        raise ValueError(
            f"未対応のAIプロバイダーです: '{provider_name}'。"
            f"利用可能なプロバイダー: {available_providers}"
        ) from error


def _call_provider(system_prompt: str, user_prompt: str) -> list[dict]:
    """設定されたAIプロバイダーへプロンプトを送信し、候補ごとのobservationsを受け取る。

    プロバイダー固有の処理（tool useの組み立てや応答からの取り出しなど）は
    `providers/`配下の各モジュールが持つ。ここではAI_PROVIDER/AI_MODELの設定に
    基づいてモジュールを読み込み、呼び出すだけであり、特定プロバイダーのSDKには
    依存しない。戻り値はMarkdown文字列ではなく、
    [{"name": ..., "observation": ...}, ...]という構造化データ。
    """

    _load_env_file()

    provider_name = os.environ.get("AI_PROVIDER")
    model_name = os.environ.get("AI_MODEL")

    if not provider_name:
        raise ValueError("AI_PROVIDERが設定されていません。.envを確認してください。")

    if not model_name:
        raise ValueError("AI_MODELが設定されていません。.envを確認してください。")

    provider_module = _load_provider_module(provider_name)

    return provider_module.generate(system_prompt, user_prompt, model_name)


def request_candidate_observations(signal_json: dict) -> list[dict]:
    """Signal JSONをAIへ送り、候補ごとのobservation（What changed相当の観測文）を取得する。

    Daily Report全体のMarkdown組み立てはreport_markdown.pyが担当するため、
    ここではAIから構造化データ（候補ごとのobservation）を取得するだけ。
    candidatesが空の場合はAPIを呼ばずに空リストを返す。
    """

    _validate_signal_json(signal_json)

    if not signal_json["candidates"]:
        return []

    system_prompt, user_prompt_template = _load_prompt_parts()
    user_prompt = _build_user_prompt(user_prompt_template, signal_json)

    return _call_provider(system_prompt, user_prompt)


class ObservationValidationResult(NamedTuple):
    """validate_candidate_observationsの結果。

    observationsは{候補name: observation文}の辞書で、
    report_markdown.pyへそのまま渡せる形。
    """

    observations: dict[str, str]
    unknown_names: list[str]
    duplicate_names: list[str]
    missing_names: list[str]


def validate_candidate_observations(
    candidates: list[dict],
    raw_observations: list[dict],
) -> ObservationValidationResult:
    """AIが返した候補ごとのobservationsを、Signal JSONのcandidatesと照合する。

    副作用のない純粋関数。

    - Signal JSONのcandidatesに存在しないnameは「未知name」として除外する
      （AIが存在しないRepositoryをでっち上げた場合の混入を防ぐ）。
    - 同じnameが複数回出現した場合は「重複name」として記録し、
      最初の1件のみを採用する。
    - name・observationのどちらかが文字列でない項目は不正な項目として無視する
      （＝その候補は「不足candidate」として扱われる）。
    - candidatesにあるがobservationsに採用されなかったnameは
      「不足candidate」として記録する。report_markdown.py側で
      フォールバック文が使われることを想定している。
    """

    known_names = {candidate["name"] for candidate in candidates}

    observations: dict[str, str] = {}
    unknown_names: list[str] = []
    duplicate_names: list[str] = []

    for item in raw_observations:
        name = item.get("name")
        observation = item.get("observation")

        if not isinstance(name, str) or not isinstance(observation, str):
            continue

        if name not in known_names:
            unknown_names.append(name)
            continue

        if name in observations:
            duplicate_names.append(name)
            continue

        observations[name] = observation

    missing_names = [
        candidate["name"] for candidate in candidates if candidate["name"] not in observations
    ]

    return ObservationValidationResult(
        observations=observations,
        unknown_names=unknown_names,
        duplicate_names=duplicate_names,
        missing_names=missing_names,
    )
