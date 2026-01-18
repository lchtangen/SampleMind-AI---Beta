"""Batch export capabilities for analysis results"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ResultExporter:
    """Export analysis results to multiple formats: JSON, CSV, YAML, Markdown"""

    # Supported formats
    FORMATS = ["JSON", "CSV", "YAML", "Markdown"]

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize exporter

        Args:
            output_dir: Output directory for exported files (defaults to current dir)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================================
    # SINGLE FILE EXPORT
    # ============================================================================

    async def export_to_json(
        self, features: Dict[str, Any], file_name: str, output_path: Optional[str] = None
    ) -> str:
        """Export analysis to JSON format"""
        try:
            output_path = output_path or self.output_dir / f"{file_name}.analysis.json"
            output_path = Path(output_path)

            data = {
                "export_date": datetime.now().isoformat(),
                "file_name": file_name,
                "analysis": self._flatten_features(features),
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Exported to JSON: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ JSON export failed: {e}")
            raise

    async def export_to_csv(
        self, features: Dict[str, Any], file_name: str, output_path: Optional[str] = None
    ) -> str:
        """Export analysis to CSV format"""
        try:
            output_path = output_path or self.output_dir / f"{file_name}.analysis.csv"
            output_path = Path(output_path)

            flat_features = self._flatten_features(features)

            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Property", "Value"])
                # Write data
                for key, value in flat_features.items():
                    writer.writerow([key, value])

            logger.info(f"✅ Exported to CSV: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ CSV export failed: {e}")
            raise

    async def export_to_yaml(
        self, features: Dict[str, Any], file_name: str, output_path: Optional[str] = None
    ) -> str:
        """Export analysis to YAML format"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")

        try:
            output_path = output_path or self.output_dir / f"{file_name}.analysis.yaml"
            output_path = Path(output_path)

            data = {
                "export_date": datetime.now().isoformat(),
                "file_name": file_name,
                "analysis": self._flatten_features(features),
            }

            with open(output_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"✅ Exported to YAML: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ YAML export failed: {e}")
            raise

    async def export_to_markdown(
        self, features: Dict[str, Any], file_name: str, output_path: Optional[str] = None
    ) -> str:
        """Export analysis to Markdown format"""
        try:
            output_path = output_path or self.output_dir / f"{file_name}.analysis.md"
            output_path = Path(output_path)

            flat_features = self._flatten_features(features)

            md_content = self._generate_markdown(file_name, flat_features)

            with open(output_path, "w") as f:
                f.write(md_content)

            logger.info(f"✅ Exported to Markdown: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Markdown export failed: {e}")
            raise

    # ============================================================================
    # BATCH EXPORT
    # ============================================================================

    async def export_batch_to_json(
        self,
        analyses: List[Dict[str, Any]],
        batch_name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Export batch of analyses to JSON"""
        try:
            output_path = output_path or self.output_dir / f"{batch_name}_batch.json"
            output_path = Path(output_path)

            data = {
                "export_date": datetime.now().isoformat(),
                "batch_name": batch_name,
                "total_files": len(analyses),
                "analyses": [self._flatten_features(a) for a in analyses],
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Exported batch ({len(analyses)} files) to JSON: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Batch JSON export failed: {e}")
            raise

    async def export_batch_to_csv(
        self,
        analyses: List[Dict[str, Any]],
        batch_name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Export batch of analyses to CSV"""
        try:
            output_path = output_path or self.output_dir / f"{batch_name}_batch.csv"
            output_path = Path(output_path)

            # Collect all keys across all analyses
            all_keys = set()
            flat_analyses = []
            for analysis in analyses:
                flat = self._flatten_features(analysis)
                flat_analyses.append(flat)
                all_keys.update(flat.keys())

            all_keys = sorted(list(all_keys))

            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_keys)
                writer.writeheader()
                for flat_analysis in flat_analyses:
                    writer.writerow({k: flat_analysis.get(k, "") for k in all_keys})

            logger.info(
                f"✅ Exported batch ({len(analyses)} files) to CSV: {output_path}"
            )
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Batch CSV export failed: {e}")
            raise

    async def export_batch_to_yaml(
        self,
        analyses: List[Dict[str, Any]],
        batch_name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Export batch of analyses to YAML"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML export")

        try:
            output_path = output_path or self.output_dir / f"{batch_name}_batch.yaml"
            output_path = Path(output_path)

            data = {
                "export_date": datetime.now().isoformat(),
                "batch_name": batch_name,
                "total_files": len(analyses),
                "analyses": [self._flatten_features(a) for a in analyses],
            }

            with open(output_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(
                f"✅ Exported batch ({len(analyses)} files) to YAML: {output_path}"
            )
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Batch YAML export failed: {e}")
            raise

    async def export_batch_to_markdown(
        self,
        analyses: List[Dict[str, Any]],
        batch_name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Export batch of analyses to Markdown"""
        try:
            output_path = output_path or self.output_dir / f"{batch_name}_batch.md"
            output_path = Path(output_path)

            md_content = f"# Batch Analysis Report\n\n"
            md_content += f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            md_content += f"**Batch Name:** {batch_name}\n"
            md_content += f"**Total Files:** {len(analyses)}\n\n"
            md_content += f"---\n\n"

            for idx, analysis in enumerate(analyses, 1):
                flat_features = self._flatten_features(analysis)
                file_name = analysis.get("file_name", f"File {idx}")
                md_content += f"## Analysis {idx}: {file_name}\n\n"
                md_content += "| Property | Value |\n"
                md_content += "|----------|-------|\n"
                for key, value in flat_features.items():
                    md_content += f"| {key} | {value} |\n"
                md_content += "\n"

            with open(output_path, "w") as f:
                f.write(md_content)

            logger.info(
                f"✅ Exported batch ({len(analyses)} files) to Markdown: {output_path}"
            )
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Batch Markdown export failed: {e}")
            raise

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    @staticmethod
    def _flatten_features(features: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary for CSV/Markdown export"""
        flat = {}

        for key, value in features.items():
            full_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"

            if isinstance(value, dict):
                # Recursively flatten nested dicts
                flat.update(ResultExporter._flatten_features(value, full_key))
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                if value and isinstance(value[0], (int, float, str)):
                    flat[full_key] = ", ".join(str(v) for v in value)
                else:
                    flat[full_key] = str(value)
            elif isinstance(value, bool):
                flat[full_key] = "Yes" if value else "No"
            else:
                flat[full_key] = str(value) if value is not None else ""

        return flat

    @staticmethod
    def _generate_markdown(file_name: str, features: Dict[str, Any]) -> str:
        """Generate Markdown formatted report"""
        md = f"# Analysis Report\n\n"
        md += f"**File:** {file_name}\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += f"---\n\n"

        md += "## Analysis Results\n\n"
        md += "| Property | Value |\n"
        md += "|----------|-------|\n"

        for key, value in features.items():
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace("_", " ").title()
            md += f"| {formatted_key} | {value} |\n"

        md += "\n---\n\n"
        md += f"*Report generated by SampleMind AI*\n"

        return md

    async def export(
        self,
        features: Dict[str, Any],
        file_name: str,
        format_type: str = "JSON",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Export to specified format

        Args:
            features: Analysis features dictionary
            file_name: Name of audio file
            format_type: Export format (JSON, CSV, YAML, Markdown)
            output_path: Custom output path

        Returns:
            Path to exported file
        """
        format_type = format_type.upper()

        if format_type == "JSON":
            return await self.export_to_json(features, file_name, output_path)
        elif format_type == "CSV":
            return await self.export_to_csv(features, file_name, output_path)
        elif format_type == "YAML":
            return await self.export_to_yaml(features, file_name, output_path)
        elif format_type == "MARKDOWN":
            return await self.export_to_markdown(features, file_name, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.FORMATS}")

    async def export_batch(
        self,
        analyses: List[Dict[str, Any]],
        batch_name: str,
        format_type: str = "JSON",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Export batch to specified format

        Args:
            analyses: List of analysis feature dictionaries
            batch_name: Name for batch export
            format_type: Export format (JSON, CSV, YAML, Markdown)
            output_path: Custom output path

        Returns:
            Path to exported file
        """
        format_type = format_type.upper()

        if format_type == "JSON":
            return await self.export_batch_to_json(analyses, batch_name, output_path)
        elif format_type == "CSV":
            return await self.export_batch_to_csv(analyses, batch_name, output_path)
        elif format_type == "YAML":
            return await self.export_batch_to_yaml(analyses, batch_name, output_path)
        elif format_type == "MARKDOWN":
            return await self.export_batch_to_markdown(analyses, batch_name, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.FORMATS}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return self.FORMATS.copy()

    def is_yaml_available(self) -> bool:
        """Check if YAML support is available"""
        return YAML_AVAILABLE
