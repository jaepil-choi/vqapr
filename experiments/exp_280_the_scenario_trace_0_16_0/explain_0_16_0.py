# ruff: noqa: E501, RUF001 -- prose data
"""What each call in a frame's stack asks for (→) and what it hands back (←), in plain words.

Keyed by qualname; `<file stem>.<qualname>` wins where two functions share a qualname (`run`).
Written from each function's docstring and code, and checked against the values `trace_io.py`
recorded for it (the renderer shows those values under each line).
"""

EXPLAIN = {
    # ---- the command line
    "main": ("터미널 인자를 받아 동사(register · run · check …)를 고르고 그 담당에게 넘긴다.", "종료 코드. 0이면 성공, 1이면 거절. 결과 봉투(JSON)는 이미 화면에 찍혔다."),
    "register.run": ("창구가 선언 파일 경로를 넘긴다: 이 YAML에 적힌 것을 등록해 달라.", "성공 봉투: 섹션별로 등록된 id와 선언이 뜻하는 바를 푼 문장(spoken)."),
    "read_yaml_mapping": ("선언 파일을 YAML 1.2 규칙으로 읽는다 — yes/no가 True/False로 바뀌는 사고를 막으려고.", "선언 내용 dict: instruments · datasets · components · runs 네 섹션."),
    "apply": ("선언 dict를 등록부에 적용해 달라. 파일 경로도 함께 넘긴다 — 거절 메시지가 어느 파일인지 말하게.", "섹션별로 무엇이 등록됐는지."),
    "_apply": ("apply의 본체. 섹션을 의존 순서(명단 → dataset → 부품 → run)대로 처리한다.", "섹션별 등록 결과."),
    "failure": ("창구가 받은 예외를 사람도 에이전트도 읽을 수 있는 봉투로 바꿔 달라고 한다.", "거절 봉투: ok false · 단계 · failures[code · 요구 · 관찰 · 고치는 법] · mutation false."),
    "success": ("결과 필드를 성공 봉투에 싸 달라.", "성공 봉투 dict (ok true)."),
    "_run_each_in_workers": ("run 이름들과 jobs=2를 받는다: 이 run들을 프로세스 여러 개로 나눠 돌려라.", "결과 봉투: run마다 한 줄."),
    # ---- the workspace (ledger)
    "Workspace.transaction": ("등록 담당이 장부 카트를 연다. 장부가 이미 있으면 그 내용을 복사해 둔다.", "빈 카트(Transaction). 디스크는 아직 그대로. fresh=True는 장부가 처음 생긴다는 뜻."),
    "Workspace.open": ("장부 파일 전체를 읽어 달라.", "Workspace 객체: 등록된 부품 · dataset · run."),
    "_instruments": ("선언의 instruments 섹션(종류별 명단 파일 이름)으로 종목 명단을 등록한다.", "영수증: 종목 10개, 종류별 개수 {'stock': 10}, 명단 파일의 지문."),
    "_component": ("부품 선언(kind · 파일 · 클래스 이름)을 받아 코드를 등록한다.", "등록된 부품 id."),
    "Transaction.commit": ("카트를 장부에 반영하라: 잠금 → 장부 다시 읽기 → 카트 합치기 → 한 번 쓰기.", "없음. 결과는 디스크의 장부 파일이다."),
    "Workspace._write": ("합친 상태(datasets · sources · components · runs)를 YAML 텍스트로 만들어 장부에 쓴다.", "없음. 실제 쓰기는 write_atomically가 한다."),
    "Workspace._write_roster": ("명단 포인터(양식 · 파일 경로 · 지문)를 instruments.json에 쓴다.", "없음."),
    "Workspace.require_verified": ("얼리기가 dataset 이름으로 묻는다: 이 dataset을 읽어도 되나?", "등록 카드. 파일 지문 검사를 통과했다는 뜻."),
    "_merge_dataset": ("카트의 장부 상태에 새 dataset 카드를 합친다. 같은 이름이 있으면 사용자가 쓴 부분을 비교한다.", "(합친 상태, 바뀌었나). 사용자가 쓴 부분이 다르면 409로 거절."),
    # ---- the inspection bench (data/verification.py and the scans under it)
    "verify_roster": ("명단 파일 경로를 검수대에 넘긴다: 이 표들이 명단으로 읽히나(instrument_id · kind 열이 있나)?", "문제 없음(Diagnosis의 failures가 비어 있음) + 파일에서 읽은 {종류: {종목: 종류}} 표."),
    "build_roster": ("읽은 표를 도메인에 넘겨 종목 객체로 만든다. 한 종목이 두 종류로 적혔는지도 본다.", "명단 객체(InstrumentRoster): 종목마다 StockInstrument."),
    "verify_source": ("dataset 카드(선언)와 파일 위치를 검수대에 넘긴다: 이 parquet이 선언대로인가?", "(판정, 걸린 시간, 잰 값이 채워진 카드). 카드에 기간 · 지문 · 체결 가격이 붙는다."),
    "describe": ("duckdb에 묻는다: 이 parquet의 컬럼과 타입은? 행은 읽지 않는다.", "컬럼 → 타입: available_at TIMESTAMP_TZ, instrument VARCHAR, open DOUBLE …"),
    "check_schema": ("선언이 가리킨 컬럼과 타입을 describe 결과와 맞춰 본다.", "판정 + 필드 타입. 틀리면 failures에 이유가 담기고 뒤 단계는 돌지 않는다."),
    "check_key": ("(available_at, instrument) 조합이 빈 값 없이 한 번씩만 있는지 파일 전체를 훑는다.", "판정. 중복이나 빈 키가 있으면 예시와 함께 거절."),
    "check_span": ("available_at의 최소 · 최대를 재 달라(파일 전체 집계).", "(판정, (첫 시각, 끝 시각))."),
    "check_values": ("숫자 컬럼에 NaN이나 무한대가 있는지 훑는다.", "판정. 있으면 행 예시와 함께 거절."),
    "check_execution_prices": ("체결표라면, 거래 가능(is_tradable) 행마다 가격 컬럼이 양수 · 유한한지 잰다.", "쓸 수 있는 가격 컬럼 목록. 거절이 아니라 측정값이다."),
    "physical_digest": ("파일 바이트의 sha256을 계산해 달라.", "지문(64자). 이후 명령은 파일 내용 대신 이것만 대조한다."),
    "require_verified": ("등록 카드와 파일 위치를 넘긴다: 지금 파일이 등록 때 잰 그 바이트인가?", "같으면 지문을 돌려준다. 다르면 source_changed 예외."),
    "Diagnosis.raise_if_failed": ("판정에 실패가 있으면 예외로 바꿔 던진다.", "예외 — 카트는 커밋되지 않고 버려진다."),
    # ---- code components
    "fingerprint_component": ("부품 파일의 바이트와 설정으로 지문을 계산한다. 코드가 한 글자만 바뀌어도 달라진다.", "지문. 기록 이름 @뒤의 8자리가 여기서 나온다."),
    "conformance": ("부품을 import해 역할의 약속(있어야 할 메서드와 그 시그니처)을 지키는지 본다.", "판정. 틀리면 어느 메서드가 왜 틀렸는지."),
    # ---- atomic file writes
    "write_atomically": ("쓸 경로와 내용을 받아 옆 임시 파일에 끝까지 쓰고 디스크에 내린다(fsync).", "없음. 끝나면 대상 파일이 통째로 새 내용이다 — 반쯤 쓴 파일은 보이지 않는다."),
    "_swap": ("임시 파일을 대상 이름으로 바꿔 끼운다(os.replace). Windows에서 누가 읽는 중이면 몇 번 다시 시도.", "없음."),
    # ---- the run's gate: preflight
    "preflight": ("check · run이 장부와 run 선언을 넘긴다: 판정을 모두 하고, 되면 run을 얼려 달라.", "평결(RunVerdict): 실패 목록 · 답하지 못한 판정 · 얼린 run 또는 얼리기가 낸 거절."),
    "judgments": ("판정 일곱(종목 · 명단 · 기간 · 체결 순서 · 읽을 dataset · 비중 · 출력)을 하나씩 돌린다.", "(실패 목록, 답하지 못한 판정 목록)."),
    "freeze": ("장부의 이름을 실제 값(코드 지문 · 파일 경로와 지문 · 시간표 · 초기 계좌)으로 풀어 한 덩어리로 얼린다.", "FrozenRun(작업 키트). 앞서 거절된 사실이 있으면 같은 거절을 다시 던진다."),
    "_judge_execution_ordering": ("모든 결정 시각 뒤에 체결할 시각이 있는지 본다.", "실패 목록. 비었으면 통과. 체결표를 못 읽으면 예외 → '답하지 못한 판정'이 된다."),
    "RunFacts._once": ("사실 하나를 처음이면 읽고, 이미 읽었으면 저장된 값을 준다 — 같은 것을 두 번 읽지 않으려고.", "그 사실(여기서는 시간표)."),
    "RunFacts.schedule": ("얼리기가 시간표를 달라고 한다.", "판정 때 만든 시간표를 그대로 — 다시 만들지 않는다."),
    "RunFacts.execution_table": ("run이 체결에 쓸 표를 한 번 묶어 달라.", "묶은 체결표. 파일이 바뀌었으면 예외(결과 없음)."),
    "derived_schedule": ("선언의 schedule 규칙(매일 08:00)을 체결표의 거래일 위에 펼친다.", "Schedule: 결정 시각(ScheduledEvent)들."),
    "Schedule.inclusive_slice": ("run의 start ~ end 사이의 결정 시각만 잘라 달라.", "그 기간의 ScheduledEvent들."),
    "distinct_values": ("체결표의 trade_at 열에서 run 기간 ± 1일의 서로 다른 시각만 읽는다.", "시각 목록 (factor run은 12개)."),
    "_validate_requirement": ("모델이 읽겠다고 한 dataset · 필드가 등록돼 있고 파일이 그대로인지 확인한다.", "그 dataset의 파일 위치(SourceSpec)."),
    "RunResources.of": ("판정 때 이미 만든 객체(모델 · 거래소 · 기간)를 얼린 run에 맞춰 꺼내 달라.", "공구 봉지(RunResources): 모델 인스턴스 · 거래소 · run 식별자."),
    # ---- assembling and running
    "assemble.run": ("얼린 run과 공구 봉지를 넘긴다: 이제 실제로 돌려라.", "RunResult: 결과와 기록."),
    "_run_member": ("run 하나에 필요한 도구(스캔 세션 · 데이터 창고 · 기록 쓰개)를 준비해 돌리고, 기록을 다시 읽는다.", "(결과 요약, 기록 내용)."),
    "_horizon": ("얼린 run의 기간을 데이터 창고의 스캔 범위로 바꾼다.", "(시작, 끝)."),
    "registered_roster": ("run 시작 때 종목 명단을 새로 읽어 달라 — 명단은 늘어나므로 얼리지 않는다.", "명단 10개와 그 지문."),
    "datamodel_loop": ("얼린 DataModel run으로 루프를 조립한다: 시간표 · 계산 담당 · 출력.", "RunLoop: 처리할 사건 16개."),
    "RunLoop.run": ("루프가 사건을 시각 순서로 하나씩 처리한다.", "결과 요약: 사건 수 · 행 수 · 출력 경로."),
    "RunLoop.finish": ("사건을 다 처리하면 결과를 모은다.", "결과 요약."),
    "RunLoop.handle": ("루프가 사건 하나를 넘긴다: ScheduledEvent면 결정, MarketEvent면 체결 · 평가.", "그 사건의 흔적: 계좌 버전 등."),
    # ---- reading data during a run
    "DuckDbObservationStore._scan_bounds": ("모델이 읽을 dataset과 lookback으로, 한 번에 스캔할 시각 범위를 정한다.", "(시작, 끝)."),
    "observation_table": ("duckdb로 그 범위의 행을 읽는다 — available_at이 지금보다 늦은 행은 빼고.", "Arrow 표 (예: 153행 × available_at · instrument · close)."),
    "Panel.from_table": ("스캔한 표를 날짜 × 종목 행렬로 접는다.", "Panel (예: 날짜 17 × 종목 10)."),
    "PanelWindow.matrix": ("저자 코드가 창을 숫자 행렬로 달라고 한다.", "numpy 행렬: 지금 알 수 있는 날 × 종목. 값이 없으면 NaN."),
    "open_cube": ("작업자가 구운 판 폴더에서 이 dataset의 판을 찾는다.", "Cube. 판의 원천 지문이 작업자가 확인한 지문과 같아야 쓴다."),
    "panel_from_cube": ("구운 판에서 자기 기간 · 종목만 잘라 panel을 만든다(메모리 매핑).", "Panel — 스캔 없이."),
    # ---- the author's models
    "SampleFeatures.compute": ("계산 담당이 저자 모델에 창(context)을 넘긴다: 이 시각 기준으로 계산해라.", "행 목록 {instrument, momentum_5d}. 첫날은 빈 목록."),
    "SampleFactor.decide": ("결정 담당이 저자 전략에 call(시각 · 창 · 계좌)을 넘긴다: 목표 비중을 정해라.", "Rebalance: 6종목 ±0.1667. 부호가 방향이다."),
    "SampleStopLoss.decide": ("결정 담당이 저자 전략에 call을 넘긴다: 손절 여부를 보고 비중을 정해라.", "Rebalance(목표 비중) 또는 Hold."),
    "SampleEnhancedIndex.decide": ("결정 담당이 저자 전략에 call을 넘긴다: 가격 창과 alpha 창으로 비중을 정해라.", "Rebalance: 9종목 0.1111 · 0.1944 · 0.0278."),
    # ---- the decision stage (run/engine/stages/decide.py)
    "CallbackHandler._visible_callback_state": ("현재 상태에서 이 전략의 memory와 payload를 꺼낸다.", "(memory 참조, memory, payload)."),
    "CallbackHandler._restore_callback_state": ("꺼낸 memory를 전략 객체의 self.memory에 넣는다.", "없음. 첫날은 {}, 둘째 날엔 진입가 9개."),
    "CallbackHandler._stamp_intent": ("저자의 Rebalance를 공장 양식의 의도서로 바꾼다(의도서 id · 전략 id 도장).", "의도서(EconomicPortfolioIntent): 목표 6개."),
    "CallbackHandler._candidate_callback_state": ("결정 뒤 memory를 엄격한 JSON으로 한 번 정리하고 지문을 붙인다.", "정리된 memory와 그 참조."),
    "RunStateRepository.publish": ("준비한 새 상태(계좌 · memory · 대기 의도서)를 한 번에 게시한다. 이 결정이 남긴 행도 함께 흘려보낸다.", "새 상태 (version 1)."),
    # ---- the market instant (execute · value)
    "ExecutionHandler.fill": ("시장 시계가 15:30 순간을 넘긴다: 기다리던 의도서가 있으면 체결해라.", "같은 순간에 체결 결과(filled)가 붙어 돌아온다."),
    "AcademicExchange.execute": ("주문 · 계좌 · 그 시각 가격을 거래소에 넘긴다.", "FillBatch: 주문마다 체결 하나."),
    "ValuationHandler.mark": ("보유를 그 시각 종가로 평가해 달라.", "평가 결과(marked)가 붙은 순간."),
    "Account.mark": ("계좌 상태와 종목별 가격을 넘긴다: 보유 × 가격을 계산해라.", "평가안(PreparedMark): NAV. 커밋해야 반영된다."),
    # ---- the record (record/writer.py, run/recording.py)
    "freeze_run_record": ("얼린 run의 설정(기간 · 읽을 파일과 지문 · 출력)을 run.json으로 쓴다 — 돌리기 전에.", "run.json 경로."),
    "RunRecordWriter.open": ("기록 칸 폴더를 만들고 .running 팻말(pid)을 건다. 누가 이미 돌리는 중이면 거절.", "없음. 이제 이 run id는 이 프로세스 것이다."),
    "RunRecordWriter.append_chunk": ("게시된 행 묶음(예: vqapr.weight 6행)을 기록 쓰개에 넘긴다.", "없음. Arrow 표로 메모리에만 쌓인다."),
    "RunRecordWriter._seal": ("표마다 메모리의 행을 all.parquet 한 파일로 쓰고 진행 메모를 지운다.", "없음."),
    "_write_compact": ("메모리에 쌓인 표 조각들을 all.parquet 한 파일로 합쳐 쓴다.", "없음."),
    "RunRecordWriter.finish": ("기록을 마감한다: 본문 표를 먼저 쓰고, 마감 도장(json)을 원자적으로 쓴다.", "도장 파일 경로."),
    "RunRecordWriter._unlock": (".running 팻말을 지운다.", "없음."),
    "read_run_record": ("run.json을 읽어 달라.", "run.json 내용: 읽은 dataset과 지문, 기간 …"),
    # ---- a run's output as a dataset (run/engine/output.py)
    "RunOutput.append": ("그 시각의 행을 출력에 넘긴다. available_at은 공장이 붙인다.", "없음. 행은 Arrow 표로 메모리에 쌓인다."),
    "RunOutput._seal": ("메모리의 행을 all.parquet 한 파일로 쓴다(임시 파일 → 바꿔 끼우기).", "없음."),
    "RunOutput.register": ("run의 출력 폴더를 dataset으로 등록해 달라 — ①과 같은 검수대를 지난다.", "등록 카드 (어느 run이 만들었는지 포함)."),
    # ---- the --jobs batch (run/batch.py, data/cube.py)
    "batch_reads": ("배치의 run마다 부품을 올려 무엇을 읽는지 한 번씩 묻는다.", "{run: {dataset: 필드}}."),
    "require_independent_batch": ("한 run이 다른 run의 출력을 읽는지 확인한다 — 병렬이면 순서를 약속할 수 없어서.", "없음이면 통과. 읽는 run이 있으면 배치 전체 거절."),
    "batch_cubes": ("배치가 읽을 dataset을 판(cube)으로 굽고, 끝나면 지운다.", "판 폴더 경로. 배치가 끝나면 삭제."),
    "_bake_for_batch": ("dataset마다 읽을 필드를 모아 bake를 부른다.", "없음."),
    "bake": ("dataset 전체 기간 × 전 종목을 한 번 스캔해 .npy 행렬 파일로 쓴다.", "Cube: 날짜 × 종목 행렬과 원천 지문."),
    "in_workers": ("run마다 새 프로세스를 띄워 작업자 함수를 부른다. 넘기는 건 문자열과 bool뿐.", "{run: 결과(status completed)}."),
}
