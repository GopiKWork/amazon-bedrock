/**
 * S3 Vector Browser Data Formatters
 * Functions for formatting and displaying data
 */

/**
 * Format timestamp to human readable format
 */
function formatTimestamp(timestamp, options = {}) {
    if (!timestamp) return 'N/A';
    
    const {
        format = 'datetime',
        locale = 'en-US',
        timezone = 'local'
    } = options;
    
    let date;
    
    // Handle different timestamp formats
    if (typeof timestamp === 'string') {
        // Remove 'Z' suffix and parse as local time if needed
        if (timestamp.endsWith('Z') && timezone === 'local') {
            date = new Date(timestamp.slice(0, -1));
        } else {
            date = new Date(timestamp);
        }
    } else if (typeof timestamp === 'number') {
        date = new Date(timestamp);
    } else if (timestamp instanceof Date) {
        date = timestamp;
    } else {
        return 'Invalid Date';
    }
    
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    
    const formatOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (format === 'datetime' || format === 'full') {
        formatOptions.hour = '2-digit';
        formatOptions.minute = '2-digit';
        formatOptions.second = '2-digit';
    }
    
    if (format === 'full') {
        formatOptions.timeZoneName = 'short';
    }
    
    try {
        return date.toLocaleDateString(locale, formatOptions);
    } catch (error) {
        return date.toString();
    }
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSeconds < 60) {
        return 'Just now';
    } else if (diffMinutes < 60) {
        return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 30) {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
        return formatTimestamp(timestamp, { format: 'date' });
    }
}

/**
 * Format AWS ARN with highlighting
 */
function formatARN(arn, options = {}) {
    if (!arn || typeof arn !== 'string') {
        return { formatted: 'N/A', parts: null };
    }
    
    const {
        highlight = true,
        breakLong = true,
        maxLength = 60
    } = options;
    
    // Parse ARN: arn:partition:service:region:account-id:resource-type/resource-id
    const parts = arn.split(':');
    
    if (parts.length < 6 || parts[0] !== 'arn') {
        return { formatted: arn, parts: null };
    }
    
    const arnParts = {
        partition: parts[1],
        service: parts[2],
        region: parts[3],
        accountId: parts[4],
        resource: parts.slice(5).join(':')
    };
    
    let formatted = arn;
    
    if (breakLong && arn.length > maxLength) {
        // Break ARN at logical points
        const resourceParts = arnParts.resource.split('/');
        if (resourceParts.length > 1) {
            formatted = `arn:${arnParts.partition}:${arnParts.service}:${arnParts.region}:${arnParts.accountId}:\n${arnParts.resource}`;
        }
    }
    
    return {
        formatted,
        parts: arnParts,
        html: highlight ? formatARNWithHTML(arn, arnParts) : formatted
    };
}

/**
 * Format ARN with HTML highlighting
 */
function formatARNWithHTML(arn, parts) {
    if (!parts) return escapeHtml(arn);
    
    return `<span class="arn-prefix">arn:${parts.partition}:${parts.service}:</span>` +
           `<span class="arn-region">${parts.region}</span>:` +
           `<span class="arn-account">${parts.accountId}</span>:` +
           `<span class="arn-resource">${parts.resource}</span>`;
}

/**
 * Extract account ID from ARN
 */
function extractAccountFromARN(arn) {
    if (!arn || typeof arn !== 'string') return null;
    
    const parts = arn.split(':');
    if (parts.length >= 5 && parts[0] === 'arn') {
        return parts[4] || null;
    }
    
    return null;
}

/**
 * Extract region from ARN
 */
function extractRegionFromARN(arn) {
    if (!arn || typeof arn !== 'string') return null;
    
    const parts = arn.split(':');
    if (parts.length >= 4 && parts[0] === 'arn') {
        return parts[3] || null;
    }
    
    return null;
}

/**
 * Format large numbers with commas
 */
function formatNumber(num, options = {}) {
    if (num === null || num === undefined) return 'N/A';
    
    const {
        locale = 'en-US',
        minimumFractionDigits = 0,
        maximumFractionDigits = 2
    } = options;
    
    if (typeof num !== 'number') {
        const parsed = parseFloat(num);
        if (isNaN(parsed)) return 'N/A';
        num = parsed;
    }
    
    return num.toLocaleString(locale, {
        minimumFractionDigits,
        maximumFractionDigits
    });
}

/**
 * Format bytes to human readable size
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    if (bytes === null || bytes === undefined) return 'N/A';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format percentage
 */
function formatPercentage(value, total, decimals = 1) {
    if (value === null || value === undefined || total === null || total === undefined || total === 0) {
        return 'N/A';
    }
    
    const percentage = (value / total) * 100;
    return `${percentage.toFixed(decimals)}%`;
}

