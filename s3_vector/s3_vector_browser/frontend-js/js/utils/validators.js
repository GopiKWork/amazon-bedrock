/**
 * S3 Vector Browser Input Validators
 * Functions for validating user input and data
 */

/**
 * Validate AWS ARN format
 */
function validateARN(arn) {
    if (!arn || typeof arn !== 'string') {
        return { valid: false, error: 'ARN must be a non-empty string' };
    }
    
    // Basic ARN format: arn:partition:service:region:account-id:resource-type/resource-id
    const arnPattern = /^arn:[^:]+:[^:]+:[^:]*:[^:]*:.+$/;
    
    if (!arnPattern.test(arn)) {
        return { valid: false, error: 'Invalid ARN format' };
    }
    
    const parts = arn.split(':');
    
    if (parts.length < 6) {
        return { valid: false, error: 'ARN must have at least 6 parts' };
    }
    
    // Validate partition
    if (!parts[1]) {
        return { valid: false, error: 'ARN partition cannot be empty' };
    }
    
    // Validate service
    if (!parts[2]) {
        return { valid: false, error: 'ARN service cannot be empty' };
    }
    
    // Validate resource
    if (!parts[5]) {
        return { valid: false, error: 'ARN resource cannot be empty' };
    }
    
    return { valid: true };
}

/**
 * Validate AWS region format
 */
function validateRegion(region) {
    if (!region || typeof region !== 'string') {
        return { valid: false, error: 'Region must be a non-empty string' };
    }
    
    // AWS region format: us-east-1, eu-west-1, etc.
    const regionPattern = /^[a-z]{2,3}-[a-z]+-\d+$/;
    
    if (!regionPattern.test(region)) {
        return { valid: false, error: 'Invalid AWS region format' };
    }
    
    return { valid: true };
}

/**
 * Validate AWS account ID format
 */
function validateAccountId(accountId) {
    if (!accountId) {
        return { valid: false, error: 'Account ID is required' };
    }
    
    const accountStr = accountId.toString();
    
    // AWS account ID is a 12-digit number
    const accountPattern = /^\d{12}$/;
    
    if (!accountPattern.test(accountStr)) {
        return { valid: false, error: 'Account ID must be a 12-digit number' };
    }
    
    return { valid: true };
}

/**
 * Validate bucket name format
 */
function validateBucketName(bucketName) {
    if (!bucketName || typeof bucketName !== 'string') {
        return { valid: false, error: 'Bucket name must be a non-empty string' };
    }
    
    // S3 bucket naming rules (simplified)
    if (bucketName.length < 3 || bucketName.length > 63) {
        return { valid: false, error: 'Bucket name must be between 3 and 63 characters' };
    }
    
    // Must start and end with lowercase letter or number
    if (!/^[a-z0-9]/.test(bucketName) || !/[a-z0-9]$/.test(bucketName)) {
        return { valid: false, error: 'Bucket name must start and end with lowercase letter or number' };
    }
    
    // Can contain lowercase letters, numbers, hyphens, and periods
    if (!/^[a-z0-9.-]+$/.test(bucketName)) {
        return { valid: false, error: 'Bucket name can only contain lowercase letters, numbers, hyphens, and periods' };
    }
    
    // Cannot contain consecutive periods
    if (/\.\./.test(bucketName)) {
        return { valid: false, error: 'Bucket name cannot contain consecutive periods' };
    }
    
    // Cannot be formatted as IP address
    if (/^\d+\.\d+\.\d+\.\d+$/.test(bucketName)) {
        return { valid: false, error: 'Bucket name cannot be formatted as IP address' };
    }
    
    return { valid: true };
}

/**
 * Validate index name format
 */
function validateIndexName(indexName) {
    if (!indexName || typeof indexName !== 'string') {
        return { valid: false, error: 'Index name must be a non-empty string' };
    }
    
    // Index names should be reasonable length
    if (indexName.length < 1 || indexName.length > 255) {
        return { valid: false, error: 'Index name must be between 1 and 255 characters' };
    }
    
    // Should not contain control characters
    if (/[\x00-\x1f\x7f]/.test(indexName)) {
        return { valid: false, error: 'Index name cannot contain control characters' };
    }
    
    return { valid: true };
}

/**
 * Validate item ID format
 */
function validateItemId(itemId) {
    if (!itemId || typeof itemId !== 'string') {
        return { valid: false, error: 'Item ID must be a non-empty string' };
    }
    
    // Item IDs should be reasonable length
    if (itemId.length < 1 || itemId.length > 1024) {
        return { valid: false, error: 'Item ID must be between 1 and 1024 characters' };
    }
    
    // Should not contain control characters
    if (/[\x00-\x1f\x7f]/.test(itemId)) {
        return { valid: false, error: 'Item ID cannot contain control characters' };
    }
    
    return { valid: true };
}

