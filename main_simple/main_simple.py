#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
import random

# This is a simplified version of the allocation algorithm without using PuLP
def simple_allocate(campers_df, hobby_config, pre_assignments=None, premium_activities=None):
    """
    Simple allocation algorithm without PuLP
    """
    print("Running simplified allocation algorithm (no PuLP)...")
    
    # Get list of campers and hobbies
    campers = list(range(len(campers_df)))
    hobbies = hobby_config['Name'].tolist()
    
    # Initialize allocations dictionary
    allocations = {}
    
    # First, handle pre-assignments if any
    if pre_assignments:
        for i, hobby in pre_assignments.items():
            allocations[i] = hobby
            print(f"Pre-assigned camper {i} to {hobby}")
    
    # Get capacity constraints
    max_capacities = {}
    min_capacities = {}
    for _, row in hobby_config.iterrows():
        hobby = row['Name']
        max_capacities[hobby] = row['Max Capacity']
        min_capacities[hobby] = row['Min Capacity']
    
    # Count how many campers are assigned to each hobby so far
    hobby_counts = {hobby: 0 for hobby in hobbies}
    for hobby in allocations.values():
        if hobby in hobby_counts:
            hobby_counts[hobby] += 1
    
    # Now allocate remaining campers
    unassigned_campers = [i for i in campers if i not in allocations]
    
    # Shuffle to randomize allocation
    random.shuffle(unassigned_campers)
    
    # Create preference matrix (tracking each camper's choices)
    preferences = {}
    for i in unassigned_campers:
        preferences[i] = []
        row = campers_df.iloc[i]
        for j in range(1, 6):
            choice_col = f'Choice {j}'
            if choice_col in row and pd.notna(row[choice_col]) and row[choice_col] in hobbies:
                preferences[i].append(row[choice_col])
    
    # Allocate campers based on preferences and capacity
    choice_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0}
    
    # First pass: try to give everyone their first choice
    for i in unassigned_campers:
        if not preferences[i]:
            continue  # Skip if camper has no preferences
            
        first_choice = preferences[i][0] if preferences[i] else None
        if first_choice and hobby_counts.get(first_choice, 0) < max_capacities.get(first_choice, 0):
            allocations[i] = first_choice
            hobby_counts[first_choice] += 1
            choice_counts[1] += 1
    
    # Second pass: try second choices
    unassigned_campers = [i for i in campers if i not in allocations]
    for i in unassigned_campers:
        if len(preferences[i]) < 2:
            continue  # Skip if camper has no second choice
            
        second_choice = preferences[i][1]
        if hobby_counts.get(second_choice, 0) < max_capacities.get(second_choice, 0):
            allocations[i] = second_choice
            hobby_counts[second_choice] += 1
            choice_counts[2] += 1
    
    # Third pass: try third, fourth, fifth choices
    for choice_rank in [3, 4, 5]:
        unassigned_campers = [i for i in campers if i not in allocations]
        for i in unassigned_campers:
            if len(preferences[i]) < choice_rank:
                continue
                
            choice = preferences[i][choice_rank-1]
            if hobby_counts.get(choice, 0) < max_capacities.get(choice, 0):
                allocations[i] = choice
                hobby_counts[choice] += 1
                choice_counts[choice_rank] += 1
    
    # Last pass: randomly assign any remaining campers
    unassigned_campers = [i for i in campers if i not in allocations]
    for i in unassigned_campers:
        # Find a hobby with space left
        available_hobbies = [h for h in hobbies if hobby_counts.get(h, 0) < max_capacities.get(h, 0)]
        if available_hobbies:
            hobby = random.choice(available_hobbies)
            allocations[i] = hobby
            hobby_counts[hobby] += 1
            choice_counts[0] += 1
    
    # Calculate satisfaction score (percentage of campers getting their top 3 choices)
    total_campers = len(campers)
    satisfaction_score = (choice_counts[1] + choice_counts[2] + choice_counts[3]) / total_campers * 100 if total_campers > 0 else 0
    
    print(f"Allocation complete. Satisfaction score: {satisfaction_score:.2f}%")
    print(f"First choice: {choice_counts[1]} campers ({choice_counts[1]/total_campers*100:.1f}%)")
    print(f"Second choice: {choice_counts[2]} campers ({choice_counts[2]/total_campers*100:.1f}%)")
    print(f"Third choice: {choice_counts[3]} campers ({choice_counts[3]/total_campers*100:.1f}%)")
    print(f"Fourth choice: {choice_counts[4]} campers ({choice_counts[4]/total_campers*100:.1f}%)")
    print(f"Fifth choice: {choice_counts[5]} campers ({choice_counts[5]/total_campers*100:.1f}%)")
    print(f"No choice matched: {choice_counts[0]} campers ({choice_counts[0]/total_campers*100:.1f}%)")
    
    return allocations, satisfaction_score, choice_counts

