"""Small project-local translation helper for Python, templates, and JavaScript."""

from settings import LANGUAGE_CODE


TRANSLATIONS = {
    'en': {
        'ai_area': 'AI assistant area',
        'ai_assistant': 'AI assistant',
        'ai_can_help': 'You may use the AI assistant during the task.',
        'ai_failed': 'The AI is temporarily unavailable. Please try again later.',
        'ai_help': 'Using the AI assistant',
        'ai_prompt_intro': 'The AI receives the following system instruction:',
        'ai_replying': 'AI is replying…',
        'ai_system_prompt': 'Always respond in English.',
        'ai_unavailable': 'AI is not available in this condition.',
        'ai_use_note': 'Using the AI is optional and does not stop the timer.',
        'answer_goal': 'Your goal',
        'auto_next': 'A new question appears after each answer',
        'block_complete': 'This task is complete.',
        'chart_aria': 'Stock price chart',
        'choose_intro': 'Choose how your score in the next task will be determined.',
        'choose_scheme': 'Choose a payment scheme',
        'chosen_scheme': 'Chosen scheme',
        'confirm_continue': 'Confirm and continue',
        'copied': 'Copied',
        'copy_matrix': 'Copy the entire matrix on the left',
        'copy_series': 'Copy all stock-price series on the left',
        'correct_answer': 'Correct answer',
        'count_area': 'Counting task area',
        'count_instructions': 'Count the number of zeros in the matrix and enter your answer.',
        'count_instructions_title': 'Counting-zero task instructions',
        'count_intro': 'Count how many zeros appear in each matrix.',
        'count_task': 'Counting-zero task',
        'count_test_result': 'You completed',
        'cumulative_score': 'Cumulative score',
        'day': 'Day',
        'enter_forecast': 'Enter your forecast.',
        'enter_integer': 'Please enter a valid integer.',
        'enter_message': 'Please enter a message.',
        'enter_number': 'Please enter a valid number.',
        'enter_zero_count': 'Enter the number of zeros.',
        'final_results': 'Final results',
        'final_score': 'Final score',
        'five_minutes': '5 minutes',
        'fixed_time': 'Fixed task duration',
        'forecast_instructions': 'Review the price history and forecast the closing price 30 trading days later.',
        'forecast_price': 'Forecast price',
        'goal_text': 'Answer as accurately as possible and complete as many questions as you can.',
        'integer_range': 'Please enter an integer from 0 to {max_cells}.',
        'matrix_aria': 'Matrix of zeros and ones',
        'message_aria': 'Message to the AI assistant',
        'message_placeholder': 'Enter a message…',
        'piece_intro': 'Your score depends only on your own performance.',
        'piece_rate': 'Piece rate',
        'piece_rate_description': 'The sum of the points you earn across all questions in Task 3 becomes your Task 3 score, without comparison with other group members.',
        'piece_rule': 'Your task score is used without comparison with other participants.',
        'points': 'points',
        'positive_forecast': 'Please enter a forecast greater than 0.',
        'question': 'Question',
        'question_score': 'Question score',
        'questions_unit': 'questions, with a cumulative score of',
        'random_block': 'One task was selected at random to determine your final score.',
        'rank': 'Rank',
        'rank_format': '{rank}',
        'relative_error': 'Relative error',
        'remaining_time': 'Time remaining:',
        'round_finished': 'Task finished',
        'scheme_aria': 'Payment-scheme choices',
        'score': 'Score',
        'score_feedback': 'Score: {score}; cumulative score: {cumulative_score}',
        'score_formula_intro': 'The score for each question is calculated as follows:',
        'score_range': 'Points per question',
        'score_rule_intro': 'First, relative error is calculated as follows:',
        'score_unit': 'points.',
        'scoring_rules': 'Scoring rules',
        'selected': 'Selected',
        'send': 'Send',
        'series_aria': 'Historical stock-price series',
        'series_title': 'Historical prices',
        'stock_area': 'Stock-forecast task area',
        'stock_instructions_title': 'Stock-forecast task instructions',
        'stock_intro': 'Use the displayed historical prices to forecast the closing price 30 trading days later.',
        'stock_task': 'Stock-forecast task',
        'stock_test_result': 'You completed',
        'stock_warning_text': ' A relative error of 20% or more receives 0 points.',
        'submit': 'OK',
        'submitted_answer': 'Submitted answer',
        'test_complete': 'Test complete',
        'task_label': 'Task',
        'tournament_description': 'Your Task 3 score is compared with the Task 2 tournament scores of the other members of your group. If your score ranks first, your Task 3 score is multiplied by 4; otherwise, your Task 3 score is 0.',
        'tournament': 'Tournament',
        'tournament_intro': 'Your performance is compared with other participants.',
        'tournament_rule': 'If you rank first in your group, your Task 2 score is multiplied by 4. Otherwise, your Task 2 score is 0.',
        'understand_continue': 'I understand; continue',
        'unlimited': 'Unlimited questions',
        'wait_group': 'Please wait',
        'wait_group_body': 'Waiting for the other members of your group to finish.',
        'wait_others': 'Please wait',
        'wait_others_body': 'The task will begin when all participants are ready.',
        'warning': 'Note:',
        'warning_text': ' A relative error of 20% or more receives 0 points.',
        'zero_count': 'Number of zeros',
    },
    'ja': {
        'ai_area': 'AIアシスタント領域', 'ai_assistant': 'AIアシスタント',
        'ai_can_help': '課題中にAIアシスタントを利用できます。',
        'ai_failed': 'AIは一時的に利用できません。しばらくしてからもう一度お試しください。',
        'ai_help': 'AIアシスタントの利用', 'ai_prompt_intro': 'AIには次のシステム指示が与えられます：',
        'ai_replying': 'AIが回答中…', 'ai_system_prompt': '常に日本語で回答してください。',
        'ai_unavailable': 'この条件ではAIを利用できません。',
        'ai_use_note': 'AIの利用は任意です。利用中もタイマーは進みます。',
        'answer_goal': '目標', 'auto_next': '回答後、自動的に次の問題が表示されます',
        'block_complete': 'このタスクは終了しました。', 'chart_aria': '株価チャート',
        'choose_intro': '次のタスクの得点決定方法を選んでください。', 'choose_scheme': '報酬方式を選択',
        'chosen_scheme': '選択した方式', 'confirm_continue': '確定して次へ', 'copied': 'コピーしました',
        'copy_matrix': '左側の行列全体をコピー', 'copy_series': '左側の株価時系列をすべてコピー',
        'correct_answer': '正解', 'count_area': 'ゼロ数え課題領域',
        'count_instructions': '行列内のゼロの数を数えて入力してください。',
        'count_instructions_title': 'ゼロ数え課題の説明', 'count_intro': '各行列に含まれるゼロの数を数えてください。',
        'count_task': 'ゼロ数え課題', 'count_test_result': '回答した問題数：',
        'cumulative_score': '累積得点', 'day': '日', 'enter_forecast': '予測値を入力してください。',
        'enter_integer': '有効な整数を入力してください。', 'enter_message': 'メッセージを入力してください。',
        'enter_number': '有効な数値を入力してください。', 'enter_zero_count': 'ゼロの数を入力してください。',
        'final_results': '最終結果', 'final_score': '最終得点', 'five_minutes': '5分間',
        'fixed_time': '制限時間は固定です',
        'forecast_instructions': '過去の株価を確認し、30取引日後の終値を予測してください。',
        'forecast_price': '予測株価',
        'goal_text': 'できるだけ正確に回答し、時間内にできるだけ多くの問題を解いてください。',
        'integer_range': '0から{max_cells}までの整数を入力してください。', 'matrix_aria': '0と1の行列',
        'message_aria': 'AIアシスタントへのメッセージ', 'message_placeholder': 'メッセージを入力…',
        'piece_intro': '得点は自分自身の成績だけで決まります。',
        'piece_rate': '出来高払い',
        'piece_rate_description': 'タスク3で各問題から獲得した得点の合計が、他のグループメンバーと比較されず、そのままタスク3の得点になります。',
        'piece_rule': '他の参加者とは比較せず、課題得点がそのまま用いられます。',
        'points': 'ポイント', 'positive_forecast': '0より大きい予測値を入力してください。',
        'question': '問題', 'question_score': '問題得点', 'questions_unit': '問、累積得点：',
        'random_block': '無作為に選ばれた1つのタスクから最終得点を決定しました。',
        'rank': '順位', 'rank_format': '{rank}位', 'relative_error': '相対誤差',
        'remaining_time': '残り時間：', 'round_finished': 'タスク終了',
        'scheme_aria': '報酬方式の選択肢', 'score': '得点',
        'score_feedback': '得点：{score}、累積得点：{cumulative_score}',
        'score_formula_intro': '各問題の得点は次の式で計算されます：', 'score_range': '1問あたりの得点',
        'score_rule_intro': 'まず、相対誤差を次の式で計算します：', 'score_unit': 'ポイントです。',
        'scoring_rules': '採点ルール', 'selected': '選択済み', 'send': '送信',
        'series_aria': '過去の株価時系列', 'series_title': '過去の株価',
        'stock_area': '株価予測課題領域', 'stock_instructions_title': '株価予測課題の説明',
        'stock_intro': '表示された過去の株価から、30取引日後の終値を予測してください。',
        'stock_task': '株価予測課題', 'stock_test_result': '回答した問題数：',
        'stock_warning_text': ' 相対誤差が20%以上の場合、得点は0点です。', 'submit': 'OK',
        'submitted_answer': '提出した回答', 'test_complete': 'テスト終了',
        'task_label': 'タスク',
        'tournament_description': '自分のタスク3の得点を、同じグループの他のメンバーのタスク2（トーナメント）の得点と比較します。自分の得点が1位の場合、タスク3の得点が4倍になります。それ以外の場合、タスク3の得点は0になります。',
        'tournament': 'トーナメント',
        'tournament_intro': 'あなたの成績を他の参加者と比較します。',
        'tournament_rule': '同じグループ内で順位が1位の場合、タスク2の得点が4倍になります。それ以外の場合、タスク2の得点は0になります。', 'understand_continue': '理解して次へ',
        'unlimited': '問題数は無制限', 'wait_group': 'お待ちください',
        'wait_group_body': 'グループの他の参加者が終了するまでお待ちください。',
        'wait_others': 'お待ちください', 'wait_others_body': '全員の準備が整うと課題が始まります。',
        'warning': '注意：', 'warning_text': ' 相対誤差が20%以上の場合、得点は0点です。',
        'zero_count': 'ゼロの数',
    },
    'zh-hans': {
        'ai_area': 'AI 助手区域', 'ai_assistant': 'AI 助手', 'ai_can_help': '任务中可以使用 AI 助手。',
        'ai_failed': 'AI 暂时无法回复，请稍后再试。', 'ai_help': '使用 AI 助手',
        'ai_prompt_intro': 'AI 会收到以下系统提示：', 'ai_replying': 'AI 正在回复…',
        'ai_system_prompt': '请始终使用中文回答。', 'ai_unavailable': '当前条件不提供 AI。',
        'ai_use_note': '是否使用 AI 由你决定，使用 AI 时计时不会暂停。', 'answer_goal': '你的目标',
        'auto_next': '每次回答后自动进入下一题', 'block_complete': '本阶段已完成。',
        'chart_aria': '股票价格图表', 'choose_intro': '请选择下一阶段的得分决定方式。',
        'choose_scheme': '选择报酬方式', 'chosen_scheme': '选择的方式', 'confirm_continue': '确认并继续',
        'copied': '已复制', 'copy_matrix': '复制左边整个矩阵', 'copy_series': '一键复制左边所有股价时间序列',
        'correct_answer': '正确答案', 'count_area': '数零任务区域',
        'count_instructions': '请数出矩阵中零的数量并输入答案。', 'count_instructions_title': '数零任务说明',
        'count_intro': '请计算每个矩阵中出现了多少个零。', 'count_task': '数零任务',
        'count_test_result': '你共完成', 'cumulative_score': '累计得分', 'day': '日',
        'enter_forecast': '请输入预测值。', 'enter_integer': '请输入有效的整数。',
        'enter_message': '请输入消息。', 'enter_number': '请输入有效的数字。',
        'enter_zero_count': '请输入零的数量。', 'final_results': '最终结果', 'final_score': '最终得分',
        'five_minutes': '5 分钟', 'fixed_time': '固定任务时间',
        'forecast_instructions': '请查看历史价格并预测 30 个交易日后的收盘价。', 'forecast_price': '预测价格',
        'goal_text': '请尽可能准确地回答，并在时间内完成尽可能多的问题。',
        'integer_range': '请输入 0 到 {max_cells} 之间的整数。', 'matrix_aria': '由零和一组成的矩阵',
        'message_aria': '发送给 AI 助手的消息', 'message_placeholder': '输入消息…',
        'piece_intro': '你的得分仅取决于自己的表现。', 'piece_rate_description': '你在任务 3 各题中获得的分数之和将直接作为任务 3 的得分，不与同组其他成员比较。',
        'piece_rate': '计件报酬',
        'piece_rule': '不与其他参与者比较，直接采用你的任务得分。', 'points': '分',
        'positive_forecast': '请输入大于 0 的预测值。', 'question': '问题', 'question_score': '本题得分',
        'questions_unit': '题，累计得分为', 'random_block': '系统随机抽取了一个阶段来决定你的最终得分。',
        'rank': '排名', 'rank_format': '第 {rank} 名', 'relative_error': '相对误差',
        'remaining_time': '剩余时间：', 'round_finished': '本阶段结束', 'scheme_aria': '报酬方式选项',
        'score': '得分', 'score_feedback': '本题得分：{score}；累计得分：{cumulative_score}',
        'score_formula_intro': '每道题的得分按以下公式计算：', 'score_range': '每题分数',
        'score_rule_intro': '首先按以下公式计算相对误差：', 'score_unit': '分。',
        'scoring_rules': '计分规则', 'selected': '已选中', 'send': '发送',
        'series_aria': '历史股票价格序列', 'series_title': '历史价格', 'stock_area': '股票预测任务区域',
        'stock_instructions_title': '股票预测任务说明', 'stock_intro': '请根据显示的历史价格预测 30 个交易日后的收盘价。',
        'stock_task': '股票预测任务', 'stock_test_result': '你共完成',
        'stock_warning_text': ' 相对误差达到或超过 20% 时，本题得 0 分。', 'submit': 'OK',
        'submitted_answer': '提交的答案', 'test_complete': '测试完成',
        'task_label': '阶段',
        'tournament_description': '将你在任务 3 中的得分与同组其他成员在任务 2（锦标赛）中的得分进行比较。如果你的得分排名第一，任务 3 的得分乘以 4；否则任务 3 的得分为 0。',
        'tournament': '锦标赛',
        'tournament_intro': '你的表现将与其他参与者比较。', 'tournament_rule': '如果你在同一组内排名第一，任务 2 的得分乘以 4；否则任务 2 的得分为 0。',
        'understand_continue': '我已理解，继续', 'unlimited': '题目数量不限', 'wait_group': '请稍候',
        'wait_group_body': '正在等待小组内其他参与者完成。', 'wait_others': '请稍候',
        'wait_others_body': '所有参与者准备好后任务将开始。', 'warning': '注意：',
        'warning_text': ' 相对误差达到或超过 20% 时，本题得 0 分。', 'zero_count': '零的数量',
    },
}


