import pandas as pd
import re

def search_item_in_excel(item_name, selected_file):
    try:
        # Read all sheets from the Excel file
        xls = pd.read_excel(selected_file, sheet_name=None)
        
        results = []
        
        # Iterate through each sheet
        for sheet_name, df in xls.items():
            # Filter rows where any cell contains the item_name (case-insensitive)
            sheet_results = df[df.apply(lambda row: row.astype(str).str.contains(item_name, case=False).any(), axis=1)]
            
            for _, row in sheet_results.iterrows():
                # Convert row to list of string values
                values = row.astype(str).tolist()
                
                # Find all numeric-like values (possibly price)
                number_like = [v for v in values if re.match(r'^[\d,.]+$', v)]
                
                # Extract the unit price from the number-like values
                unit_price = None
                if len(number_like) >= 2:
                    try:
                        unit_price = float(number_like[-2].replace(",", ""))
                    except ValueError:
                        pass
                
                # Get a summary of the first 6 values in the row (modify as needed)
                summary = " ".join(values[:6])
                
                # Append the result with sheet name, summary, and unit price
                results.append({
                    'sheet': sheet_name,
                    'summary': summary,
                    'price': unit_price if unit_price else 'N/A'
                })
        
        return results
    
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}
