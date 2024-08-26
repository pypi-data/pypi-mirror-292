import os
import json
import subprocess

from util import utils

class ResultsManager:
    def __init__(self):
        self.results = {
            "images": {},
            "nib_files": {},
            "storyboard_files": {},
            "objc_files": {},
            "plist_files": {},
            "swift_files": {}
        }

    def update_results(self, category, data):
        self.results[category] = data

    def save_results_to_files(self, project_path, analysis):
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley",
                                  "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)

        for category, data in self.results.items():
            if category == "images":
                if 'usable_images' in data and data['usable_images']:
                    usable_images_path = os.path.join(output_dir, "usable_images_results.txt")
                    with open(usable_images_path, 'w') as f:
                        f.write(json.dumps(data['usable_images'], indent=4))
                if 'unusable_images' in data and data['unusable_images']:
                    unusable_images_path = os.path.join(output_dir, "unusable_images_results.txt")
                    with open(unusable_images_path, 'w') as f:
                        f.write(json.dumps(data['unusable_images'], indent=4))
            else:
                if data:  # Only write if there is data found
                    file_path = os.path.join(output_dir, f"{category}_results.txt")
                    with open(file_path, 'w') as f:
                        f.write(json.dumps(data, indent=4))

        project_overall_description = (
            f"Project Type: {analysis['project_type']}\n"
            f"Storyboard Percentage: {analysis['storyboard_percentage']:.2f}%\n"
            f"SwiftUI Percentage: {analysis['swiftui_percentage']:.2f}%\n"
            f"XIB Percentage: {analysis['xib_percentage']:.2f}%\n"
            f"NIB Percentage: {analysis['nib_percentage']:.2f}%\n"
            f"Objective-C Percentage: {analysis['objc_percentage']:.2f}%\n"
        )

        overall_desc_path = os.path.join(output_dir, "project_overall_description.txt")
        with open(overall_desc_path, 'w') as f:
            f.write(project_overall_description)

        # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
        tree_path = os.path.join(output_dir, "tree.txt")
        with open(tree_path, 'w') as f:
            utils.tree(project_path, exclude="Zinley", stdout=f)

    def load_results_from_files(self, project_path):
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        # output_dir = os.path.join(project_path, "Zinley", "Project_analysis")

        for category in self.results.keys():
            file_path = os.path.join(output_dir, f"{category}_results.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.results[category] = json.load(f)

        # Load images separately
        images_usable_path = os.path.join(output_dir, "usable_images_results.txt")
        images_unusable_path = os.path.join(output_dir, "unusable_images_results.txt")
        if os.path.exists(images_usable_path):
            with open(images_usable_path, 'r') as f:
                self.results["images"]["usable_images"] = json.load(f)
        if os.path.exists(images_unusable_path):
            with open(images_unusable_path, 'r') as f:
                self.results["images"]["unusable_images"] = json.load(f)

    def save_milestones_to_files(self, project_path, analysis):
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)

        for category, data in self.results.items():
            if category == "images":
                if 'usable_images' in data and data['usable_images']:
                    usable_images_path = os.path.join(output_dir, "usable_images_results.txt")
                    with open(usable_images_path, 'w') as f:
                        f.write(json.dumps(data['usable_images'], indent=4))
                if 'unusable_images' in data and data['unusable_images']:
                    unusable_images_path = os.path.join(output_dir, "unusable_images_results.txt")
                    with open(unusable_images_path, 'w') as f:
                        f.write(json.dumps(data['unusable_images'], indent=4))
            else:
                if data:  # Only write if there is data found
                    file_path = os.path.join(output_dir, f"{category}_results.txt")
                    with open(file_path, 'w') as f:
                        f.write(json.dumps(data, indent=4))

        # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
        tree_path = os.path.join(output_dir, "tree.txt")
        with open(tree_path, 'w') as f:
            utils.tree(project_path, exclude="Zinley", stdout=f)

    def load_results_from_files(self, project_path):
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        # output_dir = os.path.join(project_path, "Zinley", "Project_analysis")

        for category in self.results.keys():
            file_path = os.path.join(output_dir, f"{category}_results.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.results[category] = json.load(f)

        # Load images separately
        images_usable_path = os.path.join(output_dir, "usable_images_results.txt")
        images_unusable_path = os.path.join(output_dir, "unusable_images_results.txt")
        if os.path.exists(images_usable_path):
            with open(images_usable_path, 'r') as f:
                self.results["images"]["usable_images"] = json.load(f)
        if os.path.exists(images_unusable_path):
            with open(images_unusable_path, 'r') as f:
                self.results["images"]["unusable_images"] = json.load(f)

    def get_results(self):
        return self.results

    def clear_results(self):
        self.results = {
            "images": {},
            "nib_files": {},
            "storyboard_files": {},
            "objc_files": {},
            "plist_files": {},
            "swift_files": {}
        }


class ResultsReader:
    def __init__(self, results_manager):
        self.results_manager = results_manager

    def read_results(self, category):
        return self.results_manager.get_results().get(category, None)