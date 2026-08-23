"""Download random, fixed-length Japanese equity series for the experiment.

Each CSV contains 252 historical trading days followed by 30 future trading
days. Only ordinary equities are accepted; indices, ETFs, funds and REITs are
excluded. Successful ticker codes are written to ``StockBank.py``.
"""

from datetime import date, timedelta
from pathlib import Path
import random
import time

import pandas as pd
import yfinance as yf


TARGET_COUNT = 200
HISTORY_TRADING_DAYS = 252
FORECAST_TRADING_DAYS = 30
TOTAL_TRADING_DAYS = HISTORY_TRADING_DAYS + FORECAST_TRADING_DAYS
RANDOM_START_MIN = date(2010, 1, 1)
# Leave ample room for 282 subsequent Tokyo trading days.
RANDOM_START_MAX = date.today() - timedelta(days=450)
DOWNLOAD_CALENDAR_DAYS = 450
MAX_ATTEMPTS = 3000
REQUEST_DELAY_SECONDS = 0.15

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'TSdata'
STOCK_BANK_PATH = BASE_DIR / 'StockBank.py'


def extract_close(downloaded: pd.DataFrame, ticker: str) -> pd.Series:
    """Return a one-dimensional raw Close series across yfinance versions."""
    close = downloaded['Close']
    if isinstance(close, pd.DataFrame):
        if ticker in close.columns:
            close = close[ticker]
        elif len(close.columns) == 1:
            close = close.iloc[:, 0]
        else:
            raise ValueError('无法识别下载结果中的 Close 列。')
    return pd.to_numeric(close, errors='coerce').dropna()


def is_suitable_equity(stock: yf.Ticker) -> bool:
    """Accept operating-company shares, excluding funds, indices and REITs."""
    info = stock.get_info()
    if str(info.get('quoteType', '')).upper() != 'EQUITY':
        return False

    # Yahoo normally labels REITs as EQUITY, so quoteType alone is insufficient.
    searchable = ' '.join(
        str(info.get(field, ''))
        for field in ('industry', 'sector', 'longName', 'shortName')
    ).upper()
    reit_markers = ('REIT', 'REAL ESTATE INVESTMENT TRUST', '投資法人')
    return not any(marker in searchable for marker in reit_markers)


def random_start_date(random_generator: random.Random) -> date:
    if RANDOM_START_MAX < RANDOM_START_MIN:
        raise RuntimeError('随机日期范围无效，请检查 RANDOM_START_MIN。')
    span = (RANDOM_START_MAX - RANDOM_START_MIN).days
    return RANDOM_START_MIN + timedelta(
        days=random_generator.randint(0, span)
    )


def prepare_stock_data(
    ticker: str,
    requested_start: date,
) -> pd.DataFrame | None:
    stock = yf.Ticker(ticker)
    if not is_suitable_equity(stock):
        return None

    # The first returned row is the first trading day on/after the random date.
    requested_end = requested_start + timedelta(days=DOWNLOAD_CALENDAR_DAYS)
    downloaded = yf.download(
        ticker,
        start=requested_start.isoformat(),
        end=requested_end.isoformat(),
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=False,
    )
    if downloaded.empty or 'Close' not in downloaded:
        return None

    close = extract_close(downloaded, ticker)
    if len(close) < TOTAL_TRADING_DAYS:
        return None
    close = close.iloc[:TOTAL_TRADING_DAYS]

    base_close = float(close.iloc[0])
    if not pd.notna(base_close) or base_close <= 0:
        return None

    segments = (
        ['history'] * HISTORY_TRADING_DAYS
        + ['forecast'] * FORECAST_TRADING_DAYS
    )
    return pd.DataFrame(
        {
            'Date': pd.to_datetime(close.index).strftime('%Y-%m-%d'),
            'Close': close.to_numpy(dtype=float),
            'NormalizedClose': close.to_numpy(dtype=float) / base_close * 100,
            'Segment': segments,
        }
    )


def write_stock_bank(tickers: list[str]) -> None:
    lines = ['StockBank = [']
    lines.extend(f"    {ticker!r}," for ticker in tickers)
    lines.append(']')
    STOCK_BANK_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def load_existing_downloads() -> list[str]:
    """Reuse only files produced with the current 252+30-day format."""
    existing: list[str] = []
    required_columns = {'Date', 'Close', 'NormalizedClose', 'Segment'}
    expected_segments = (
        ['history'] * HISTORY_TRADING_DAYS
        + ['forecast'] * FORECAST_TRADING_DAYS
    )
    for csv_path in DATA_DIR.glob('*.T.csv'):
        try:
            data = pd.read_csv(csv_path)
        except Exception:
            continue
        if (
            required_columns.issubset(data.columns)
            and len(data) == TOTAL_TRADING_DAYS
            and data['Segment'].tolist() == expected_segments
        ):
            existing.append(csv_path.stem)
    return existing[:TARGET_COUNT]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    random_generator = random.SystemRandom()
    downloaded_tickers = load_existing_downloads()
    random_generator.shuffle(downloaded_tickers)
    attempted: set[str] = set(downloaded_tickers)

    print(
        f'开始随机下载 {TARGET_COUNT} 只日本普通股票：每只随机起始日期，'
        f'{HISTORY_TRADING_DAYS} 个历史交易日 + '
        f'{FORECAST_TRADING_DAYS} 个未来交易日'
    )
    print(f'随机起始日期范围：{RANDOM_START_MIN} 至 {RANDOM_START_MAX}')
    print(f'CSV 保存目录：{DATA_DIR}')
    if downloaded_tickers:
        print(f'复用已完成的 {len(downloaded_tickers)} 个 CSV。')

    while (
        len(downloaded_tickers) < TARGET_COUNT
        and len(attempted) < MAX_ATTEMPTS
    ):
        ticker = f'{random_generator.randint(1300, 9999)}.T'
        if ticker in attempted:
            continue
        attempted.add(ticker)
        requested_start = random_start_date(random_generator)

        try:
            stock_data = prepare_stock_data(ticker, requested_start)
            if stock_data is None:
                continue

            output_path = DATA_DIR / f'{ticker}.csv'
            stock_data.to_csv(output_path, index=False, float_format='%.6f')
            downloaded_tickers.append(ticker)
            print(
                f'[{len(downloaded_tickers):03d}/{TARGET_COUNT}] '
                f'{ticker}: {stock_data.iloc[0]["Date"]} 至 '
                f'{stock_data.iloc[-1]["Date"]}，{len(stock_data)} 个交易日'
            )
        except Exception as error:
            print(f'跳过 {ticker}: {error}')
        finally:
            time.sleep(REQUEST_DELAY_SECONDS)

    if len(downloaded_tickers) != TARGET_COUNT:
        raise RuntimeError(
            f'尝试 {len(attempted)} 个代码后仅成功下载 '
            f'{len(downloaded_tickers)} 只股票；StockBank.py 未更新。'
        )

    write_stock_bank(downloaded_tickers)
    print(f'下载完成，StockBank 已写入：{STOCK_BANK_PATH}')


if __name__ == '__main__':
    main()