# End-of-task transition to the post-task questionnaire.
for language, messages in {'en': {'main_task_complete': 'Main task complete', 'questionnaire_intro': 'You have completed all three stages of the main task. Please answer the questionnaire next. Your final results will be displayed after you submit your answers.', 'start_questionnaire': 'Continue to questionnaire'}, 'ja': {'main_task_complete': 'メインタスク終了', 'questionnaire_intro': 'メインタスクの全3段階が終了しました。続いてアンケートにお答えください。回答を送信した後に、最終結果が表示されます。', 'start_questionnaire': 'アンケートに進む'}, 'zh-hans': {'main_task_complete': '主任务已完成', 'questionnaire_intro': '你已完成主任务的全部三个阶段。接下来请回答问卷，提交后将显示最终收益结果。', 'start_questionnaire': '开始回答问卷'}}.items():
    TRANSLATIONS[language].update(messages)


for language, messages in {'en': {'crt_intro': 'You have completed the main task. Next, please answer seven quizzes, followed by a questionnaire. Your earnings will be shown at the end.', 'start_crt': 'Continue to quiz instructions'}, 'ja': {'crt_intro': 'メインタスクが終了しました。続いて7つのクイズとアンケートにお答えください。報酬は最後に表示されます。', 'start_crt': 'クイズの説明に進む'}, 'zh-hans': {'crt_intro': '主任务已完成。接下来请回答七道测验题及问卷，报酬将在最后统一显示。', 'start_crt': '查看测验说明'}}.items():
    TRANSLATIONS[language].update(messages)


