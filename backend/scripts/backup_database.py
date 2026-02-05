"""
Database backup automation script.
Supports SQLite database backup with retention policy.
"""
import shutil
import os
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Handles database backup and retention"""
    
    def __init__(self, db_path: str = "futuroforbes.db", backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Retention policy
        self.daily_retention = 7  # Keep 7 daily backups
        self.weekly_retention = 4  # Keep 4 weekly backups
        self.monthly_retention = 12  # Keep 12 monthly backups
    
    def create_backup(self, compress: bool = True) -> Path:
        """
        Create a database backup.
        
        Args:
            compress: Whether to compress the backup with gzip
            
        Returns:
            Path to the created backup file
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"3f_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✓ Created backup: {backup_path}")
            
            # Compress if requested
            if compress:
                compressed_path = self._compress_backup(backup_path)
                backup_path.unlink()  # Remove uncompressed file
                backup_path = compressed_path
                logger.info(f"✓ Compressed backup: {compressed_path}")
            
            # Verify backup integrity
            if self._verify_backup(backup_path):
                logger.info(f"✓ Backup verified successfully")
            else:
                logger.warning(f"⚠ Backup verification failed")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"✗ Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            raise
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup with gzip"""
        compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """Verify backup file integrity"""
        try:
            # For compressed files
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f:
                    # Try to read first few bytes
                    f.read(100)
            else:
                # For regular files, just check size
                if backup_path.stat().st_size == 0:
                    return False
            
            return True
        except Exception:
            return False
    
    def cleanup_old_backups(self):
        """
        Clean up old backups according to retention policy.
        Keeps:
        - Last 7 daily backups
        - Last 4 weekly backups (one per week)
        - Last 12 monthly backups (one per month)
        """
        all_backups = self._get_all_backups()
        
        if not all_backups:
            logger.info("No backups to clean up")
            return
        
        now = datetime.now()
        keep_backups = set()
        
        # Keep last 7 daily backups
        daily_backups = all_backups[:self.daily_retention]
        keep_backups.update(daily_backups)
        
        # Keep weekly backups (one per week)
        weekly_backups = self._get_weekly_backups(all_backups, self.weekly_retention)
        keep_backups.update(weekly_backups)
        
        # Keep monthly backups (one per month)
        monthly_backups = self._get_monthly_backups(all_backups, self.monthly_retention)
        keep_backups.update(monthly_backups)
        
        # Delete all backups not in keep list
        deleted_count = 0
        for backup in all_backups:
            if backup not in keep_backups:
                try:
                    backup.unlink()
                    deleted_count += 1
                    logger.info(f"✓ Deleted old backup: {backup.name}")
                except Exception as e:
                    logger.error(f"✗ Failed to delete {backup.name}: {e}")
        
        logger.info(f"✓ Cleanup complete. Deleted {deleted_count} old backups, kept {len(keep_backups)}")
    
    def _get_all_backups(self) -> List[Path]:
        """Get all backup files sorted by modification time (newest first)"""
        backups = list(self.backup_dir.glob("3f_backup_*.db*"))
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def _get_weekly_backups(self, backups: List[Path], count: int) -> List[Path]:
        """Get one backup per week"""
        weekly = []
        seen_weeks = set()
        
        for backup in backups:
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            week_key = (mtime.year, mtime.isocalendar()[1])
            
            if week_key not in seen_weeks:
                weekly.append(backup)
                seen_weeks.add(week_key)
                
                if len(weekly) >= count:
                    break
        
        return weekly
    
    def _get_monthly_backups(self, backups: List[Path], count: int) -> List[Path]:
        """Get one backup per month"""
        monthly = []
        seen_months = set()
        
        for backup in backups:
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            month_key = (mtime.year, mtime.month)
            
            if month_key not in seen_months:
                monthly.append(backup)
                seen_months.add(month_key)
                
                if len(monthly) >= count:
                    break
        
        return monthly
    
    def restore_backup(self, backup_path: Path):
        """
        Restore database from backup.
        
        WARNING: This will overwrite the current database!
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create a safety backup of current database
        if self.db_path.exists():
            safety_backup = self.db_path.with_suffix('.db.before_restore')
            shutil.copy2(self.db_path, safety_backup)
            logger.info(f"✓ Created safety backup: {safety_backup}")
        
        try:
            # Decompress if needed
            if backup_path.suffix == '.gz':
                temp_file = self.backup_dir / "temp_restore.db"
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_to_restore = temp_file
            else:
                backup_to_restore = backup_path
            
            # Restore database
            shutil.copy2(backup_to_restore, self.db_path)
            logger.info(f"✓ Database restored from: {backup_path}")
            
            # Cleanup temp file
            if backup_path.suffix == '.gz':
                temp_file.unlink()
                
        except Exception as e:
            logger.error(f"✗ Restore failed: {e}")
            # Try to restore safety backup
            if safety_backup.exists():
                shutil.copy2(safety_backup, self.db_path)
                logger.info("✓ Restored from safety backup")
            raise


def main():
    """Run backup manually"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database backup utility")
    parser.add_argument('--db', default='futuro forbes.db', help='Database file path')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--no-compress', action='store_true', help='Do not compress backups')
    parser.add_argument('--cleanup', action='store_true', help='Run cleanup after backup')
    
    args = parser.parse_args()
    
    # Setup logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    backup_manager = DatabaseBackup(args.db, args.backup_dir)
    
    try:
        backup_path = backup_manager.create_backup(compress=not args.no_compress)
        print(f"\n✓ Backup created: {backup_path}")
        
        if args.cleanup:
            print("\nRunning cleanup...")
            backup_manager.cleanup_old_backups()
        
        print("\n✓ Backup completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Backup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
