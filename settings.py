from os import environ

SESSION_CONFIGS = [
    dict(
        name='counting_zero_demo',
        display_name='Counting Zero Demo',
        app_sequence=['CountingZero', 'Final_Payoff'],
        num_demo_participants=4,
    ),
    dict(
        name='stock_forecast_demo',
        display_name='Stock Forecast Demo',
        app_sequence=['StockForecast', 'Final_Payoff'],
        num_demo_participants=4,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
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




# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'ja'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '9099979674036'
