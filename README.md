# Camp Northland Hobby Allocator

A web application for automating the allocation of campers to hobby activities based on their preferences, optimizing for overall satisfaction while respecting constraints.

## Overview

Camp Northland runs a program called "Hobbies" where campers select and rank their preferred activities. This application:

- Optimally assigns campers to activities based on their preferences
- Respects activity minimum and maximum capacity constraints
- Ensures campers from the same division/section are grouped together
- Handles pre-assignments and restricted activities
- Prioritizes campers who didn't get top choices in previous weeks
- Provides detailed visualizations and reports

## Features

- **User-friendly Interface**: Upload files and adjust parameters through a simple web UI
- **Powerful Optimization**: Uses PuLP mixed-integer programming to find optimal allocations
- **Privacy-Focused**: All data is processed temporarily and not stored permanently
- **Comprehensive Outputs**:
  - Excel files organized by hobby and division
  - Summary reports with capacity information
  - Visualizations of allocations and preference distributions
  - Priority tracking for multi-week programs

## Usage

1. Upload the required CSV files:
   - Camper preferences (with their top 5 choices)
   - Hobby configuration (with capacities and allowed divisions)

2. Optionally upload:
   - Pre-assignment file (for campers who must be assigned to specific hobbies)
   - Previous allocations file (to prioritize campers who didn't get top choices before)

3. Adjust parameters as needed:
   - Priority weight factor
   - Premium activity factor
   - Restricted activities

4. Click "Run Allocation" and wait for processing to complete

5. View results and download output files

## Input File Formats

### Camper Preferences CSV
Required columns:
- Full Name: Camper's name
- Division: Age group and gender (e.g., "Section 1" or "Unit 2")
- Choice 1 through Choice 5: Hobby preferences

### Hobby Configuration CSV
Required columns:
- Hobby Name/Name: Name of the activity
- Min Capacity: Minimum number of campers
- Max Capacity: Maximum number of campers
- Allowed Groups/Allowed Divisions: Comma-separated list of divisions allowed to join

Optional columns:
- Location: Where the activity takes place
- Leader/Specialty: Who runs the activity
- Premium: "Yes"/"No" - Is this a premium activity?
- Restricted: "Yes"/"No" - Is this restricted to pre-assigned campers only?

### Pre-assignments CSV (Optional)
- Full Name: Camper's name
- Assigned Hobby: Hobby to which they must be assigned

### Previous Allocations CSV (Optional)
- Full Name: Camper's name
- Division: Age group
- Assigned Hobby: Previously assigned hobby
- Choice Rank: Which choice they got (1-5, or 0 for no match)

## Installation for Local Development

```bash
git clone https://github.com/yourusername/camp-northland-hobby-allocator.git
cd camp-northland-hobby-allocator
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

This application is deployed on Streamlit Community Cloud. You can access it at: [https://camp-northland-hobby-allocator.streamlit.app](https://camp-northland-hobby-allocator.streamlit.app)

## License

[MIT License](LICENSE)
