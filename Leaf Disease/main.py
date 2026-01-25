import os
import json
import logging
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DiseaseAnalysisResult:
    """
    Data class for storing comprehensive disease and plant analysis results.
    """
    # Plant Identity
    plant_name: str
    scientific_name: str
    description: str
    taxonomy: Dict[str, str]
    
    # Disease Analysis
    disease_detected: bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms: List[str]
    possible_causes: List[str]
    treatment: List[str]
    
    # Visuals
    similar_images: List[str]
    disease_scientific_name: Optional[str] = None
    
    analysis_timestamp: str = datetime.now().astimezone().isoformat()


class LeafDiseaseDetector:
    """
    Advanced Leaf Disease Detection System using Kindwise (Plant.id) API.
    """

    PLANT_ID_URL = "https://plant.id/api/v3/identification"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Leaf Disease Detector with Plant.id API credentials.
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("KINDWISE_API_KEY")
        if not self.api_key:
            raise ValueError("KINDWISE_API_KEY not found in environment variables")
        logger.info("Leaf Disease Detector (Kindwise) initialized")

    def analyze_leaf_image_base64(self, base64_image: str,
                                  temperature: float = None,
                                  max_tokens: int = None) -> Dict:
        """
        Analyze base64 encoded image data for leaf diseases using Kindwise API.
        """
        try:
            logger.info("Starting analysis with Kindwise API")

            # Clean base64 string
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]

            import requests
            
            headers = {
                "Content-Type": "application/json",
                "Api-Key": self.api_key,
            }
            
            payload = {
                "images": [f"data:image/jpeg;base64,{base64_image}"],
                "health": "all",
                "similar_images": True
            }

            # Requesting additional details
            query_params = {
                "details": "common_names,cause,treatment,description,url,classification,wiki_description,taxonomy,wiki_image",
                "language": "en"
            }

            response = requests.post(self.PLANT_ID_URL, json=payload, headers=headers, params=query_params)
            
            if response.status_code != 201 and response.status_code != 200:
                logger.error(f"Kindwise API error: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")

            result_data = response.json()
            logger.info("Kindwise API request completed successfully")

            # Map Kindwise response to DiseaseAnalysisResult
            result = self._convert_plant_id_response(result_data)
            
            return result.__dict__

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

    def _convert_plant_id_response(self, data: Dict) -> DiseaseAnalysisResult:
        """
        Convert Kindwise API response to internal DiseaseAnalysisResult format.
        """
        try:
            result_section = data.get("result", {})
            
            # DEBUG: Print keys to understand structure
            print(f"DEBUG: Result keys: {list(result_section.keys())}")
            if "health_assessment" in result_section:
                print(f"DEBUG: Health keys: {list(result_section['health_assessment'].keys())}")
            
            # --- Check if it's a plant ---
            is_plant = result_section.get("is_plant", {}).get("binary", True)
            if not is_plant:
                return DiseaseAnalysisResult(
                    plant_name="Not a Plant",
                    scientific_name="Non-plant object detected",
                    description="The image does not appear to contain a plant. Please upload a clear photo of a plant leaf.",
                    taxonomy={},
                    disease_detected=False,
                    disease_name=None,
                    disease_type="invalid_image",
                    severity="none",
                    confidence=0,
                    symptoms=["Image is not a plant"],
                    possible_causes=["Upload contained non-plant objects"],
                    treatment=["Upload a valid plant image"],
                    similar_images=[]
                )

            # --- 1. Parse Classification (Identity) ---
            classification = result_section.get("classification", {})
            suggestions = classification.get("suggestions", [])
            
            plant_name = "Unknown Plant"
            scientific_name = "Identification failed"
            description = "Could not confidently identify the plant species."
            taxonomy = {}
            similar_images = []

            if suggestions:
                top_plant = suggestions[0]
                plant_name = top_plant.get("name", plant_name)
                
                # Get common name if available (often better than latin name for display)
                details = top_plant.get("details", {})
                common_names = details.get("common_names", [])
                if common_names:
                    plant_name = common_names[0].title()
                
                scientific_name = top_plant.get("name", "Unknown")
                
                # Description
                description = details.get("description", {}).get("value") or \
                              details.get("wiki_description", {}).get("value") or \
                              description
                
                # Taxonomy
                taxonomy_data = details.get("taxonomy", {})
                taxonomy = {
                    "class": taxonomy_data.get("class", ""),
                    "family": taxonomy_data.get("family", ""),
                    "genus": taxonomy_data.get("genus", "")
                }
                
                # Similar Images (from the plant suggestion)
                for img in top_plant.get("similar_images", [])[:3]:
                    if "url" in img:
                        similar_images.append(img["url"])

            # --- 2. Parse Health Assessment (Disease) ---
            # Note: 'disease' and 'is_healthy' are direct children of 'result' in the ID endpoint
            is_healthy_data = result_section.get("is_healthy", {})
            diseases = result_section.get("disease", {}).get("suggestions", [])

            is_healthy = is_healthy_data.get("binary", True)
            
            if not diseases or is_healthy:
                # Healthy leaf case
                return DiseaseAnalysisResult(
                    plant_name=plant_name,
                    scientific_name=scientific_name,
                    description=description,
                    taxonomy=taxonomy,
                    disease_detected=False,
                    disease_name=None,
                    disease_type="healthy",
                    severity="none",
                    confidence=round(is_healthy_data.get("probability", 0) * 100, 2),
                    symptoms=["No pathogenic symptoms detected"],
                    possible_causes=["Optimal growing conditions"],
                    treatment=["Continue standard care"],
                    similar_images=similar_images
                )

            # Sick leaf case - take the top disease suggestion
            top_disease = diseases[0]
            scientific_name_disease = top_disease.get("name", "Unknown Disease")
            prob = round(top_disease.get("probability", 0) * 100, 2)
            
            disease_details = top_disease.get("details", {})
            
            # Try to get a common name
            common_names = disease_details.get("common_names", [])
            if common_names:
                disease_name = common_names[0].title()
            else:
                disease_name = scientific_name_disease

            # Map symptoms
            symptoms = [disease_details.get("description", "Characteristic symptoms observed")]
            
            # Map causes
            possible_causes = [disease_details.get("cause", "Environmental or biological factors")]
            
            # Map treatments
            treatment_info = disease_details.get("treatment", {})
            treatment = []
            if isinstance(treatment_info, dict):
                for key, val in treatment_info.items():
                    if isinstance(val, list):
                        treatment.extend(val)
                    elif isinstance(val, str):
                        treatment.append(val)
            
            if not treatment:
                treatment = ["Consult an expert for specific treatment"]

            return DiseaseAnalysisResult(
                plant_name=plant_name,
                scientific_name=scientific_name,
                description=description,
                taxonomy=taxonomy,
                disease_detected=True,
                disease_name=disease_name,
                disease_scientific_name=scientific_name_disease,
                disease_type="unknown", 
                severity="moderate", 
                confidence=prob,
                symptoms=symptoms,
                possible_causes=possible_causes,
                treatment=treatment,
                similar_images=similar_images
            )

        except Exception as e:
            logger.error(f"Error mapping response: {str(e)}")
            # Fallback for errors
            return DiseaseAnalysisResult(
                plant_name="Error",
                scientific_name="Error",
                description="Error processing data",
                taxonomy={},
                disease_detected=False,
                disease_name="Error parsing result",
                disease_type="error",
                severity="none",
                confidence=0,
                symptoms=["Error processing API response"],
                possible_causes=["Unknown"],
                treatment=["Try again later"],
                similar_images=[]
            )


def main():
    """Main execution function for testing"""
    try:
        # Example usage
        detector = LeafDiseaseDetector()
        print("Leaf Disease Detector (minimal version) initialized successfully!")
        print("Use analyze_leaf_image_base64() method with base64 image data.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