# Add a function to read pre-assignments similar to your original code
def read_pre_assignments(file_path, campers_df):
    if file_path is None or not os.path.exists(file_path):
        print("No pre-assignments file provided or file does not exist.")
        return {}
            
    print(f"Reading pre-assignments from {file_path}...")
    
    # Read the CSV file
    pre_assignments_df = pd.read_csv(file_path)
    
    # Create dictionary to map camper names to assigned hobbies
    name_to_hobby = {}
    for _, row in pre_assignments_df.iterrows():
        name_to_hobby[row['Full Name']] = row['Assigned Hobby']
    
    # Map to camper indices in the main dataframe
    pre_assignments = {}
    not_found_campers = []
    
    for name, hobby in name_to_hobby.items():
        # Find matching camper in main dataframe
        matching_indices = campers_df.index[campers_df['Full Name'] == name].tolist()
        if matching_indices:
            camper_idx = matching_indices[0]
            pre_assignments[camper_idx] = hobby
        else:
            not_found_campers.append(name)
    
    if not_found_campers:
        print(f"WARNING: Could not find these campers in the main data file: {not_found_campers}")
    
    print(f"Successfully processed {len(pre_assignments)} pre-assignments for campers")
    
    return pre_assignments

# Add other functions you need for generating output files...
def generate_hobby_excel(allocations, campers_df, output_path):
    print(f"Generating hobby-organized Excel file at {output_path}...")
    
    # Create a dictionary to hold DataFrames for each hobby
    hobby_dfs = {}
    
    # Prepare the data for each hobby
    for camper_idx, hobby in allocations.items():
        if hobby not in hobby_dfs:
            hobby_dfs[hobby] = []
        
        camper = campers_df.iloc[camper_idx]
        
        # Check if Cabin column exists
        cabin = "Unknown"
        if 'Cabin' in campers_df.columns:
            cabin = camper['Cabin'] if pd.notna(camper['Cabin']) else "Unknown"
        
        hobby_dfs[hobby].append({
            'Name': camper['Full Name'],
            'Division': camper['Division'],
            'Cabin': cabin
        })
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Create a sheet for each hobby
        for hobby, campers in hobby_dfs.items():
            if not campers:
                continue
                
            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(campers)
            
            # Sort by Division and then Name
            if 'Division' in df.columns and 'Name' in df.columns:
                df = df.sort_values(by=['Division', 'Name'])
            
            # Write to Excel, using hobby name as sheet name
            safe_sheet_name = str(hobby)[:31]  # Excel sheet names have a 31 character limit
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

def generate_division_excel(allocations, campers_df, output_path):
    print(f"Generating division-organized Excel file at {output_path}...")
    
    # Create a dictionary to hold DataFrames for each division
    division_dfs = {}
    
    # Prepare the data for each division
    for camper_idx, hobby in allocations.items():
        camper = campers_df.iloc[camper_idx]
        division = camper['Division']
        
        if division not in division_dfs:
            division_dfs[division] = []
        
        # Check if Cabin column exists
        cabin = "Unknown"
        if 'Cabin' in campers_df.columns:
            cabin = camper['Cabin'] if pd.notna(camper['Cabin']) else "Unknown"
        
        division_dfs[division].append({
            'Cabin': cabin,
            'Name': camper['Full Name'],
            'Assigned Hobby': hobby
        })
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Create a sheet for each division
        for division, campers in division_dfs.items():
            if not campers:
                continue
                
            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(campers)
            
            # Sort by Cabin and then Name
            if 'Cabin' in df.columns and 'Name' in df.columns:
                df = df.sort_values(by=['Cabin', 'Name'])
            
            # Write to Excel, using division name as sheet name
            safe_sheet_name = str(division)[:31]  # Excel sheet names have a 31 character limit
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

