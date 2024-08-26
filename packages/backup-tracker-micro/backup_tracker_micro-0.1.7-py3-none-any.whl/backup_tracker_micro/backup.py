
import json

from enum import Enum

from rest_client_micro import BaseRESTAPI


class BackupEvent(Enum):
    STARTED = "started"
    FINISHED = "finished"


class BackupTracker(BaseRESTAPI):

    host: str
    service: str
    uid: str

    def __init__(self, host: str, service: str, root_endpoint: str, uid: str = '', config_dir: str = None, cache_dir: str = None) -> None:
        app_name = "BackupTrackerMicro"
        user_agent = "BackupTracker (0.1.0)"
        use_cache = False
        force_cache = True
        sleep_ms = 25
        basic_auth = None
        cache_timeout_mins = 0
        super().__init__(app_name, root_endpoint, user_agent, sleep_ms, basic_auth,
                         config_dir, cache_dir, cache_timeout_mins, force_cache, use_cache)
        if uid == '':
            self.uid = self._get_id()['result']
        else:
            self.uid = uid
        self.host = host
        self.service = service

    def get_backup_status(self, rows: int) -> list:
        e = "backup/status"
        p = {
            "rows": rows
        }
        res = self._run_rest(e, p, "get", None)
        if res.error:
            print(res.error_text)
            return ''
        return json.loads(res.response)

    def get_backup_status_by_uid(self, uid) -> None:
        e = "backup/status"
        p = {
            "uid": uid
        }
        res = self._run_rest(e, p, "get", None)
        if res.error:
            print(res.error_text)
            return ''
        return ""

    def backup_status(self, size) -> None:
        e = "backup/status"
        p = {
            "uid": self.uid,
            "size": size
        }
        res = self._run_rest(e, p, "post", None)
        if res.error:
            print(res.error_text)
            return ''
        return ""

    def get_backup_events(self, rows: int) -> list:
        e = "backup"
        p = {
            "rows": rows
        }
        res = self._run_rest(e, p, "get", None)
        if res.error:
            print(res.error_text)
            return ''
        return json.loads(res.response)
    
    def get_backup_events_by_time(self, time: float) -> list:
        e = "backup/time"
        p = {
            "time": time
        }
        res = self._run_rest(e, p, "get", None)
        if res.error:
            print(res.error_text)
            return ''
        return json.loads(res.response)

    def backup_event(self, event: BackupEvent) -> None:
        e = f"backup/{event.value}"
        p = {
            "host": self.host,
            "service": self.service,
            "uid": self.uid
        }
        res = self._run_rest(e, p, "post", None)
        if res.error:
            print(res.error_text)
            return ''
        return self.uid

    def _get_id(self) -> dict:
        e = "backup/uid"
        p = {}
        res = self._run_rest(e, p, "get", None)
        if res.error:
            print(res.error_text)
            return ''
        # print(res.response)
        return json.loads(res.response)
