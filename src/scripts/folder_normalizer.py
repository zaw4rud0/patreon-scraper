import os
import shutil


def normalize_month_folders(base_path):
    for year in os.listdir(base_path):
        year_path = os.path.join(base_path, year)
        if not os.path.isdir(year_path):
            continue

        # Collect month folders that need normalization
        months = [folder for folder in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, folder))]

        for month in months:
            try:
                month_int = int(month)
                normalized_month = f"{month_int:02d}"

                current_month_path = os.path.join(year_path, month)
                normalized_month_path = os.path.join(year_path, normalized_month)

                if normalized_month != month:
                    # If the normalized folder doesn't exist, rename
                    if not os.path.exists(normalized_month_path):
                        os.rename(current_month_path, normalized_month_path)
                    else:
                        # If the folder exists, move files into it
                        for file_name in os.listdir(current_month_path):
                            source_file = os.path.join(current_month_path, file_name)
                            dest_file = os.path.join(normalized_month_path, file_name)

                            # Overwrite files if they exist
                            if os.path.isfile(source_file):
                                shutil.move(source_file, dest_file)

                        os.rmdir(current_month_path)
            except ValueError:
                print(f"Skipping invalid folder: {month}")
