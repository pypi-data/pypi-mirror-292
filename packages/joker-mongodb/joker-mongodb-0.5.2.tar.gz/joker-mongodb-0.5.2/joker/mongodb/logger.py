#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging

from pymongo.monitoring import (
    CommandListener,
    CommandStartedEvent,
    CommandSucceededEvent,
    CommandFailedEvent,
)


class MongoCommandLogger(CommandListener):
    _registered = False
    _logger = logging.getLogger("_mongodb")
    _level = logging.DEBUG

    @staticmethod
    def _fmt_opid(event):
        if event.request_id == event.operation_id:
            return event.request_id
        return "{}.{}".format(event.request_id, event.operation_id)

    @staticmethod
    def _fmt_url(event):
        addr = ":".join(str(s) for s in event.connection_id)
        return "{}/{}".format(addr, event.database_name)

    def started(self, event: CommandStartedEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            "started",
            self._fmt_url(event),
            event.command,
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)

    def succeeded(self, event: CommandSucceededEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            "succeeded",
            int(event.duration_micros / 1000),
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)

    def failed(self, event: CommandFailedEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            "failed",
            event.duration_micros,
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)
