"""
Model Manager for handling ML model versioning and retraining
"""
import os
import json
import pickle
from datetime import datetime
import boto3
from typing import Optional, Dict, Any

class ModelManager:
    def __init__(self, model_dir: str = "models", s3_bucket: Optional[str] = None):
        self.model_dir = model_dir
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3') if s3_bucket else None
        os.makedirs(model_dir, exist_ok=True)
        
        # Metadata file to track model versions
        self.metadata_file = os.path.join(model_dir, "model_metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load or create model metadata"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            "models": {
                "outlier_detector": {"current_version": None, "versions": []},
                "risk_predictor": {"current_version": None, "versions": []},
                "vendor_cluster": {"current_version": None, "versions": []}
            }
        }
    
    def _save_metadata(self):
        """Save model metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_model(self, model: Any, model_type: str, metrics: Dict[str, float]) -> str:
        """
        Save a trained model with version control
        
        Args:
            model: The trained model object
            model_type: Type of model ('outlier_detector', 'risk_predictor', 'vendor_cluster')
            metrics: Dictionary of evaluation metrics
            
        Returns:
            version_id: The version ID of the saved model
        """
        # Generate version ID using timestamp
        version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{model_type}_{version_id}.pkl"
        filepath = os.path.join(self.model_dir, filename)
        
        # Save model locally
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        # Upload to S3 if configured
        if self.s3_bucket:
            self.s3_client.upload_file(
                filepath,
                self.s3_bucket,
                f"models/{filename}"
            )
        
        # Update metadata
        model_info = {
            "version_id": version_id,
            "filename": filename,
            "metrics": metrics,
            "created_at": datetime.now().isoformat(),
            "is_current": True
        }
        
        # Set previous current version to false
        for version in self.metadata["models"][model_type]["versions"]:
            version["is_current"] = False
        
        self.metadata["models"][model_type]["versions"].append(model_info)
        self.metadata["models"][model_type]["current_version"] = version_id
        self._save_metadata()
        
        return version_id
    
    def load_model(self, model_type: str, version_id: Optional[str] = None) -> Any:
        """
        Load a model from storage
        
        Args:
            model_type: Type of model to load
            version_id: Specific version to load, or None for current version
            
        Returns:
            The loaded model object
        """
        if version_id is None:
            version_id = self.metadata["models"][model_type]["current_version"]
            
        if version_id is None:
            raise ValueError(f"No model version found for {model_type}")
            
        filename = f"{model_type}_{version_id}.pkl"
        filepath = os.path.join(self.model_dir, filename)
        
        # Try to load from local storage first
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        
        # If not found locally and S3 is configured, try to download
        if self.s3_bucket:
            self.s3_client.download_file(
                self.s3_bucket,
                f"models/{filename}",
                filepath
            )
            with open(filepath, 'rb') as f:
                return pickle.load(f)
                
        raise FileNotFoundError(f"Model file not found: {filename}")
    
    def get_model_metrics(self, model_type: str, version_id: Optional[str] = None) -> Dict[str, float]:
        """Get evaluation metrics for a model version"""
        if version_id is None:
            version_id = self.metadata["models"][model_type]["current_version"]
            
        for version in self.metadata["models"][model_type]["versions"]:
            if version["version_id"] == version_id:
                return version["metrics"]
                
        raise ValueError(f"No metrics found for model {model_type} version {version_id}")
    
    def list_versions(self, model_type: str) -> list:
        """List all versions of a model type"""
        return self.metadata["models"][model_type]["versions"]
    
    def get_current_version(self, model_type: str) -> Optional[str]:
        """Get the current version ID for a model type"""
        return self.metadata["models"][model_type]["current_version"]
    
    def set_current_version(self, model_type: str, version_id: str):
        """Set the current version for a model type"""
        found = False
        for version in self.metadata["models"][model_type]["versions"]:
            if version["version_id"] == version_id:
                version["is_current"] = True
                found = True
            else:
                version["is_current"] = False
                
        if not found:
            raise ValueError(f"Version {version_id} not found for model {model_type}")
            
        self.metadata["models"][model_type]["current_version"] = version_id
        self._save_metadata()
