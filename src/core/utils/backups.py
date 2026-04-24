import os
import shutil
import datetime
import logging

logger = logging.getLogger(__name__)

def perform_rolling_backup(src, dst_dir, max_backups=5):
    if not os.path.exists(src):
        return
    os.makedirs(dst_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bp = os.path.join(dst_dir, f"backup_{ts}")
    try:
        shutil.copytree(src, bp)
        logger.info(f"Backup: {bp}")
        bs = sorted(
            [
                os.path.join(dst_dir, d)
                for d in os.listdir(dst_dir)
                if d.startswith("backup_")
            ],
            key=os.path.getctime,
        )
        while len(bs) > max_backups:
            oldest = bs.pop(0)
            shutil.rmtree(oldest)
            logger.info(f"Removed: {oldest}")
        return bp
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

def list_backups(dst_dir):
    if not os.path.exists(dst_dir):
        return []
    backups = []
    for d in os.listdir(dst_dir):
        if d.startswith("backup_"):
            full_path = os.path.join(dst_dir, d)
            backups.append({
                'path': full_path,
                'name': d,
                'timestamp': os.path.getctime(full_path)
            })
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

def restore_backup(backup_path, dst):
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(backup_path, dst)
        logger.info(f"Restored from: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False
