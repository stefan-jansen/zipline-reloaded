"""
Sandbank용 bundle
"""
import os
import sys

from logbook import Logger, StreamHandler
from numpy import empty
from pandas import DataFrame, Index, Timedelta, NaT, read_parquet
from zipline.utils.calendar_utils import register_calendar_alias
import boto3

from zipline.utils.cli import maybe_show_progress

from . import core as bundles

handler = StreamHandler(sys.stdout, format_string=" | {record.message}")
logger = Logger(__name__)
logger.handlers.append(handler)


def crypto_ingest(tframes=None, dir=None, instType='FUTURES'):
    """
    기존에 비해 추가로 instType을 넣어서 분류할 수도 잇음
    Generate an ingest function for custom data bundle
    This function can be used in ~/.zipline/extension.py
    to register bundle with custom parameters, e.g. with
    a custom trading calendar.

    Parameters
    ----------
    tframes: tuple, optional
        The data time frames, supported timeframes: 'daily' and 'minute'
    csvdir : string, optional, default: CSVDIR environment variable
        The path to the directory of this structure:
        <directory>/<timeframe1>/<symbol1>.csv
        <directory>/<timeframe1>/<symbol2>.csv
        <directory>/<timeframe1>/<symbol3>.csv
        <directory>/<timeframe2>/<symbol1>.csv
        <directory>/<timeframe2>/<symbol2>.csv
        <directory>/<timeframe2>/<symbol3>.csv

    Returns
    -------
    ingest : callable
        The bundle ingest function

    Examples
    --------
    This code should be added to ~/.zipline/extension.py
    .. code-block:: python
       from zipline.data.bundles import csvdir_equities, register
       register('custom-csvdir-bundle',
                csvdir_equities(["daily", "minute"],
                '/full/path/to/the/csvdir/directory'))
    """

    return SandBankBundle(tframes, dir, instType).ingest


