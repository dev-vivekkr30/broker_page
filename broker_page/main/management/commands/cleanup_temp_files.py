from django.core.management.base import BaseCommand
import os
import tempfile
import shutil

class Command(BaseCommand):
    help = 'Clean up orphaned temporary files from abandoned registrations'

    def handle(self, *args, **options):
        temp_dir = tempfile.gettempdir()
        cleaned_count = 0
        
        # Look for temporary directories that might contain our files
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and item.startswith('tmp'):
                try:
                    # Check if directory is empty or contains only our temp files
                    files = os.listdir(item_path)
                    if len(files) <= 2:  # profile_photo and/or profile_video
                        for file in files:
                            if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov')):
                                file_path = os.path.join(item_path, file)
                                os.remove(file_path)
                                self.stdout.write(f"Removed temporary file: {file_path}")
                        os.rmdir(item_path)
                        cleaned_count += 1
                except Exception as e:
                    self.stdout.write(f"Error cleaning {item_path}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {cleaned_count} temporary directories')
        ) 