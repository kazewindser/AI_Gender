"""Randomly download Japanese stock-price series for the experiment.

Each successful ticker is saved as ``TSdata/<ticker>.csv`` and the complete
set of downloaded ticker codes is written to ``StockBank.py``.
"""

from pathlib import Path
import random
import time

import pandas as pd
import yfinance as yf


TARGET_COUNT = 200
START_DATE = '2025-01-01'
# yfinance treats end as exclusive, so this includes 2026-01-31.
DOWNLOAD_END_DATE = '2026-02-01'
MIN_OBSERVATIONS = 240
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


def prepare_stock_data(ticker: str) -> pd.DataFrame | None:
    downloaded = yf.download(
        ticker,
        start=START_DATE,
        end=DOWNLOAD_END_DATE,
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=False,
    )
    if downloaded.empty or 'Close' not in downloaded:
        return None

    close = extract_close(downloaded, ticker)
    if len(close) < MIN_OBSERVATIONS:
        return None

    # January 1 is a market holiday. Use the first available trading day's
    # close as the base value and normalize it to 100.
    base_close = float(close.iloc[0])
    if not pd.notna(base_close) or base_close <= 0:
        return None

    return pd.DataFrame(
        {
            'Date': pd.to_datetime(close.index).strftime('%Y-%m-%d'),
            'Close': close.to_numpy(dtype=float),
            'NormalizedClose': close.to_numpy(dtype=float) / base_close * 100,
        }
    )


def write_stock_bank(tickers: list[str]) -> None:
    lines = ['StockBank = [']
    lines.extend(f"    {ticker!r}," for ticker in tickers)
    lines.append(']')
    STOCK_BANK_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def load_existing_downloads() -> list[str]:
    """Reuse valid files from an interrupted run instead of downloading twice."""
    existing: list[str] = []
    required_columns = {'Date', 'Close', 'NormalizedClose'}
    for csv_path in DATA_DIR.glob('*.T.csv'):
        try:
            data = pd.read_csv(csv_path)
        except Exception:
            continue
        if required_columns.issubset(data.columns) and len(data) >= MIN_OBSERVATIONS:
            existing.append(csv_path.stem)
    return existing[:TARGET_COUNT]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    random_generator = random.SystemRandom()
    downloaded_tickers = load_existing_downloads()
    random_generator.shuffle(downloaded_tickers)
    attempted: set[str] = set(downloaded_tickers)

    print(
        f'开始随机下载 {TARGET_COUNT} 只日本股票：'
        f'{START_DATE} 至 2026-01-31'
    )
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

        try:
            stock_data = prepare_stock_data(ticker)
            if stock_data is None:
                continue

            output_path = DATA_DIR / f'{ticker}.csv'
            stock_data.to_csv(output_path, index=False, float_format='%.6f')
            downloaded_tickers.append(ticker)
            print(
                f'[{len(downloaded_tickers):03d}/{TARGET_COUNT}] '
                f'{ticker}: {len(stock_data)} 个交易日'
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
