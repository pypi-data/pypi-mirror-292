import os
import plistlib

class InfoPlistScanner:
    def __init__(self, project_path):
        self.project_path = project_path

    def scan_info_plist(self):
        plist_files = []
        for root, dirs, files in os.walk(self.project_path):
            if 'Pods' in root:
                continue
            for file in files:
                if file == "Info.plist":
                    plist_path = os.path.join(root, file)
                    with open(plist_path, 'rb') as f:
                        plist_content = plistlib.load(f)
                        plist_files.append((plist_path, plist_content))
        return plist_files
