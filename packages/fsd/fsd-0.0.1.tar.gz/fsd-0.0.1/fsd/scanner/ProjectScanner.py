import os
import aiohttp
import asyncio
import json
import plistlib

from .ImageScanner import ImageScanner
from .InfoPlistScanner import InfoPlistScanner
from .NibScanner import NibScanner
from .ObjectiveCScanner import ObjectiveCScanner
from .PlistScanner import PlistScanner
from .StoryboardScanner import StoryboardScanner
from .SwiftScanner import SwiftScanner
from .XibScanner import XibScanner
from .overallProjectScanner import overallProjectScanner


class ProjectScanner:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens):
        self.project_path = project_path
        self.info_plist_scanner = InfoPlistScanner(project_path)
        self.overall_project_scanner = overallProjectScanner(project_path)
        self.image_scanner = ImageScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.swift_scanner = SwiftScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.objc_scanner = ObjectiveCScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.xib_scanner = XibScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.nib_scanner = NibScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.plist_scanner = PlistScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
        self.storyboard_scanner = StoryboardScanner(project_path, api_key, endpoint, deployment_id, max_tokens)

    def analyze_project(self):
        """
        Analyze the overall project to gather various statistics and file lists.

        Returns:
            dict: Dictionary containing project type analysis, percentages, and file lists.
        """
        project_analysis = self.overall_project_scanner.determine_project_type()
        storyboard_files = self.overall_project_scanner.get_storyboard_files()
        swift_files = self.overall_project_scanner.get_swift_files()
        xib_files = self.overall_project_scanner.get_xib_files()
        nib_files = self.overall_project_scanner.get_nib_files()
        objc_files = self.overall_project_scanner.get_objc_files()
        image_files = self.image_scanner.scan_files_in_project()
        plist_files = self.info_plist_scanner.scan_info_plist()

        return {
            "project_type": project_analysis["primary_type"],
            "storyboard_percentage": project_analysis["storyboard_percentage"],
            "swiftui_percentage": project_analysis["swiftui_percentage"],
            "xib_percentage": project_analysis["xib_percentage"],
            "nib_percentage": project_analysis["nib_percentage"],
            "objc_percentage": project_analysis["objc_percentage"],
            "storyboard_files": storyboard_files,
            "swift_files": swift_files,
            "xib_files": xib_files,
            "nib_files": nib_files,
            "objc_files": objc_files,
            "image_files": image_files,
            "plist_files": plist_files
        }

    async def analyze_project_images(self):
        """
        Get images in the project by scanning files and return the scanned results.

        Returns:
            dict: Dictionary containing usable and unusable image descriptions.
        """
        images = self.image_scanner.scan_files_in_project()
        return await self.get_images_scanned_result(images)

    async def get_images_scanned_result(self, images):
        """
        Analyze images in the project by scanning and getting descriptions.

        Args:
            images (list): List of image files to be analyzed.

        Returns:
            dict: Dictionary containing usable and unusable image descriptions.
        """
        descriptions = await self.image_scanner.get_image_descriptions(images)

        # Identify failed images for reprocessing due to JSON decode errors
        failed_images = [desc for desc in descriptions["unusable_images"] if desc.get("reason") == "Failed to decode JSON response"]
        if failed_images:
            reprocessed_descriptions = await self.image_scanner.reprocess_failed_images(failed_images)
            # Combine successful descriptions with reprocessed descriptions
            descriptions["unusable_images"] = [desc for desc in descriptions["unusable_images"] if "description" in desc] + reprocessed_descriptions

        return descriptions


    async def analyze_swift_files(self):
        """
        Analyze Swift files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        swift_files = self.swift_scanner.scan_files_in_project()
        return await self.get_swift_files_summaries(swift_files)

    async def get_swift_files_summaries(self, swift_files):
        """
        Get summaries for Swift files by scanning and reprocessing if necessary.

        Args:
            swift_files (list): List of Swift files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.swift_scanner.get_file_summaries(swift_files)

        # Identify failed files for reprocessing
        failed_files = [summary for summary in summaries if "reason" in summary]

        return summaries


    async def analyze_plist_files(self):
        """
        Analyze plist files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        plist_files = self.plist_scanner.scan_files_in_project()
        return await self.get_plist_files_summaries(plist_files)

    async def get_plist_files_summaries(self, plist_files):
        """
        Get summaries for plist files by scanning and reprocessing if necessary.

        Args:
            plist_files (list): List of plist files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.plist_scanner.get_file_summaries(plist_files)

        # Identify failed files for reprocessing
        failed_files = [summary for summary in summaries if "reason" in summary]

        return summaries


    async def analyze_objc_files(self):
        """
        Analyze Objective-C files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        objc_files = self.objc_scanner.scan_files_in_project()
        return await self.get_objc_files_summaries(objc_files)

    async def get_objc_files_summaries(self, objc_files):
        """
        Get summaries for Objective-C files by scanning and reprocessing if necessary.

        Args:
            objc_files (list): List of Objective-C files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.objc_scanner.get_file_summaries(objc_files)

        # Identify failed files for reprocessing
        failed_files = [summary for summary in summaries if "reason" in summary]

        return summaries


    async def analyze_xib_files(self):
        """
        Analyze XIB files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        xib_files = self.xib_scanner.scan_files_in_project()
        return await self.get_xib_files_summaries(xib_files)

    async def get_xib_files_summaries(self, xib_files):
        """
        Get summaries for XIB files by scanning and reprocessing if necessary.

        Args:
            xib_files (list): List of XIB files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.xib_scanner.get_file_summaries(xib_files)

        # Identify failed files for reprocessing
        failed_files = [summary for summary in summaries if "reason" in summary]

        return summaries


    async def analyze_nib_files(self):
        """
        Analyze NIB files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        nib_files = self.nib_scanner.scan_files_in_project()
        return await self.get_nib_files_summaries(nib_files)

    async def get_nib_files_summaries(self, nib_files):
        """
        Get summaries for NIB files by scanning and reprocessing if necessary.

        Args:
            nib_files (list): List of NIB files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.nib_scanner.get_file_summaries(nib_files)

        return summaries


    async def analyze_storyboard_files(self):
        """
        Analyze storyboard files in the project by scanning and getting summaries.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        storyboard_files = self.storyboard_scanner.scan_files_in_project()
        return await self.get_storyboard_files_summaries(storyboard_files)

    async def get_storyboard_files_summaries(self, storyboard_files):
        """
        Get summaries for storyboard files by scanning and reprocessing if necessary.

        Args:
            storyboard_files (list): List of storyboard files to be analyzed.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        summaries = await self.storyboard_scanner.get_file_summaries(storyboard_files)

        return summaries
