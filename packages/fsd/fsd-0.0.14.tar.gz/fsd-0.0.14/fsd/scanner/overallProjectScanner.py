import os

class overallProjectScanner:
    def __init__(self, project_path):
        self.project_path = project_path

    def get_files_by_extension(self, extensions):
        files = {ext: [] for ext in extensions}

        for root, dirs, filenames in os.walk(self.project_path):
            if 'Pods' in root:
                continue
            for file in filenames:
                file_ext = os.path.splitext(file)[1]
                if file_ext in extensions:
                    file_path = os.path.join(root, file)
                    files[file_ext].append(file_path)

        return files

    def get_file_contents(self, file_paths):
        contents = []
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                contents.append(f.read())
        return contents

    def get_storyboard_files(self):
        storyboard_files = self.get_files_by_extension(['.storyboard'])
        storyboard_contents = self.get_file_contents(storyboard_files['.storyboard'])

        return {
            "storyboard_files": storyboard_files['.storyboard'],
            "storyboard_contents": storyboard_contents
        }

    def get_swift_files(self):
        swift_files = self.get_files_by_extension(['.swift'])
        swift_contents = self.get_file_contents(swift_files['.swift'])

        return {
            "swift_files": swift_files['.swift'],
            "swift_contents": swift_contents
        }

    def get_xib_files(self):
        xib_files = self.get_files_by_extension(['.xib'])
        xib_contents = self.get_file_contents(xib_files['.xib'])

        return {
            "xib_files": xib_files['.xib'],
            "xib_contents": xib_contents
        }

    def get_nib_files(self):
        nib_files = self.get_files_by_extension(['.nib'])

        return {
            "nib_files": nib_files['.nib']
        }

    def get_objc_files(self):
        objc_files = self.get_files_by_extension(['.h', '.m'])
        objc_contents = {'.h': self.get_file_contents(objc_files['.h']),
                         '.m': self.get_file_contents(objc_files['.m'])}

        return {
            "objc_files": objc_files,
            "objc_contents": objc_contents
        }

    def determine_project_type(self):
        storyboard_results = self.get_storyboard_files()
        swift_results = self.get_swift_files()
        xib_results = self.get_xib_files()
        nib_results = self.get_nib_files()
        objc_results = self.get_objc_files()

        storyboard_count = len(storyboard_results["storyboard_files"])
        swift_count = len(swift_results["swift_files"])
        xib_count = len(xib_results["xib_files"])
        nib_count = len(nib_results["nib_files"])
        objc_count = len(objc_results["objc_files"]['.h']) + len(objc_results["objc_files"]['.m'])

        relevant_files_count = storyboard_count + swift_count + xib_count + nib_count + objc_count

        if relevant_files_count == 0:
            return "Unknown Project Type", 0, 0

        storyboard_percentage = (storyboard_count / relevant_files_count) * 100
        swiftui_percentage = (swift_count / relevant_files_count) * 100
        xib_percentage = (xib_count / relevant_files_count) * 100
        nib_percentage = (nib_count / relevant_files_count) * 100
        objc_percentage = (objc_count / relevant_files_count) * 100

        primary_type = max(
            ("Storyboard", storyboard_percentage),
            ("SwiftUI", swiftui_percentage),
            ("Xib", xib_percentage),
            ("Nib", nib_percentage),
            ("Objective-C", objc_percentage),
            key=lambda item: item[1]
        )[0]

        return {
            "primary_type": f"Primarily {primary_type} Project",
            "storyboard_percentage": storyboard_percentage,
            "swiftui_percentage": swiftui_percentage,
            "xib_percentage": xib_percentage,
            "nib_percentage": nib_percentage,
            "objc_percentage": objc_percentage,
            "details": {
                "storyboard_files": storyboard_results["storyboard_files"],
                "swift_files": swift_results["swift_files"],
                "xib_files": xib_results["xib_files"],
                "nib_files": nib_results["nib_files"],
                "objc_files": objc_results["objc_files"]
            }
        }
