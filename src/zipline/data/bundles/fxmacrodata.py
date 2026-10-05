"""
Module for building a daily FX dataset from FXMacroData.
"""

import logging
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

from . import core as bundles

log = logging.getLogger(__name__)

FXMACRODATA_API_URL = "https://api.fxmacrodata.com/v1/forex"
DEFAULT_SYMBOLS = "EURUSD,GBPUSD,USDJPY,AUDUSD"
# the API returns at most 100 rows per request, newest first
PAGE_LIMIT = 100
MAX_PAGES = 1000


def parse_symbols(environ):
    symbols = environ.get("FXMACRODATA_SYMBOLS", DEFAULT_SYMBOLS)
    return [
        symbol.strip().replace("/", "").replace("-", "").upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]


def split_pair(symbol):
    clean_symbol = symbol.replace("/", "").replace("-", "").upper()

    if len(clean_symbol) != 6:
        raise ValueError(
            "FXMacroData symbols must be six-letter FX pairs, for example EURUSD"
        )

    return clean_symbol[:3], clean_symbol[3:]


def format_fxmacrodata_url(symbol, start_date, end_date, offset=0):
    base, quote = split_pair(symbol)
    query = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "limit": PAGE_LIMIT,
        "offset": offset,
    }

    return f"{FXMACRODATA_API_URL}/{base.lower()}/{quote.lower()}?{urlencode(query)}"


def fxmacrodata_headers(api_key=None):
    api_key = (api_key or "").strip()
    if any(char.isspace() or not char.isprintable() for char in api_key):
        raise ValueError("FXMACRODATA_API_KEY contains invalid characters")
    if api_key:
        return {"X-API-Key": api_key}
    return {}


def fetch_fx_pair(symbol, start_date, end_date, api_key=None):
    rows = []
    offset = 0
    for _ in range(MAX_PAGES):
        url = format_fxmacrodata_url(symbol, start_date, end_date, offset)
        # Redirects are not followed, so the key never leaves this host.
        response = requests.get(
            url,
            headers=fxmacrodata_headers(api_key),
            timeout=30,
            allow_redirects=False,
        )
        if 300 <= response.status_code < 400:
            raise requests.HTTPError(
                f"FXMacroData returned an unexpected redirect "
                f"({response.status_code}) for {symbol}"
            )
        response.raise_for_status()
        payload = response.json()
        page = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(page, list):
            detail = payload.get("detail") if isinstance(payload, dict) else None
            raise ValueError(
                f"Unexpected FXMacroData response for {symbol}: "
                f"{detail or 'missing data list'}"
            )
        rows.extend(
            row
            for row in page
            if isinstance(row, dict) and "date" in row and "val" in row
        )

        pagination = payload.get("pagination")
        if (
            not page
            or not isinstance(pagination, dict)
            or not pagination.get("has_more")
        ):
            break
        offset = pagination.get("next_offset") or offset + len(page)

    if len(rows) == 0:
        raise ValueError(f"No FXMacroData rows returned for {symbol}")

    data = pd.DataFrame(rows)
    data["date"] = pd.to_datetime(data["date"])
    data["symbol"] = symbol
    data["open"] = data["val"].astype(float)
    data["high"] = data["val"].astype(float)
    data["low"] = data["val"].astype(float)
    data["close"] = data["val"].astype(float)
    data["volume"] = 0.0
    data = data.drop_duplicates("date").sort_values("date", ignore_index=True)

    return data[["symbol", "date", "open", "high", "low", "close", "volume"]]


def fetch_fxmacrodata_table(symbols, start_date, end_date, api_key, show_progress):
    frames = []

    for symbol in symbols:
        if show_progress:
            log.info("Downloading FXMacroData %s.", symbol)
        frames.append(fetch_fx_pair(symbol, start_date, end_date, api_key))

    return pd.concat(frames, ignore_index=True)


def gen_asset_metadata(data):
    asset_metadata = data.groupby(by="symbol").agg({"date": [np.min, np.max]})
    asset_metadata.reset_index(inplace=True)
    asset_metadata["start_date"] = asset_metadata.date[np.min.__name__]
    asset_metadata["end_date"] = asset_metadata.date[np.max.__name__]
    del asset_metadata["date"]
    asset_metadata.columns = asset_metadata.columns.get_level_values(0)
    asset_metadata["exchange"] = "FXMACRODATA"
    asset_metadata["auto_close_date"] = asset_metadata[
        "end_date"
    ].values + pd.Timedelta(days=1)
    return asset_metadata


def parse_pricing_and_vol(data, sessions, symbol_map):
    sessions = sessions.tz_localize(None)

    for asset_id, symbol in symbol_map.items():
        asset_data = data.xs(symbol, level=1).reindex(sessions).ffill().dropna()
        yield asset_id, asset_data


@bundles.register("fxmacrodata")
def fxmacrodata_bundle(
    environ,
    asset_db_writer,
    minute_bar_writer,
    daily_bar_writer,
    adjustment_writer,
    calendar,
    start_session,
    end_session,
    cache,
    show_progress,
    output_dir,
):
    """
    Build a daily FX spot bundle using FXMacroData's /v1/forex endpoint.

    Environment variables:

    - ``FXMACRODATA_SYMBOLS``: comma-separated FX pairs such as
      ``EURUSD,GBPUSD,USDJPY``.  Defaults to major USD pairs.
    - ``FXMACRODATA_API_KEY``: FXMacroData API key, sent in the
      ``X-API-Key`` request header.
    """
    symbols = parse_symbols(environ)
    api_key = environ.get("FXMACRODATA_API_KEY")

    raw_data = fetch_fxmacrodata_table(
        symbols, start_session, end_session, api_key, show_progress
    )
    asset_metadata = gen_asset_metadata(raw_data[["symbol", "date"]])

    exchanges = pd.DataFrame(
        data=[["FXMACRODATA", "FXMacroData", "US"]],
        columns=["exchange", "canonical_name", "country_code"],
    )
    asset_db_writer.write(equities=asset_metadata, exchanges=exchanges)

    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)

    raw_data.set_index(["date", "symbol"], inplace=True)
    daily_bar_writer.write(
        parse_pricing_and_vol(raw_data, sessions, symbol_map),
        show_progress=show_progress,
    )

    adjustment_writer.write()
