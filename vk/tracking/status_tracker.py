# Copyright (c) 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "VK scripts" project.
# For details, see https://github.com/egor-tensin/vk-scripts.
# Distributed under the MIT License.

from collections.abc import Callable
import contextlib
import time
import signal

import vk.error
from vk.user import UserField


class StatusTracker:
    DEFAULT_TIMEOUT = 5

    def __init__(self, api, timeout=DEFAULT_TIMEOUT):
        self._api = api
        self._timeout = timeout
        self._on_initial_status = []
        self._on_status_update = []
        self._on_connection_error = []

    def _wait_after_connection_error(self):
        time.sleep(self._timeout)

    def add_database_writer(self, writer):
        self.add_initial_status_handler(writer.on_initial_status)
        self.add_status_update_handler(writer.on_status_update)
        self.add_connection_error_handler(writer.on_connection_error)

    def add_initial_status_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_initial_status.append(fn)

    def add_status_update_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_status_update.append(fn)

    def add_connection_error_handler(self, fn):
        self._assert_is_callback(fn)
        self._on_connection_error.append(fn)

    @staticmethod
    def _assert_is_callback(fn):
        if not isinstance(fn, Callable):
            raise TypeError()

    _USER_FIELDS = UserField.DOMAIN, UserField.ONLINE, UserField.LAST_SEEN,

    def _query_status(self, uids):
        user_list = self._api.users_get(uids, self._USER_FIELDS,
                                        deactivated_users=False)
        return {user.get_uid(): user for user in user_list}

    def _notify_status(self, user):
        for fn in self._on_initial_status:
            fn(user)

    def _notify_status_update(self, user):
        for fn in self._on_status_update:
            fn(user)

    def _notify_connection_error(self, e):
        for fn in self._on_connection_error:
            fn(e)

    def _query_initial_status(self, uids):
        while True:
            try:
                return self._query_status(uids)
            except vk.error.APIConnectionError as e:
                self._notify_connection_error(e)
                self._wait_after_connection_error()

    def _query_status_updates(self, uids):
        while True:
            self._wait_after_connection_error()
            try:
                return self._query_status(uids)
            except vk.error.APIConnectionError as e:
                self._notify_connection_error(e)

    @staticmethod
    def _filter_status_updates(old_users, new_users):
        for uid, user in new_users.items():
            if old_users[uid].is_online() != user.is_online():
                old_users[uid] = user
                yield user

    def query_status(self, uids):
        users = self._query_initial_status(uids)
        for user in users.values():
            self._notify_status(user)
        return users

    def _do_loop(self, uids):
        users = self.query_status(uids)
        while True:
            updated_users = self._query_status_updates(uids)
            for user in self._filter_status_updates(users, updated_users):
                self._notify_status_update(user)

    class StopLooping(RuntimeError):
        pass

    @staticmethod
    def _stop_looping(signo, frame):
        raise StatusTracker.StopLooping()

    @staticmethod
    @contextlib.contextmanager
    def _handle_signal(signo, handler):
        old_handler = signal.getsignal(signo)
        signal.signal(signo, handler)
        try:
            yield
        finally:
            signal.signal(signal.SIGINT, old_handler)

    @staticmethod
    def _handle_sigint():
        # Python doesn't raise KeyboardInterrupt in case a real SIGINT is sent
        # from outside, surprisingly.
        return StatusTracker._handle_signal(signal.SIGINT,
                                            StatusTracker._stop_looping)

    @staticmethod
    def _handle_sigterm():
        return StatusTracker._handle_signal(signal.SIGTERM,
                                            StatusTracker._stop_looping)

    def loop(self, uids):
        with self._handle_sigint(), self._handle_sigterm():
            try:
                self._do_loop(uids)
            except (KeyboardInterrupt, StatusTracker.StopLooping):
                pass