def generate_summary(allocations, hobby_config, output_path):
    print(f"Generating summary file at {output_path}...")
    
    # Count campers assigned to each hobby
    hobby_counts = {}
    for hobby in allocations.values():
        if hobby in hobby_counts:
            hobby_counts[hobby] += 1
        else:
            hobby_counts[hobby] = 1
    
    # Create summary DataFrame
    summary_data = []
    for _, row in hobby_config.iterrows():
        hobby_name = row['Name']
        assigned = hobby_counts.get(hobby_name, 0)
        
        # Handle different column names
        location = row.get('Location', 'Unknown')
        leader = row.get('Leader', row.get('Specialty', 'Unknown'))
        allowed_groups = row.get('Allowed Groups', row.get('Allowed Divisions', 'All'))
        
        min_capacity = row['Min Capacity']
        max_capacity = row['Max Capacity']
        
        summary_data.append({
            'Hobby Name': hobby_name,
            'Location': location,
            'Hobby Leader': leader,
            'Allowed Age Groups': allowed_groups,
            'Min Capacity': min_capacity,
            'Max Capacity': max_capacity,
            'Number of Campers Assigned': assigned,
            'Available Slots': max(0, max_capacity - assigned)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_path, index=False)
    
    return summary_df

def create_allocation_bar_chart(summary_df, output_path):
    print(f"Creating hobby allocation visualization at {output_path}...")
    
    # Extract data for plotting
    hobbies = summary_df['Hobby Name'].tolist()
    assigned = summary_df['Number of Campers Assigned'].tolist()
    min_capacities = summary_df['Min Capacity'].tolist()
    max_capacities = summary_df['Max Capacity'].tolist()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot the bars
    bar_width = 0.6
    bar_positions = range(len(hobbies))
    bars = ax.bar(bar_positions, assigned, bar_width, label='Assigned Campers', color='#3498db')
    
    # Add count labels on top of bars
    for i, count in enumerate(assigned):
        ax.text(i, count + 1, str(count), ha='center', va='bottom', fontweight='bold')
    
    # Plot min and max capacity lines
    min_cap_line = None
    max_cap_line = None
    for i, (min_cap, max_cap) in enumerate(zip(min_capacities, max_capacities)):
        min_line = ax.plot([i - bar_width/2, i + bar_width/2], [min_cap, min_cap], 'r-', linewidth=2)
        max_line = ax.plot([i - bar_width/2, i + bar_width/2], [max_cap, max_cap], 'g-', linewidth=2)
        
        if i == 0:
            min_cap_line = min_line[0]
            max_cap_line = max_line[0]
    
    # Set axis labels and title
    ax.set_xlabel('Hobby', fontsize=12)
    ax.set_ylabel('Number of Campers', fontsize=12)
    ax.set_title('Camper Allocation by Hobby', fontsize=16)
    
    # Set x-axis tick labels to hobby names
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(hobbies, rotation=45, ha='right', fontsize=10)
    
    # Add legend
    ax.legend([bars[0], min_cap_line, max_cap_line], 
             ['Assigned Campers', 'Min Capacity', 'Max Capacity'])
    
    # Add grid for easier reading
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300)
    plt.close()

