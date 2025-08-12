# Automotive Dataset Generators

This directory contains scripts to generate realistic automotive datasets for testing and development purposes.

## Generated Datasets

### 1. Normalized Dealer Database (`normalized_dealer_database.json`)
- **Purpose**: Comprehensive dealer information with contact details and specialties
- **Structure**: Dealer ID → Dealer information
- **Contains**: Name, region, state, city, location, manufacturer specialties, services, contact info, appointment slots
- **Use Cases**: Dealer recommendation, service routing, appointment scheduling, state-based filtering
- **Enhanced Features**: Multi-state coverage with 100+ cities across all US regions

### 2. Normalized Parts Inventory (`normalized_parts_inventory.json`)
- **Purpose**: Parts availability across dealers with pricing and delivery information
- **Structure**: Part ID → Part details with dealer inventory
- **Contains**: Part name, category, compatible vehicles, dealer-specific pricing and availability
- **Use Cases**: Parts availability checking, price comparison, inventory management

### 3. Normalized Recall Database (`normalized_recall_database.json`)
- **Purpose**: Vehicle recall information with affected models and remedies
- **Structure**: Recall ID → Recall details
- **Contains**: VIN patterns, affected models/years, description, severity, remedy, parts needed
- **Use Cases**: Recall notifications, safety alerts, repair scheduling

### 4. Parts Catalog (`parts_catalog.json`)
- **Purpose**: Comprehensive parts catalog with OEM and aftermarket options
- **Structure**: Category → List of parts with pricing
- **Contains**: Part details, OEM vs aftermarket pricing, compatible vehicles, quantities
- **Use Cases**: Parts lookup, cost estimation, repair planning

### 5. Dealer-OEM Interactions (`dealer_oem_interaction.json`)
- **Purpose**: Dealer-OEM interaction scenarios and communications
- **Structure**: Metadata + List of interaction scenarios
- **Contains**: Dealer info, OEM data, vehicle specs, interaction types, detailed descriptions
- **Use Cases**: Communication tracking, relationship management, service coordination

### 6. Automotive Expert Knowledge (`automotive_expert_knowledge.json`)
- **Purpose**: Technical knowledge base with TSBs, warranty claims, and diagnostic procedures
- **Structure**: Metadata + List of knowledge entries
- **Contains**: Technical service bulletins, warranty information, diagnostic steps, parts lists
- **Use Cases**: Technical support, troubleshooting, training, knowledge management

## Generator Scripts

### Individual Generators

#### `generate_dealer_database.py`
```bash
python generate_dealer_database.py [--count N]
```
- **Default**: 50 dealers
- **Features**: Realistic dealer names, regional distribution, manufacturer specialties
- **Output**: `normalized_dealer_database.json`

#### `generate_parts_inventory.py`
```bash
python generate_parts_inventory.py [--count N]
```
- **Default**: 50 parts
- **Features**: Cross-references dealer database, realistic pricing, availability simulation
- **Output**: `normalized_parts_inventory.json`
- **Dependencies**: Reads `normalized_dealer_database.json` if available

#### `generate_recall_database.py`
```bash
python generate_recall_database.py [--count N]
```
- **Default**: 50 recalls
- **Features**: Realistic VIN patterns, NHTSA numbers, severity levels, affected vehicle counts
- **Output**: `normalized_recall_database.json`
- **Dependencies**: Reads `normalized_dealer_database.json` if available

#### `generate_parts_catalog.py`
```bash
python generate_parts_catalog.py [--count N]
```
- **Default**: 50 parts
- **Features**: OEM vs aftermarket pricing, vehicle compatibility, organized by category
- **Output**: `parts_catalog.json`

#### `dealer_oem_data_generator.py`
```bash
python dealer_oem_data_generator.py [--count N]
```
- **Default**: 50 interactions
- **Features**: Realistic dealer-OEM scenarios, comprehensive metadata, interaction types
- **Output**: `dealer_oem_interaction.json`
- **Dependencies**: Requires `data_models.py` and `data_generator.py`

#### `generate_expert_knowledge.py`
```bash
python generate_expert_knowledge.py [--count N]
```
- **Default**: 50 knowledge entries
- **Features**: Technical service bulletins, warranty claims, diagnostic procedures
- **Output**: `automotive_expert_knowledge.json`

### Master Generator

#### `generate_all_datasets.py`
```bash
# Generate all datasets with default counts (50 each)
python generate_all_datasets.py

# Generate all datasets with custom count
python generate_all_datasets.py --all 100

# Generate with individual counts
python generate_all_datasets.py --dealers 25 --parts 75 --recalls 30 --catalog 60 --oem 40 --expert 80

# Clean existing files and regenerate
python generate_all_datasets.py --clean --all 50
```

**Options:**
- `--dealers N`: Number of dealers (default: 50)
- `--parts N`: Number of parts inventory items (default: 50)
- `--recalls N`: Number of recalls (default: 50)
- `--catalog N`: Number of catalog parts (default: 50)
- `--oem N`: Number of OEM interactions (default: 50)
- `--expert N`: Number of expert knowledge entries (default: 50)
- `--all N`: Set count for all datasets
- `--clean`: Remove existing files before generating

