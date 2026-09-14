# ruff: noqa: E501 -- prose data
"""exp_280's plain-words → / ← lines, with the calls records 280-281 moved, folded or added.

Everything not named below is exp_280's line unchanged. Each line here was written from the
function's docstring and code on f862c147 and checked against the values this directory's traces
recorded for it.
"""

from pathlib import Path

_namespace: dict = {}
exec((Path(__file__).resolve().parents[1] / "exp_280_the_scenario_trace_0_16_0" / "explain_0_16_0.py").read_text(encoding="utf-8"), _namespace)

GONE = {"read_yaml_mapping", "_apply"}  # record 280: renamed to read_declaration; folded into apply

EXPLAIN = {k: v for k, v in _namespace["EXPLAIN"].items() if k not in GONE} | {
    "read_declaration": ("선언 파일을 YAML 1.2 규칙으로 읽는다 — yes/no가 True/False로 바뀌는 사고를 막으려고. 등록 쪽에 산다(record 280).", "선언 내용: instruments · datasets · components · runs 네 섹션."),
    "apply": ("선언을 장부에 적용해 달라. 파일 경로도 넘긴다 — 거절이 어느 파일인지 말하게. 섹션은 명단 → dataset → 부품 → run 순서.", "섹션별로 등록된 것. 거절이면 예외 — 장부는 그대로."),
    "stage_measured": ("dataset 카드와 파일 위치를 넘긴다: 검수대에서 재고, 통과하면 잰 카드를 카트에 담아라. 모든 dataset이 지나는 문 하나(record 281).", "(잰 카드, 장부가 바뀌나). 검수에 걸리면 예외 — 카트에 아무것도 담기지 않는다."),
    "mismatched_source": ("카드가 가리키는 source 이름과 넘겨받은 파일 위치의 이름이 같은지 본다.", "같으면 None. 다르면 거절 하나(400 source_mismatch). 검수대와 장부 합치기가 같은 규칙을 묻는다(record 281)."),
    "Transaction.register_dataset": ("잰 카드와 파일 위치를 카트에 올린다 — 장부 상태에 미리 합쳐 본다.", "장부가 바뀌나(True/False). 파일은 아직 쓰지 않는다."),
    "_merge_dataset": ("카트의 장부 상태에 dataset 카드를 합친다. 같은 이름이 있으면 사용자가 쓴 부분을 비교한다.", "(합친 상태, 바뀌었나). source 이름이 어긋나면 400, 사용자가 쓴 부분이 다르면 409."),
    "RunOutput.register": ("run의 출력 폴더를 dataset으로 등록해 달라 — ①과 같은 문(stage_measured)을 지난다.", "등록 카드 (어느 run이 만들었는지 포함)."),
}