/**
 * Validate vector dimension
 */
function validateDimension(dimension) {
    if (dimension === null || dimension === undefined) {
        return { valid: false, error: 'Dimension is required' };
    }
    
    const dim = parseInt(dimension);
    
    if (isNaN(dim)) {
        return { valid: false, error: 'Dimension must be a number' };
    }
    
    if (dim < 1) {
        return { valid: false, error: 'Dimension must be positive' };
    }
    
    if (dim > 10000) {
        return { valid: false, error: 'Dimension cannot exceed 10,000' };
    }
    
    return { valid: true };
}

/**
 * Validate distance metric
 */
function validateDistanceMetric(metric) {
    if (!metric || typeof metric !== 'string') {
        return { valid: false, error: 'Distance metric must be a non-empty string' };
    }
    
    const validMetrics = [
        'cosine',
        'euclidean',
        'dot_product',
        'manhattan',
        'l1',
        'l2'
    ];
    
    if (!validMetrics.includes(metric.toLowerCase())) {
        return { 
            valid: false, 
            error: `Distance metric must be one of: ${validMetrics.join(', ')}` 
        };
    }
    
    return { valid: true };
}

/**
 * Validate data type
 */
function validateDataType(dataType) {
    if (!dataType || typeof dataType !== 'string') {
        return { valid: false, error: 'Data type must be a non-empty string' };
    }
    
    const validTypes = [
        'float32',
        'float64',
        'int8',
        'int16',
        'int32',
        'uint8',
        'uint16',
        'uint32'
    ];
    
    if (!validTypes.includes(dataType.toLowerCase())) {
        return { 
            valid: false, 
            error: `Data type must be one of: ${validTypes.join(', ')}` 
        };
    }
    
    return { valid: true };
}

/**
 * Validate query vector
 */
function validateQueryVector(vector, expectedDimension = null) {
    if (!Array.isArray(vector)) {
        return { valid: false, error: 'Query vector must be an array' };
    }
    
    if (vector.length === 0) {
        return { valid: false, error: 'Query vector cannot be empty' };
    }
    
    if (expectedDimension && vector.length !== expectedDimension) {
        return { 
            valid: false, 
            error: `Query vector must have ${expectedDimension} dimensions, got ${vector.length}` 
        };
    }
    
    // Check that all elements are numbers
    for (let i = 0; i < vector.length; i++) {
        if (typeof vector[i] !== 'number' || isNaN(vector[i])) {
            return { 
                valid: false, 
                error: `Query vector element at index ${i} must be a number` 
            };
        }
        
        if (!isFinite(vector[i])) {
            return { 
                valid: false, 
                error: `Query vector element at index ${i} must be finite` 
            };
        }
    }
    
    return { valid: true };
}

/**
 * Validate metadata object
 */
function validateMetadata(metadata) {
    if (metadata === null || metadata === undefined) {
        return { valid: true }; // Metadata is optional
    }
    
    if (typeof metadata !== 'object' || Array.isArray(metadata)) {
        return { valid: false, error: 'Metadata must be an object' };
    }
    
    // Check for reasonable size
    const jsonString = JSON.stringify(metadata);
    if (jsonString.length > 100000) { // 100KB limit
        return { valid: false, error: 'Metadata is too large (max 100KB)' };
    }
    
    // Check for valid keys
    for (const key of Object.keys(metadata)) {
        if (typeof key !== 'string') {
            return { valid: false, error: 'Metadata keys must be strings' };
        }
        
        if (key.length === 0) {
            return { valid: false, error: 'Metadata keys cannot be empty' };
        }
        
        if (key.length > 1000) {
            return { valid: false, error: 'Metadata keys cannot exceed 1000 characters' };
        }
        
        // Check for control characters in keys
        if (/[\x00-\x1f\x7f]/.test(key)) {
            return { valid: false, error: 'Metadata keys cannot contain control characters' };
        }
    }
    
    return { valid: true };
}

/**
 * Validate pagination parameters
 */
function validatePagination(limit, offset) {
    const result = { valid: true, errors: [] };
    
    if (limit !== null && limit !== undefined) {
        const limitNum = parseInt(limit);
        if (isNaN(limitNum)) {
            result.valid = false;
            result.errors.push('Limit must be a number');
        } else if (limitNum < 1) {
            result.valid = false;
            result.errors.push('Limit must be positive');
        } else if (limitNum > 1000) {
            result.valid = false;
            result.errors.push('Limit cannot exceed 1000');
        }
    }
    
    if (offset !== null && offset !== undefined) {
        const offsetNum = parseInt(offset);
        if (isNaN(offsetNum)) {
            result.valid = false;
            result.errors.push('Offset must be a number');
        } else if (offsetNum < 0) {
            result.valid = false;
            result.errors.push('Offset cannot be negative');
        }
    }
    
    return result;
}

