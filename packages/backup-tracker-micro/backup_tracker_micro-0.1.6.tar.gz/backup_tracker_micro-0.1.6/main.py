from src.backup_tracker_micro import BackupTracker, BackupEvent

b = BackupTracker("localhost", "Test", "http://localhost:5000/")

b.backup_event(BackupEvent.STARTED)
b.backup_status(100.01)
b.backup_event(BackupEvent.FINISHED)
res = b.get_backup_events(100)
print(res)
