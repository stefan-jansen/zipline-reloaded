import io
import tarfile

import pandas as pd
import pytest

from zipline.data import bundles
from zipline.data.bundles import quandl
from zipline.data.bundles.core import to_bundle_ingest_dirname


@pytest.fixture
def archive_ingestion(tmp_path, monkeypatch):
    timestamp = pd.Timestamp("2025-01-01", tz="UTC")
    name = to_bundle_ingest_dirname(timestamp.tz_localize(None))
    destination = tmp_path / "data" / "quantopian-quandl" / name

    def ingest(member):
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w:gz") as archive:
            archive.addfile(member, io.BytesIO(b"data") if member.isfile() else None)
        payload.seek(0)
        monkeypatch.setattr(quandl, "download_without_progress", lambda *a: payload)
        bundles.ingest(
            "quantopian-quandl",
            environ={"ZIPLINE_ROOT": str(tmp_path)},
            timestamp=timestamp,
        )

    return ingest, destination


@pytest.mark.skipif(
    not hasattr(tarfile, "data_filter"), reason="Python lacks secure archive extraction"
)
@pytest.mark.parametrize("kind", ["parent", "sibling_prefix", "symlink", "hardlink"])
def test_bundle_ingestion_rejects_archive_escape(archive_ingestion, kind):
    ingest, destination = archive_ingestion
    outside = destination.parent / (destination.name + "-other") / "escaped"
    escape = "../" + destination.name + "-other/escaped"
    member = tarfile.TarInfo(escape if kind == "sibling_prefix" else "../escaped")
    member.size = 4
    if kind in ("symlink", "hardlink"):
        member.name = "link"
        member.type = tarfile.SYMTYPE if kind == "symlink" else tarfile.LNKTYPE
        member.linkname = str(outside)
        member.size = 0
        if kind == "hardlink":
            outside.parent.mkdir(parents=True)
            outside.write_bytes(b"keep")
    with pytest.raises(tarfile.FilterError):
        ingest(member)
    assert not (destination.parent / "escaped").exists()
    assert not (destination / "link").exists()
    if kind == "hardlink":
        assert outside.read_bytes() == b"keep"
    else:
        assert not outside.exists()


@pytest.mark.skipif(
    not hasattr(tarfile, "data_filter"), reason="Python lacks secure archive extraction"
)
def test_bundle_ingestion_preserves_safe_archive_files(archive_ingestion):
    ingest, destination = archive_ingestion
    member = tarfile.TarInfo("nested/bundle-data")
    member.size = 4
    ingest(member)
    assert (destination / "nested/bundle-data").read_bytes() == b"data"


def test_bundle_ingestion_requires_secure_archive_runtime(
    archive_ingestion, monkeypatch
):
    ingest, destination = archive_ingestion
    monkeypatch.delattr(tarfile, "data_filter", raising=False)
    member = tarfile.TarInfo("../escaped")
    member.size = 4
    with pytest.raises(RuntimeError, match="requires a Python security update"):
        ingest(member)
    assert not (destination.parent / "escaped").exists()
    assert not (destination / "assets-7.sqlite").exists()
