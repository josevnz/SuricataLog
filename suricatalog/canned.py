from __future__ import annotations

from pathlib import Path
from typing import List
import locale

from textual.app import App

from suricatalog.mini_apps import FlowApp, HostDataUse, TopUserApp, OneShotApp
from suricatalog.filter import BaseFilter

locale.setlocale(locale.LC_ALL, '')


def get_one_shot_flow_table(
        *,
        eve: List[Path],
        data_filter: BaseFilter
) -> App:
    flow_app = FlowApp(
        eve=eve,
        data_filter=data_filter
    )
    logs = ' '.join(map(lambda x: str(x), eve))
    flow_app.title = f"SuricataLog FLOW protocol, logs={logs}"
    return flow_app


def get_host_data_use(
        eve_files: List[Path],
        data_filter: BaseFilter,
        ip_address: any
) -> App:
    hdu = HostDataUse(
        eve=eve_files,
        data_filter=data_filter,
        ip_address=ip_address
    )
    hdu.title = f"SuricataLog Net-Flow for: {ip_address}"
    return hdu


def get_agents(
        eve_files: List[Path],
        data_filter: BaseFilter
) -> App:
    top_user_app = TopUserApp(
        eve=eve_files,
        data_filter=data_filter
    )
    top_user_app.title = f"SuricataLog User Agents"
    return top_user_app


def get_capture(
        *,
        eve: List[Path],
        data_filter: BaseFilter,
        title: str
) -> App:
    one_shot_app = OneShotApp(
        eve=eve,
        data_filter=data_filter
    )
    one_shot_app.title = f"{title}"
    return one_shot_app