class SandBankBundle:
    """
    Wrapper class to call sandbank_bundle with provided
    list of time frames and a path to the csvdir directory
    """

    def __init__(self, tframes=None, dir=None, instType='FUTURES'):
        self.tframes = tframes
        self.dir = dir
        self.instType = instType

    def ingest(
        self,
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

        sandbank_bundle(
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
            self.tframes,
            self.dir,
            self.instType
        )


@bundles.register("sandbank")
def sandbank_bundle(
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
    tframes=None,
    dir=None,
    instType='FUTURES',
):
    """
    Build a zipline data bundle from the directory with csv files.
    """
    if not dir:
        dir = environ.get("SANDBANK")
        if not dir:
            raise ValueError("SANDBANK environment variable is not set")

    if not os.path.isdir(dir):
        if dir[:2]=='s3':
            is_s3_path = True
        else:
            raise ValueError("%s is not a directory" % dir)

    if not tframes:
        tframes = set(["daily", "minute"]).intersection(os.listdir(dir))

        if not tframes:
            raise ValueError(
                "'daily' and 'minute' directories " "not found in '%s'" % dir
            )

    divs_splits = {
        "divs": DataFrame(
            columns=[
                "sid",
                "amount",
                "ex_date",
                "record_date",
                "declared_date",
                "pay_date",
            ]
        ),
        "splits": DataFrame(columns=["sid", "ratio", "effective_date"]),
    }
    
    for tframe in tframes:
        if is_s3_path:
            ddir = dir + "/" + tframe
            pg = boto3.client('s3').get_paginator('list_objects_v2')
            bucket = ddir.split('/')[2]
            prefix = "/".join(ddir.split('/')[3:]) + '/'
            iterator = pg.paginate(Bucket=bucket, Prefix=prefix)
            symbols = []
            files = []
            for page in iterator:
                for content in page['Contents']:
                    if ".gzip" in content['Key']:
                        symbols.append(content['Key'].split('/')[-1].split('.gzip')[0])
                        files.append(content['Key'].split(prefix)[1])

        else:
            ddir = os.path.join(dir, tframe)
            symbols = sorted(
                item.split(".gzip")[0] for item in os.listdir(ddir) if ".gzip" in item
            )
            files = os.listdir(dir)
        if not symbols:
            raise ValueError("no <symbol>.gzip* files found in %s" % ddir)

        
        if instType == 'FUTURES':
            dtype = [
                ("start_date", "datetime64[ns]"),
                ("end_date", "datetime64[ns]"),
                ("auto_close_date", "datetime64[ns]"),
                ("symbol", "object"),
                ("root_symbol", "object"),
                ("asset_name", "object"),
                ("first_traded", "datetime64[ns]"),
                ("exchange", "object"),
                ("notice_date", "datetime64[ns]"),
                ("expiration_date", "datetime64[ns]"),
                ("tick_size", "float"),
                ("multiplier", "float"),
            ]
            
        else:
            dtype = [
            ("start_date", "datetime64[ns]"),
            ("end_date", "datetime64[ns]"),
            ("auto_close_date", "datetime64[ns]"),
            ("symbol", "object"),
            ]
            root_symbols = None
            

        metadata = DataFrame(empty(len(symbols), dtype=dtype))

        if tframe == "minute":
            writer = minute_bar_writer
        else:
            writer = daily_bar_writer

        # symbol별 가격 데이터 입력 + asset meta 데이터에 넣을 universe 작성
        roots = {"num" : 0}
        
        writer.write(
            _pricing_iter(ddir, symbols, metadata, divs_splits, show_progress, instType, roots, files),
            show_progress=show_progress,
        )


        exchanges = DataFrame(
            data=[["CRYPTO", "CRYPTO", "0"]],
            columns=["exchange", "canonical_name", "country_code"],
            )
        metadata["exchange"] = "CRYPTO"

        
        if instType in ['FUTURES', 'PERPETUAL']:
            del roots['num']
            root_symbols = (DataFrame(
                list(roots.values()), 
                columns=[
                    'root_symbol_id', 'root_symbol', 
                    'sector', 'description', 'exchange'])
                .astype({'root_symbol_id' : 'int', 
                        'root_symbol' : 'object', 
                        'sector' : 'object', 
                        'description' : 'object',
                        'exchange' : 'object'}))
            asset_db_writer.write(futures=metadata, exchanges=exchanges, root_symbols=root_symbols)
        else:
            asset_db_writer.write(equities=metadata, exchanges=exchanges)

        divs_splits["divs"]["sid"] = divs_splits["divs"]["sid"].astype(int)
        divs_splits["splits"]["sid"] = divs_splits["splits"]["sid"].astype(int)
        adjustment_writer.write(
            splits=divs_splits["splits"], dividends=divs_splits["divs"]
        )


def _pricing_iter(dir, symbols, metadata, divs_splits, show_progress, instType, roots, files):
    with maybe_show_progress(
        symbols, show_progress, label="Loading custom pricing data: "
    ) as it:
        
        for sid, symbol in enumerate(it):
            logger.debug("%s: sid %s" % (symbol, sid))

            
            try:
                fname = [fname for fname in files if "%s.gzip" % symbol in fname][0]
            except IndexError:
                raise ValueError("%s.gzip file is not in %s" % (symbol, dir))
            
            # gzip 파일 받아오기
            dfr = read_parquet(os.path.join(dir, fname)).sort_index()

            start_date = dfr.index[0]
            end_date = dfr.index[-1]

            # Auto close : 종목의 상장 폐지가 발생하는 경우 처분하는 날짜
            ac_date = end_date

            if instType in ['FUTURES', 'SWAP']:
                root_symbol = "".join(symbol.split('/')[:2])
                if root_symbol not in roots: 
                    roots[root_symbol] = [roots["num"], root_symbol, "", "", "CRYPTO"]
                    roots['num']+=1 
                
                tick_size = dfr['tick_size'].unique()[0]
                multiplier = dfr['multiplier'].unique()[0]
                notice_date=expiration_date=end_date
                metadata.iloc[sid] = (
                    start_date, end_date, ac_date, symbol,
                    root_symbol, symbol, start_date, "CRYPTO",
                    notice_date, expiration_date, tick_size, multiplier
                )
            else:
                metadata.iloc[sid] = start_date, end_date, ac_date, symbol

            # split, dividend 관련 정보를 입력함.
            if "split" in dfr.columns:
                tmp = 1.0 / dfr[dfr["split"] != 1.0]["split"]
                split = DataFrame(data=tmp.index.tolist(), columns=["effective_date"])
                split["ratio"] = tmp.tolist()
                split["sid"] = sid

                splits = divs_splits["splits"]
                index = Index(range(splits.shape[0], splits.shape[0] + split.shape[0]))
                split.set_index(index, inplace=True)
                divs_splits["splits"] = splits.append(split)

            if "dividend" in dfr.columns:
                # ex_date   amount  sid record_date declared_date pay_date
                tmp = dfr[dfr["dividend"] != 0.0]["dividend"]
                div = DataFrame(data=tmp.index.tolist(), columns=["ex_date"])
                div["record_date"] = NaT
                div["declared_date"] = NaT
                div["pay_date"] = NaT
                div["amount"] = tmp.tolist()
                div["sid"] = sid

                divs = divs_splits["divs"]
                ind = Index(range(divs.shape[0], divs.shape[0] + div.shape[0]))
                div.set_index(ind, inplace=True)
                divs_splits["divs"] = divs.append(div)

            yield sid, dfr


register_calendar_alias("SANDBANK", "CRYPTO")