/**
 * Validate URL format
 */
function validateURL(url) {
    if (!url || typeof url !== 'string') {
        return { valid: false, error: 'URL must be a non-empty string' };
    }
    
    try {
        new URL(url);
        return { valid: true };
    } catch {
        return { valid: false, error: 'Invalid URL format' };
    }
}

/**
 * Validate email format
 */
function validateEmail(email) {
    if (!email || typeof email !== 'string') {
        return { valid: false, error: 'Email must be a non-empty string' };
    }
    
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailPattern.test(email)) {
        return { valid: false, error: 'Invalid email format' };
    }
    
    return { valid: true };
}

/**
 * Sanitize input string
 */
function sanitizeInput(input, options = {}) {
    if (typeof input !== 'string') {
        return '';
    }
    
    const {
        maxLength = 1000,
        allowHTML = false,
        trimWhitespace = true
    } = options;
    
    let sanitized = input;
    
    // Trim whitespace
    if (trimWhitespace) {
        sanitized = sanitized.trim();
    }
    
    // Remove HTML if not allowed
    if (!allowHTML) {
        sanitized = sanitized.replace(/<[^>]*>/g, '');
    }
    
    // Remove control characters
    sanitized = sanitized.replace(/[\x00-\x1f\x7f]/g, '');
    
    // Truncate to max length
    if (sanitized.length > maxLength) {
        sanitized = sanitized.substring(0, maxLength);
    }
    
    return sanitized;
}

/**
 * Validate and sanitize form data
 */
function validateFormData(data, schema) {
    const result = {
        valid: true,
        errors: {},
        sanitized: {}
    };
    
    for (const [field, rules] of Object.entries(schema)) {
        const value = data[field];
        const fieldErrors = [];
        
        // Check required
        if (rules.required && (value === null || value === undefined || value === '')) {
            fieldErrors.push(`${field} is required`);
        }
        
        // Skip other validations if field is empty and not required
        if (!rules.required && (value === null || value === undefined || value === '')) {
            result.sanitized[field] = value;
            continue;
        }
        
        // Type validation
        if (rules.type && typeof value !== rules.type) {
            fieldErrors.push(`${field} must be of type ${rules.type}`);
        }
        
        // Length validation for strings
        if (typeof value === 'string') {
            if (rules.minLength && value.length < rules.minLength) {
                fieldErrors.push(`${field} must be at least ${rules.minLength} characters`);
            }
            if (rules.maxLength && value.length > rules.maxLength) {
                fieldErrors.push(`${field} cannot exceed ${rules.maxLength} characters`);
            }
        }
        
        // Range validation for numbers
        if (typeof value === 'number') {
            if (rules.min !== undefined && value < rules.min) {
                fieldErrors.push(`${field} must be at least ${rules.min}`);
            }
            if (rules.max !== undefined && value > rules.max) {
                fieldErrors.push(`${field} cannot exceed ${rules.max}`);
            }
        }
        
        // Pattern validation
        if (rules.pattern && typeof value === 'string') {
            if (!rules.pattern.test(value)) {
                fieldErrors.push(`${field} format is invalid`);
            }
        }
        
        // Custom validation
        if (rules.validator && typeof rules.validator === 'function') {
            const customResult = rules.validator(value);
            if (!customResult.valid) {
                fieldErrors.push(customResult.error);
            }
        }
        
        // Sanitize value
        let sanitizedValue = value;
        if (typeof value === 'string' && rules.sanitize) {
            sanitizedValue = sanitizeInput(value, rules.sanitize);
        }
        
        result.sanitized[field] = sanitizedValue;
        
        if (fieldErrors.length > 0) {
            result.valid = false;
            result.errors[field] = fieldErrors;
        }
    }
    
    return result;
}

// Export functions to global scope
window.validateARN = validateARN;
window.validateRegion = validateRegion;
window.validateAccountId = validateAccountId;
window.validateBucketName = validateBucketName;
window.validateIndexName = validateIndexName;
window.validateItemId = validateItemId;
window.validateDimension = validateDimension;
window.validateDistanceMetric = validateDistanceMetric;
window.validateDataType = validateDataType;
window.validateQueryVector = validateQueryVector;
window.validateMetadata = validateMetadata;
window.validatePagination = validatePagination;
window.validateURL = validateURL;
window.validateEmail = validateEmail;
window.sanitizeInput = sanitizeInput;
window.validateFormData = validateFormData;