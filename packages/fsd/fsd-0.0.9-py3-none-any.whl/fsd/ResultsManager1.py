import os
import json
import subprocess

from fsd.util import utils

class ResultsManager1:
    def __init__(self):
        self.results = {}

    def update_dependencies_results(self, project_path, dependencies):
        self._update_category_results(project_path, "dependencies", dependencies)

    def update_total_results(self, project_path, file_path, summary):
        category, filename = self._get_category_and_filename(file_path)
        self._update_file_results(project_path, category, filename, summary)

    def update_results(self, project_path, file_path, summary):
        self.load_results_from_files(project_path)
        category, filename = self._get_category_and_filename(file_path)
        
        if category not in self.results:
            self.results[category] = {}
        
        if filename not in self.results[category] or self.results[category][filename] != summary:
            self.results[category][filename] = summary
            self.save_results_to_files(project_path)

    def save_results_to_files(self, project_path):
        output_dir = self._get_output_dir(project_path)
        os.makedirs(output_dir, exist_ok=True)

        for category, data in self.results.items():
            file_path = os.path.join(output_dir, f"{category}_results.txt")
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

        tree_path = os.path.join(output_dir, "tree.txt")
        with open(tree_path, 'w') as f:
            utils.tree(project_path, exclude="Zinley", stdout=f)

    def load_results_from_files(self, project_path):
        output_dir = self._get_output_dir(project_path)
        for file_name in os.listdir(output_dir):
            if file_name.endswith("_results.txt"):
                category = file_name.replace("_results.txt", "")
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, 'r') as f:
                    self.results[category] = json.load(f)

    def save_milestones_to_files(self, project_path):
        self.save_results_to_files(project_path)

    def get_results(self):
        return self.results

    def clear_results(self):
        self.results = {}

    def _update_category_results(self, project_path, category, data):
        self.results[category] = data
        self.save_results_to_files(project_path)

    def _update_file_results(self, project_path, category, filename, summary):
        if category not in self.results:
            self.results[category] = {}
        self.results[category][filename] = summary
        self.save_results_to_files(project_path)

    def _get_category_and_filename(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lstrip('.')
        filename = os.path.basename(file_path)
        category = f"{file_extension}_files"
        return category, filename

    def _get_output_dir(self, project_path):
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        project_name = os.path.basename(project_path)
        return os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")


class ResultsReader:
    def __init__(self, results_manager):
        self.results_manager = results_manager

    def read_results(self, category):
        return self.results_manager.get_results().get(category, None)


def create_dynamic_results_manager(file_extensions):
    manager = ResultsManager1()
    for ext in file_extensions:
        manager.update_results(None, f"{ext}.dummy", {})
    return manager