/**
 * Check if a string is an S3 URI
 */
function isS3URI(str) {
    if (typeof str !== 'string') return false;
    // More robust S3 URI pattern that allows for various bucket naming conventions
    return /^s3:\/\/[a-z0-9][a-z0-9.-]*[a-z0-9]\/.*/.test(str) || /^s3:\/\/[a-z0-9]\/.*/.test(str);
}

/**
 * Highlight search terms in text
 */
function highlightSearchTerm(text, searchTerm) {
    if (!searchTerm || !text) return escapeHtml(text);
    
    const escapedText = escapeHtml(text);
    const escapedSearchTerm = escapeHtml(searchTerm);
    
    // Create a case-insensitive regex
    const regex = new RegExp(`(${escapedSearchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    
    return escapedText.replace(regex, '<span class="search-highlight">$1</span>');
}

/**
 * Format metadata object for display
 */
function formatMetadata(metadata, options = {}) {
    if (!metadata || typeof metadata !== 'object') {
        return { formatted: 'No metadata', entries: [] };
    }
    
    const {
        maxKeyLength = 30,
        maxValueLength = 100,
        sortKeys = true,
        searchQuery = null,
        highlightMatches = false
    } = options;
    
    let entries = Object.entries(metadata);
    
    if (sortKeys) {
        entries.sort(([a], [b]) => a.localeCompare(b));
    }
    
    const formattedEntries = entries.map(([key, value]) => {
        let formattedKey = key;
        let formattedValue = value;
        let isS3Link = false;
        
        // Truncate long keys
        if (key.length > maxKeyLength) {
            formattedKey = key.substring(0, maxKeyLength - 3) + '...';
        }
        
        // Format value based on type
        if (value === null || value === undefined) {
            formattedValue = 'null';
        } else if (typeof value === 'boolean') {
            formattedValue = value.toString();
        } else if (typeof value === 'number') {
            formattedValue = formatNumber(value);
        } else if (typeof value === 'object') {
            formattedValue = JSON.stringify(value, null, 2);
        } else {
            formattedValue = value.toString();
            // Check if it's an S3 URI
            if (isS3URI(formattedValue)) {
                isS3Link = true;
            }
        }
        
        // Truncate long values (but not S3 URIs as they need to be clickable)
        if (!isS3Link && formattedValue.length > maxValueLength) {
            formattedValue = formattedValue.substring(0, maxValueLength - 3) + '...';
        }
        
        // Apply search highlighting if requested
        let highlightedKey = formattedKey;
        let highlightedValue = formattedValue;
        
        if (highlightMatches && searchQuery) {
            highlightedKey = highlightSearchTerm(formattedKey, searchQuery);
            if (!isS3Link) {
                highlightedValue = highlightSearchTerm(formattedValue, searchQuery);
            }
        }
        
        return {
            key,
            value,
            formattedKey,
            formattedValue,
            highlightedKey,
            highlightedValue,
            type: typeof value,
            isS3Link
        };
    });
    
    return {
        formatted: JSON.stringify(metadata, null, 2),
        entries: formattedEntries,
        count: entries.length
    };
}

/**
 * Format vector dimension information
 */
function formatDimension(dimension) {
    if (dimension === null || dimension === undefined) return 'N/A';
    
    const num = parseInt(dimension);
    if (isNaN(num)) return 'Invalid';
    
    return `${formatNumber(num)} dimensions`;
}

/**
 * Format distance metric
 */
function formatDistanceMetric(metric) {
    if (!metric) return 'N/A';
    
    const metricMap = {
        'cosine': 'Cosine Similarity',
        'euclidean': 'Euclidean Distance',
        'dot_product': 'Dot Product',
        'manhattan': 'Manhattan Distance',
        'l2': 'L2 (Euclidean)',
        'l1': 'L1 (Manhattan)'
    };
    
    return metricMap[metric.toLowerCase()] || capitalize(metric);
}

/**
 * Format data type
 */
function formatDataType(dataType) {
    if (!dataType) return 'N/A';
    
    const typeMap = {
        'float32': 'Float32',
        'float64': 'Float64',
        'int8': 'Int8',
        'int16': 'Int16',
        'int32': 'Int32',
        'uint8': 'UInt8',
        'uint16': 'UInt16',
        'uint32': 'UInt32'
    };
    
    return typeMap[dataType.toLowerCase()] || capitalize(dataType);
}

/**
 * Format item count with appropriate units
 */
function formatItemCount(count) {
    if (count === null || count === undefined) return 'N/A';
    
    const num = parseInt(count);
    if (isNaN(num)) return 'Invalid';
    
    if (num === 0) return 'Empty';
    if (num === 1) return '1 item';
    
    if (num >= 1000000) {
        return `${(num / 1000000).toFixed(1)}M items`;
    } else if (num >= 1000) {
        return `${(num / 1000).toFixed(1)}K items`;
    } else {
        return `${formatNumber(num)} items`;
    }
}

/**
 * Format similarity score
 */
function formatSimilarityScore(score) {
    if (score === null || score === undefined) return 'N/A';
    
    const num = parseFloat(score);
    if (isNaN(num)) return 'Invalid';
    
    return `${(num * 100).toFixed(2)}%`;
}

/**
 * Format JSON with syntax highlighting
 */
function formatJSON(obj, options = {}) {
    const {
        indent = 2,
        maxDepth = 10,
        currentDepth = 0
    } = options;
    
    if (currentDepth > maxDepth) {
        return '"[Max depth reached]"';
    }
    
    if (obj === null) return 'null';
    if (obj === undefined) return 'undefined';
    
    if (typeof obj === 'string') {
        return `"${escapeHtml(obj)}"`;
    }
    
    if (typeof obj === 'number' || typeof obj === 'boolean') {
        return obj.toString();
    }
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return '[]';
        
        const items = obj.map(item => 
            ' '.repeat((currentDepth + 1) * indent) + 
            formatJSON(item, { ...options, currentDepth: currentDepth + 1 })
        );
        
        return '[\n' + items.join(',\n') + '\n' + ' '.repeat(currentDepth * indent) + ']';
    }
    
    if (typeof obj === 'object') {
        const keys = Object.keys(obj);
        if (keys.length === 0) return '{}';
        
        const items = keys.map(key => 
            ' '.repeat((currentDepth + 1) * indent) + 
            `"${escapeHtml(key)}": ` + 
            formatJSON(obj[key], { ...options, currentDepth: currentDepth + 1 })
        );
        
        return '{\n' + items.join(',\n') + '\n' + ' '.repeat(currentDepth * indent) + '}';
    }
    
    return obj.toString();
}

/**
 * Create a preview of metadata
 */
function createMetadataPreview(metadata, maxKeys = 3) {
    if (!metadata || typeof metadata !== 'object') {
        return 'No metadata';
    }
    
    const keys = Object.keys(metadata);
    if (keys.length === 0) {
        return 'Empty metadata';
    }
    
    const preview = keys.slice(0, maxKeys).join(', ');
    const remaining = keys.length - maxKeys;
    
    if (remaining > 0) {
        return `${preview} (+${remaining} more)`;
    }
    
    return preview;
}

/**
 * Format error message for display
 */
function formatError(error) {
    if (!error) return 'Unknown error';
    
    if (typeof error === 'string') {
        return error;
    }
    
    if (error.message) {
        return error.message;
    }
    
    if (error.detail) {
        return error.detail;
    }
    
    return error.toString();
}

/**
 * Test S3 URI detection (for debugging)
 */
function testS3URIDetection() {
    const testURI = 's3://automotive-vectors-showcase-490491240736-object/objects/original_texts/5d58c638-ff92-4b1f-9bde-155161a5c66d.txt';
    console.log('Testing S3 URI:', testURI);
    console.log('Is S3 URI:', isS3URI(testURI));
    
    const testMetadata = {
        '__TEXT_REF': testURI,
        'other_field': 'normal value'
    };
    
    const formatted = formatMetadata(testMetadata);
    console.log('Formatted metadata:', formatted);
    
    // Test the specific entry
    const s3Entry = formatted.entries.find(e => e.key === '__TEXT_REF');
    if (s3Entry) {
        console.log('S3 Entry:', s3Entry);
        console.log('Is S3 Link:', s3Entry.isS3Link);
    }
    
    return formatted;
}

// Export functions to global scope
window.isS3URI = isS3URI;
window.highlightSearchTerm = highlightSearchTerm;
window.testS3URIDetection = testS3URIDetection;
window.formatTimestamp = formatTimestamp;
window.formatRelativeTime = formatRelativeTime;
window.formatARN = formatARN;
window.formatARNWithHTML = formatARNWithHTML;
window.extractAccountFromARN = extractAccountFromARN;
window.extractRegionFromARN = extractRegionFromARN;
window.formatNumber = formatNumber;
window.formatBytes = formatBytes;
window.formatPercentage = formatPercentage;
window.formatMetadata = formatMetadata;
window.formatDimension = formatDimension;
window.formatDistanceMetric = formatDistanceMetric;
window.formatDataType = formatDataType;
window.formatItemCount = formatItemCount;
window.formatSimilarityScore = formatSimilarityScore;
window.formatJSON = formatJSON;
window.createMetadataPreview = createMetadataPreview;
window.formatError = formatError;