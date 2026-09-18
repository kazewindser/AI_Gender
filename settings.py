from os import environ

SESSION_CONFIGS = [
    dict(
        name='counting_zero_demo',
        display_name='Counting Zero — No AI',
        treatment_ai=False,
        app_sequence=['Instruction', 'Quiz', 'CountingZeroPractice', 'CountingZero', 'CRT', 'questionnaire', 'Final_Payoff'],
        num_demo_participants=4,
    ),
    dict(
        name='stock_forecast_demo',
        display_name='Stock Forecast — No AI',
        treatment_ai=False,
        app_sequence=['Instruction', 'Quiz', 'StockForecastPractice', 'StockForecast', 'CRT', 'questionnaire', 'Final_Payoff'],
        num_demo_participants=4,
    ),
    dict(
        name='counting_zero_demo_ai',
        display_name='Counting Zero — With AI',
        app_sequence=['Instruction', 'Quiz', 'CountingZeroPractice', 'CountingZero', 'CRT', 'questionnaire', 'Final_Payoff'],
        num_demo_participants=4,
        treatment_ai=True,
    ),
    dict(
        name='stock_forecast_demo_ai',
        display_name='Stock Forecast — With AI',
        app_sequence=['Instruction', 'Quiz', 'StockForecastPractice', 'StockForecast', 'CRT', 'questionnaire', 'Final_Payoff'],
        num_demo_participants=4,
        treatment_ai=True,
    ),
    dict(
        name='CRT',
        display_name='CRT',
        app_sequence=['CRT'],
        num_demo_participants=1,
    ),
    dict(
        name='questionnaire',
        display_name='Questionnaire',
        app_sequence=['questionnaire'],
        num_demo_participants=1,
    ),
    dict(
        name='CountingZeroPractice',
        display_name='CountingZeroPractice',
        app_sequence=['CountingZeroPractice'],
        num_demo_participants=1,
    ),
    dict(
        name='StockForecastPractice',
        display_name='StockForecastPractice',
        app_sequence=['StockForecastPractice'],
        num_demo_participants=1,
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=6.00, participation_fee=500, doc=""
)

PARTICIPANT_FIELDS = [
    'cz_round1_score',
    'cz_round2_score',
    'cz_round3_score',
    'cz_round1_rank',
    'cz_round2_rank',
    'cz_round3_rank',
    'cz_round3_choice',
    'cz_selected_round',
    'cz_final_score',
    'sf_round1_score',
    'sf_round2_score',
    'sf_round3_score',
    'sf_round1_rank',
    'sf_round2_rank',
    'sf_round3_rank',
    'sf_round3_choice',
    'sf_selected_round',
    'sf_final_score',
    'sf_used_stock_codes',
]
SESSION_FIELDS = []


TreatmentAI = False
ShowFeedback = False

# rooms
ROOMS = [
    dict(
        name='pclab',
        display_name='社研PCラボ',
        participant_label_file='_rooms/pclab.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)')
]




# Participant-interface language. Supported by this project:
# 'zh-hans' = Simplified Chinese, 'en' = English, 'ja' = Japanese.
# Restart oTree after changing this value.
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'JPY'
# Preserve half-yen investment earnings for odd investment amounts.
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2
# Keep fixed-yen rewards accurate when converted to points (e.g. 20 / 6).
POINTS_DECIMAL_PLACES = 6
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '9099979674036'