def create_choice_distribution_chart(choice_counts, total_campers, output_path):
    print(f"Creating choice distribution visualization at {output_path}...")
    
    # Extract data for plotting
    choices = ['First Choice', 'Second Choice', 'Third Choice', 'Fourth Choice', 'Fifth Choice', 'No Choice Match']
    counts = [
        choice_counts[1],  # First choice
        choice_counts[2],  # Second choice
        choice_counts[3],  # Third choice
        choice_counts[4],  # Fourth choice
        choice_counts[5],  # Fifth choice
        choice_counts[0],  # No choice match
    ]
    
    # Calculate percentages
    percentages = [count / total_campers * 100 for count in counts] if total_campers > 0 else [0] * len(counts)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Define colors for the bars
    colors = ['#2ecc71', '#27ae60', '#3498db', '#f1c40f', '#e67e22', '#e74c3c']
    
    # Plot the bars
    bar_positions = range(len(choices))
    bars = ax.bar(bar_positions, counts, color=colors)
    
    # Add count and percentage labels on top of bars
    for i, (count, percentage) in enumerate(zip(counts, percentages)):
        if count > 0:  # Only add label if there are campers in this category
            ax.text(i, count + 2, f"{count}\n({percentage:.1f}%)", ha='center', va='bottom', fontweight='bold')
    
    # Set axis labels and title
    ax.set_xlabel('Choice Rank', fontsize=12)
    ax.set_ylabel('Number of Campers', fontsize=12)
    ax.set_title('Distribution of Choice Ranks Assigned', fontsize=16)
    
    # Set x-axis tick labels
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(choices, rotation=0, fontsize=10)
    
    # Add grid for easier reading
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Camp Northland Hobby Allocator (Simple Version)')
    parser.add_argument('--input', type=str, required=True, help='Path to input CSV file with camper preferences')
    parser.add_argument('--config', type=str, required=True, help='Path to hobby configuration CSV file')
    parser.add_argument('--pre-assignments', type=str, help='Path to pre-assignments CSV file')
    parser.add_argument('--premium-activities', type=str, help='Comma-separated list of premium activities')
    parser.add_argument('--restricted-activities', type=str, help='Comma-separated list of restricted activities')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory for output files')
    parser.add_argument('--weight-factor', type=float, default=0.2, help='Weight factor (ignored in simple version)')
    parser.add_argument('--premium-factor', type=float, default=0.1, help='Premium factor (ignored in simple version)')
    parser.add_argument('--previous-allocations', type=str, help='Path to previous allocations CSV file (ignored in simple version)')
    args = parser.parse_args()
    
    # Create timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(args.output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input data
    print(f"Reading camper data from {args.input}...")
    campers_df = pd.read_csv(args.input)
    print(f"Loaded {len(campers_df)} campers")
    
    print(f"Reading hobby configuration from {args.config}...")
    hobby_config = pd.read_csv(args.config)
    print(f"Loaded {len(hobby_config)} hobbies")
    
    # Handle column name variations
    if 'Hobby Name' in hobby_config.columns and 'Name' not in hobby_config.columns:
        hobby_config['Name'] = hobby_config['Hobby Name']
        
    if 'Allowed Groups' in hobby_config.columns and 'Allowed Divisions' not in hobby_config.columns:
        hobby_config['Allowed Divisions'] = hobby_config['Allowed Groups']
    
    # Read pre-assignments if provided
    pre_assignments = None
    if args.pre_assignments:
        pre_assignments = read_pre_assignments(args.pre_assignments, campers_df)
    
    # Get premium activities if specified
    premium_activities = None
    if args.premium_activities:
        premium_activities = [activity.strip() for activity in args.premium_activities.split(',')]
        print(f"Using premium activities: {premium_activities}")
    
    # Run allocation
    allocations, satisfaction_score, choice_counts = simple_allocate(campers_df, hobby_config, pre_assignments, premium_activities)
    
    # Generate output files
    hobby_excel_path = os.path.join(output_dir, 'hobby_allocation.xlsx')
    generate_hobby_excel(allocations, campers_df, hobby_excel_path)
    
    division_excel_path = os.path.join(output_dir, 'division_allocation.xlsx')
    generate_division_excel(allocations, campers_df, division_excel_path)
    
    summary_path = os.path.join(output_dir, 'allocation_summary.csv')
    summary_df = generate_summary(allocations, hobby_config, summary_path)
    
    hobby_viz_path = os.path.join(output_dir, 'allocation_chart.png')
    create_allocation_bar_chart(summary_df, hobby_viz_path)
    
    choice_viz_path = os.path.join(output_dir, 'choice_distribution.png')
    create_choice_distribution_chart(choice_counts, len(campers_df), choice_viz_path)
    
    # Generate master file
    master_path = os.path.join(output_dir, 'master_allocation.xlsx')
    master_df = campers_df.copy()
    master_df['Assigned Hobby'] = None
    for i, hobby in allocations.items():
        master_df.loc[i, 'Assigned Hobby'] = hobby
    master_df.to_excel(master_path, index=False)
    
    print("\nAllocation completed successfully!")
    print(f"Satisfaction score: {satisfaction_score:.2f}%")
    print(f"\nOutput files in: {output_dir}/")

if __name__ == "__main__":
    main()