for language, messages in {'ja': {'crt_reward': 'クイズの報酬', 'crt_correct_count': '正解数', 'total_payment': '合計報酬（参加費を含む）', 'yen': '円'}, 'en': {'crt_reward': 'Quiz earnings', 'crt_correct_count': 'Correct answers', 'total_payment': 'Total earnings (including participation fee)', 'yen': 'yen'}, 'zh-hans': {'crt_reward': '测验报酬', 'crt_correct_count': '答对题数', 'total_payment': '总报酬（含参与费）', 'yen': '日元'}}.items():
    TRANSLATIONS[language].update(messages)


for language, messages in {'ja': {'payment_before_rounding': '切り上げ前の合計報酬', 'payment_after_rounding': '切り上げ後の最終報酬', 'payment_rounding_note': '10円未満の部分は切り上げます。'}, 'en': {'payment_before_rounding': 'Total earnings before rounding', 'payment_after_rounding': 'Final payment after rounding', 'payment_rounding_note': 'The total payment is rounded up to the nearest 10 yen.'}, 'zh-hans': {'payment_before_rounding': '取整前总报酬', 'payment_after_rounding': '取整后最终报酬', 'payment_rounding_note': '总报酬不足10日元的部分向上取整，即按10日元的整数倍支付。'}}.items():
    TRANSLATIONS[language].update(messages)


