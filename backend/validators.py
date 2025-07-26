"""
Input validation for LEXICON API endpoints
"""
from typing import Dict, List, Optional, Tuple
import re

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class BriefGenerationValidator:
    """Validator for brief generation requests"""
    
    VALID_STRATEGIES = ['challenge', 'support']
    VALID_MOTION_TYPES = [
        'Daubert Motion',
        'Response to Daubert Challenge',
        'Frye Motion', 
        'Response to Frye Challenge',
        'Motion in Limine',
        'Expert Qualification Challenge',
        'Methodology Challenge'
    ]
    # For MVP, limiting to jurisdictions where client operates
    VALID_JURISDICTIONS = [
        'federal',
        'illinois',
        'indiana'
    ]
    
    # Expert name patterns
    EXPERT_NAME_PATTERN = re.compile(r'^[A-Za-z\s\.\-\']{2,100}$')
    
    @staticmethod
    def validate_expert_name(name: Optional[str]) -> str:
        """Validate expert name"""
        if not name:
            raise ValidationError('expert_name', 'Expert name is required')
            
        name = name.strip()
        
        if len(name) < 2:
            raise ValidationError('expert_name', 'Expert name must be at least 2 characters')
            
        if len(name) > 100:
            raise ValidationError('expert_name', 'Expert name must not exceed 100 characters')
            
        if not BriefGenerationValidator.EXPERT_NAME_PATTERN.match(name):
            raise ValidationError('expert_name', 
                'Expert name can only contain letters, spaces, periods, hyphens, and apostrophes')
        
        # Check for suspicious patterns
        suspicious_patterns = ['script', 'alert', '<', '>', 'function', 'eval']
        name_lower = name.lower()
        for pattern in suspicious_patterns:
            if pattern in name_lower:
                raise ValidationError('expert_name', 'Invalid characters in expert name')
        
        return name
    
    @staticmethod
    def validate_strategy(strategy: Optional[str]) -> str:
        """Validate litigation strategy"""
        if not strategy:
            return 'challenge'  # Default value
            
        strategy = strategy.strip().lower()
        
        if strategy not in BriefGenerationValidator.VALID_STRATEGIES:
            raise ValidationError('strategy', 
                f'Strategy must be one of: {", ".join(BriefGenerationValidator.VALID_STRATEGIES)}')
        
        return strategy
    
    @staticmethod
    def validate_motion_type(motion_type: Optional[str]) -> str:
        """Validate motion type"""
        if not motion_type:
            raise ValidationError('motion_type', 'Motion type is required')
            
        motion_type = motion_type.strip()
        
        # Allow both exact matches and lowercase versions
        motion_type_lower = motion_type.lower()
        valid_types_lower = [mt.lower() for mt in BriefGenerationValidator.VALID_MOTION_TYPES]
        
        if motion_type not in BriefGenerationValidator.VALID_MOTION_TYPES and \
           motion_type_lower not in valid_types_lower:
            raise ValidationError('motion_type',
                f'Invalid motion type. Valid types are: {", ".join(BriefGenerationValidator.VALID_MOTION_TYPES)}')
        
        # Return the properly formatted motion type
        for valid_type in BriefGenerationValidator.VALID_MOTION_TYPES:
            if valid_type.lower() == motion_type_lower:
                return valid_type
        
        return motion_type
    
    @staticmethod
    def validate_jurisdiction(jurisdiction: Optional[str]) -> str:
        """Validate jurisdiction"""
        if not jurisdiction:
            return 'federal'  # Default value
            
        jurisdiction = jurisdiction.strip().lower()
        
        if jurisdiction not in BriefGenerationValidator.VALID_JURISDICTIONS:
            raise ValidationError('jurisdiction',
                f'Invalid jurisdiction. Valid options are: {", ".join(BriefGenerationValidator.VALID_JURISDICTIONS)}')
        
        return jurisdiction
    
    @staticmethod
    def validate_request(data: Dict) -> Dict:
        """Validate the complete request"""
        validated = {}
        
        # Validate each field
        validated['expert_name'] = BriefGenerationValidator.validate_expert_name(
            data.get('expert_name'))
        validated['strategy'] = BriefGenerationValidator.validate_strategy(
            data.get('strategy'))
        validated['motion_type'] = BriefGenerationValidator.validate_motion_type(
            data.get('motion_type'))
        validated['jurisdiction'] = BriefGenerationValidator.validate_jurisdiction(
            data.get('jurisdiction'))
        
        return validated


class DocumentValidator:
    """Validator for document uploads"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.wpd'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILES = 50
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Check if file extension is allowed"""
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext in DocumentValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Check if file size is within limits"""
        return 0 < file_size <= DocumentValidator.MAX_FILE_SIZE
    
    @staticmethod
    def validate_file_count(file_count: int) -> bool:
        """Check if number of files is within limits"""
        return 0 < file_count <= DocumentValidator.MAX_FILES


def create_validation_error_response(error: ValidationError) -> Tuple[Dict, int]:
    """Create a standardized error response for validation errors"""
    return {
        'success': False,
        'error': error.message,
        'field': error.field,
        'error_code': 'INVALID_INPUT'
    }, 400