## Data Characteristics

### Realistic Data Features
- **Geographic Distribution**: 5 regions (North, South, East, West, Central) with 30+ states
- **City Coverage**: 100+ cities across all major US states and territories
- **State-Level Data**: Individual state and city information for precise location filtering
- **Comprehensive Coverage**: Includes Alaska, Hawaii, and all continental US states
- **Manufacturer Coverage**: 8+ major automotive manufacturers
- **Part Categories**: brake, engine, transmission, suspension, electrical
- **Price Variations**: Realistic OEM vs aftermarket pricing differences
- **Inventory Simulation**: Realistic stock levels and delivery times
- **Recall Severity**: Proper severity classification (Low, Medium, High, Critical)

### Data Relationships
- Parts inventory references dealer database
- Recalls reference dealer database for recommended service centers
- All datasets use consistent manufacturer and model names
- Cross-references maintain data integrity

## Usage Examples

### Quick Start
```bash
# Generate all datasets with default settings
python generate_all_datasets.py

# Generate larger datasets for testing
python generate_all_datasets.py --all 200

# Generate specific dataset only
python generate_dealer_database.py --count 100
```

### Integration Examples
```python
import json

# Load dealer database
with open('normalized_dealer_database.json', 'r') as f:
    dealers = json.load(f)

# Find BMW dealers in West region
bmw_west_dealers = [
    dealer for dealer in dealers.values()
    if 'BMW' in dealer['manufacturer_specialties'] 
    and dealer['region'] == 'West'
]

# Load parts inventory
with open('normalized_parts_inventory.json', 'r') as f:
    inventory = json.load(f)

# Find brake parts available at specific dealer
dealer_brake_parts = [
    part for part in inventory.values()
    if part['category'] == 'brake' 
    and 'DEALER-001' in part['dealers']
    and part['dealers']['DEALER-001']['quantity'] > 0
]
```

## File Sizes and Performance

### Typical File Sizes (50 items each)
- `normalized_dealer_database.json`: ~25-35 KB
- `normalized_parts_inventory.json`: ~15-25 KB  
- `normalized_recall_database.json`: ~20-30 KB
- `parts_catalog.json`: ~12-20 KB
- `dealer_oem_interaction.json`: ~30-45 KB
- `automotive_expert_knowledge.json`: ~40-60 KB

### Generation Performance
- **Individual generators**: 1-3 seconds each
- **Master generator**: 8-15 seconds total
- **Large datasets (500+ items)**: 15-45 seconds
- **File copying**: Additional 1-2 seconds

## Customization

### Adding New Manufacturers
Edit the manufacturer lists in each generator to add new brands:
```python
self.manufacturers = {
    "Honda": {...},
    "Toyota": {...},
    "YourBrand": {
        "models": ["Model1", "Model2"],
        "vin_patterns": ["PATTERN*"]
    }
}
```

### Adding New Part Categories
Extend the part categories in the generators:
```python
self.part_categories = {
    "brake": {...},
    "engine": {...},
    "your_category": {
        "parts": [...],
        "vehicles": [...]
    }
}
```

### Adjusting Price Ranges
Modify price ranges in the generators to match your market:
```python
"oem_price_range": (min_price, max_price),
"am_price_range": (min_price, max_price)
```

## Dependencies

- **Python 3.7+**
- **Standard library only** (no external dependencies for most generators)
- **Cross-platform** (Windows, macOS, Linux)
- **Note**: `dealer_oem_data_generator.py` requires `data_models.py` and `data_generator.py`

## File Management

### File Management
Generated files are stored in the local data directory for use by the demos.

### Cleanup Script
Use `cleanup_datasets.py` to remove generated files:

```bash
# Remove local files (with confirmation)
python cleanup_datasets.py

# Remove files without confirmation
python cleanup_datasets.py --confirm
```

**Options:**
- `--local`: Remove local data files (default)
- `--confirm`: Skip confirmation prompt

## Data Quality

### Validation Features
- Consistent ID generation across datasets
- Realistic price relationships (OEM > Aftermarket)
- Proper data type validation
- Cross-reference integrity checking

### Statistics Reporting
Each generator provides summary statistics:
- Total items generated
- Distribution across categories/regions
- Value calculations and relationships
- Data quality metrics

## Troubleshooting

### Common Issues
1. **Permission errors**: Ensure write permissions in the data directory
2. **Missing dependencies**: All generators use only standard library
3. **Memory issues**: Large datasets (1000+ items) may require more RAM
4. **File conflicts**: Use `--clean` flag to remove existing files

### Error Messages
- `"Error: Count must be at least 1"`: Provide positive count values
- `"Missing required generator scripts"`: Ensure all .py files are present
- `"normalized_dealer_database.json not found"`: Run dealer generator first

## Contributing

To add new generators or enhance existing ones:
1. Follow the existing naming convention (`generate_*.py`)
2. Include `--count` argument with default of 50
3. Provide summary statistics output
4. Update this README with new generator information
5. Test with various count values (1, 50, 500+)

## License

These generators are part of the S3 Vector automotive showcase project and are provided for educational and testing purposes.