for language, messages in {'ja': {'main_task_reward': 'メインタスクの報酬', 'participation_fee_label': '参加費'}, 'en': {'main_task_reward': 'Main task earnings', 'participation_fee_label': 'Participation fee'}, 'zh-hans': {'main_task_reward': '主任务报酬', 'participation_fee_label': '参与费'}}.items():
    TRANSLATIONS[language].update(messages)


for language, messages in {'ja': {'additional_payment': '追加報酬'}, 'en': {'additional_payment': 'Additional earnings'}, 'zh-hans': {'additional_payment': '追加报酬'}}.items():
    TRANSLATIONS[language].update(messages)


LANGUAGE_ALIASES = {
    'zh': 'zh-hans',
    'zh-cn': 'zh-hans',
    'zh-hans': 'zh-hans',
    'en-us': 'en',
    'en-gb': 'en',
    'ja-jp': 'ja',
}

LANGUAGE = LANGUAGE_ALIASES.get(LANGUAGE_CODE.lower(), LANGUAGE_CODE.lower())
if LANGUAGE not in TRANSLATIONS:
    LANGUAGE = 'en'

TEXT = TRANSLATIONS[LANGUAGE]


def tr(key, **values):
    """Return one translated string and interpolate named placeholders."""
    text = TEXT.get(key, TRANSLATIONS['en'].get(key, key))
    return text.format(**values) if values else text


def template_context(**values):
    """Add the active translation mapping to an oTree template context."""
    return dict(t=TEXT, **values)
