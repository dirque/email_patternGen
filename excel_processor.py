# #!/usr/bin/env python3
# """
# Excel Email Enrichment Script
# Reads Excel file, calls FastAPI to generate emails, writes back enriched Excel
# """

# import pandas as pd
# import requests
# import json
# import time
# from datetime import datetime
# import os

# # Configuration
# EXCEL_INPUT_FILE = "data/input/dard2.xlsx"  # Your original Excel file
# EXCEL_OUTPUT_FILE = "data/output/dard2_with_emails.xlsx"  # Output with emails
# API_URL = "http://localhost:8000"
# BATCH_SIZE = 50  # Process in batches
# REQUEST_DELAY = 0.1  # 100ms delay between batches

# def check_api_health():
#     """Check if FastAPI is running"""
#     try:
#         response = requests.get(f"{API_URL}/health", timeout=5)
#         if response.status_code == 200:
#             print("✅ FastAPI is running and healthy")
#             return True
#         else:
#             print(f"❌ FastAPI health check failed: {response.status_code}")
#             return False
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Cannot connect to FastAPI: {e}")
#         print("💡 Make sure to start the FastAPI server first:")
#         print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
#         return False

# def read_excel_file(file_path):
#     """Read Excel file and prepare data for API"""
#     try:
#         print(f"📖 Reading Excel file: {file_path}")
        
#         # Read Excel file
#         df = pd.read_excel(file_path)
#         print(f"✅ Found {len(df)} rows in Excel file")
        
#         # Show column names
#         print(f"📋 Columns found: {list(df.columns)}")
        
#         # Convert to list of dictionaries for API
#         leads = df.to_dict('records')
        
#         # Clean up NaN values (replace with empty strings)
#         for lead in leads:
#             for key, value in lead.items():
#                 if pd.isna(value):
#                     lead[key] = ""
        
#         print(f"✅ Prepared {len(leads)} leads for processing")
#         return leads, df
        
#     except FileNotFoundError:
#         print(f"❌ Excel file not found: {file_path}")
#         print("💡 Make sure to place your dard2.xlsx file in the data/input/ folder")
#         return None, None
#     except Exception as e:
#         print(f"❌ Error reading Excel file: {e}")
#         return None, None

# def enrich_leads_with_emails(leads):
#     """Call FastAPI to enrich leads with emails"""
#     print(f"🚀 Starting email enrichment for {len(leads)} leads...")
    
#     enriched_leads = []
#     total_successful = 0
#     total_failed = 0
    
#     # Process in batches
#     for i in range(0, len(leads), BATCH_SIZE):
#         batch = leads[i:i + BATCH_SIZE]
#         batch_num = (i // BATCH_SIZE) + 1
#         total_batches = (len(leads) + BATCH_SIZE - 1) // BATCH_SIZE
        
#         print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} leads)...")
        
#         try:
#             response = requests.post(
#                 f"{API_URL}/enrich-leads-batch",
#                 json=batch,
#                 headers={'Content-Type': 'application/json'},
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
                
#                 if result.get('success'):
#                     enriched_leads.extend(result['enriched_leads'])
#                     batch_successful = result.get('successful_generations', 0)
#                     batch_failed = result.get('failed_generations', 0)
                    
#                     total_successful += batch_successful
#                     total_failed += batch_failed
                    
#                     print(f"✅ Batch {batch_num} completed: {batch_successful}/{len(batch)} emails generated")
#                 else:
#                     print(f"❌ Batch {batch_num} failed: API returned success=false")
#                     enriched_leads.extend(batch)  # Add original data
#                     total_failed += len(batch)
#             else:
#                 print(f"❌ Batch {batch_num} HTTP error: {response.status_code}")
#                 enriched_leads.extend(batch)  # Add original data
#                 total_failed += len(batch)
                
#         except requests.exceptions.Timeout:
#             print(f"⏰ Batch {batch_num} timed out - adding original data")
#             enriched_leads.extend(batch)
#             total_failed += len(batch)
#         except Exception as e:
#             print(f"❌ Batch {batch_num} error: {e}")
#             enriched_leads.extend(batch)
#             total_failed += len(batch)
        
#         # Small delay between batches
#         if i + BATCH_SIZE < len(leads):
#             time.sleep(REQUEST_DELAY)
    
#     # Summary
#     print(f"\n📊 Email Enrichment Summary:")
#     print(f"   Total leads processed: {len(leads)}")
#     print(f"   Emails generated: {total_successful} ({total_successful/len(leads)*100:.1f}%)")
#     print(f"   Failed generations: {total_failed} ({total_failed/len(leads)*100:.1f}%)")
    
#     return enriched_leads

# def save_enriched_excel(enriched_leads, original_df, output_file):
#     """Save enriched data back to Excel"""
#     try:
#         print(f"💾 Saving enriched data to: {output_file}")
        
#         # Convert enriched leads back to DataFrame
#         enriched_df = pd.DataFrame(enriched_leads)
        
#         # Ensure output directory exists
#         os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
#         # Save to Excel
#         enriched_df.to_excel(output_file, index=False)
        
#         # Show what new columns were added
#         original_columns = set(original_df.columns)
#         new_columns = set(enriched_df.columns) - original_columns
        
#         print(f"✅ Excel file saved successfully!")
#         print(f"📊 Total rows: {len(enriched_df)}")
#         print(f"📊 Total columns: {len(enriched_df.columns)}")
        
#         if new_columns:
#             print(f"🆕 New email columns added: {', '.join(new_columns)}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Error saving Excel file: {e}")
#         return False

# def show_sample_results(enriched_leads, num_samples=5):
#     """Show sample results"""
#     print(f"\n🔍 Sample Results (first {num_samples} leads):")
#     print("-" * 80)
    
#     for i, lead in enumerate(enriched_leads[:num_samples]):
#         name = f"{lead.get('firstName', 'Unknown')} {lead.get('lastName', '')}"
#         company = lead.get('companyName', 'Unknown Company')
#         email = lead.get('generatedEmail', 'No email generated')
#         confidence = lead.get('emailConfidence', 0)
#         pattern = lead.get('emailPattern', 'N/A')
        
#         print(f"{i+1}. {name} @ {company}")
#         print(f"   📧 Email: {email}")
#         print(f"   🎯 Confidence: {confidence:.1%} | Pattern: {pattern}")
#         print()

# def main():
#     """Main processing function"""
#     print("🚀 Excel Email Enrichment Tool")
#     print("=" * 50)
    
#     # Step 1: Check API health
#     if not check_api_health():
#         return False
    
#     # Step 2: Read Excel file
#     leads, original_df = read_excel_file(EXCEL_INPUT_FILE)
#     if leads is None:
#         return False
    
#     # Step 3: Enrich with emails
#     enriched_leads = enrich_leads_with_emails(leads)
    
#     # Step 4: Save results
#     if save_enriched_excel(enriched_leads, original_df, EXCEL_OUTPUT_FILE):
#         # Step 5: Show sample results
#         show_sample_results(enriched_leads)
        
#         print(f"\n🎉 Process completed successfully!")
#         print(f"📁 Input file: {EXCEL_INPUT_FILE}")
#         print(f"📁 Output file: {EXCEL_OUTPUT_FILE}")
#         print(f"💡 Open the output file to see your leads with generated emails!")
        
#         return True
#     else:
#         print(f"\n❌ Process failed during Excel save")
#         return False

# def test_single_row():
#     """Test with just the first row of Excel data"""
#     print("🧪 Testing with single Excel row...")
    
#     leads, _ = read_excel_file(EXCEL_INPUT_FILE)
#     if not leads:
#         return
    
#     # Test with just first lead
#     test_lead = leads[0]
#     print(f"📝 Testing lead: {test_lead.get('firstName', 'Unknown')} {test_lead.get('lastName', '')}")
    
#     try:
#         response = requests.post(
#             f"{API_URL}/generate-email",
#             json=test_lead,
#             headers={'Content-Type': 'application/json'}
#         )
        
#         if response.status_code == 200:
#             result = response.json()
#             print(f"✅ Test successful!")
#             print(f"   📧 Generated: {result.get('generated_email')}")
#             print(f"   🎯 Confidence: {result.get('confidence_score', 0):.1%}")
#             print(f"   📝 Pattern: {result.get('pattern_used')}")
#         else:
#             print(f"❌ Test failed: {response.status_code}")
#             print(f"   Error: {response.text}")
#     except Exception as e:
#         print(f"❌ Test error: {e}")

# if __name__ == "__main__":
#     import sys
    
#     # Check command line arguments
#     if len(sys.argv) > 1 and sys.argv[1] == "test":
#         test_single_row()
#     else:
#         success = main()
#         sys.exit(0 if success else 1)


#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Windows-Friendly Excel Email Enrichment Script
No emojis - pure ASCII for Windows console compatibility
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime
import os
import logging

# Configuration
EXCEL_INPUT_FILE = "data/input/dard2.xlsx"
EXCEL_OUTPUT_FILE = "data/output/dard2_with_emails_complete.xlsx"
API_URL = "http://localhost:8000"
BATCH_SIZE = 25
REQUEST_DELAY = 0.1

# Setup Windows-compatible logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/output/processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_api_health():
    """Check if FastAPI is running"""
    try:
        logger.info("Checking FastAPI health...")
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"SUCCESS: FastAPI is healthy - {health_data.get('message', 'OK')}")
            return True
        else:
            logger.error(f"ERROR: FastAPI health check failed - HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("ERROR: Cannot connect to FastAPI")
        logger.info("HELP: Start with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        logger.error(f"ERROR: Health check failed - {e}")
        return False

def read_excel_file(file_path):
    """Read Excel file and prepare data"""
    try:
        logger.info(f"Reading Excel file: {file_path}")
        
        # Read Excel with proper handling
        df = pd.read_excel(file_path, na_filter=False)
        logger.info(f"SUCCESS: Read {len(df)} rows from Excel")
        logger.info(f"Columns found: {len(df.columns)} total")
        
        # Convert to records and clean data
        leads = df.to_dict('records')
        
        # Clean up data
        for lead in leads:
            for key, value in lead.items():
                if pd.isna(value) or str(value).lower() in ['nan', 'none', 'null']:
                    lead[key] = ""
                else:
                    lead[key] = str(value).strip()
        
        # Quick data quality check
        valid_leads = 0
        for lead in leads:
            if lead.get('firstName') and lead.get('companyDomain'):
                valid_leads += 1
        
        logger.info(f"Data quality: {valid_leads}/{len(leads)} leads have required fields")
        
        return leads, df
        
    except FileNotFoundError:
        logger.error(f"ERROR: Excel file not found - {file_path}")
        logger.info("HELP: Place your Excel file in data/input/ folder")
        return None, None
    except Exception as e:
        logger.error(f"ERROR: Failed to read Excel - {e}")
        return None, None

def enrich_leads_with_emails(leads):
    """Process leads through email API"""
    logger.info(f"Starting email enrichment for {len(leads)} leads...")
    
    enriched_leads = []
    total_successful = 0
    total_failed = 0
    
    # Process in batches
    for i in range(0, len(leads), BATCH_SIZE):
        batch = leads[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(leads) + BATCH_SIZE - 1) // BATCH_SIZE
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} leads)")
        
        try:
            response = requests.post(
                f"{API_URL}/enrich-leads-batch",
                json=batch,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    enriched_leads.extend(result['results'])
                    batch_successful = result.get('successful_generations', 0)
                    batch_failed = result.get('failed_generations', 0)
                    
                    total_successful += batch_successful
                    total_failed += batch_failed
                    
                    logger.info(f"SUCCESS: Batch {batch_num} completed - {batch_successful}/{len(batch)} emails generated")
                else:
                    logger.error(f"ERROR: Batch {batch_num} failed - API returned success=false")
                    enriched_leads.extend(batch)
                    total_failed += len(batch)
            else:
                logger.error(f"ERROR: Batch {batch_num} HTTP error - {response.status_code}")
                enriched_leads.extend(batch)
                total_failed += len(batch)
                
        except Exception as e:
            logger.error(f"ERROR: Batch {batch_num} failed - {e}")
            enriched_leads.extend(batch)
            total_failed += len(batch)
        
        # Small delay between batches
        if i + BATCH_SIZE < len(leads):
            time.sleep(REQUEST_DELAY)
    
    # Summary
    logger.info(f"SUMMARY: Email enrichment completed")
    logger.info(f"  Total leads: {len(leads)}")
    logger.info(f"  Emails generated: {total_successful} ({total_successful/len(leads)*100:.1f}%)")
    logger.info(f"  Failed: {total_failed} ({total_failed/len(leads)*100:.1f}%)")
    
    return enriched_leads

def save_results(enriched_leads, original_df, output_file):
    """Save enriched data to Excel"""
    try:
        logger.info(f"Saving results to: {output_file}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Convert to DataFrame and save
        enriched_df = pd.DataFrame(enriched_leads)
        enriched_df.to_excel(output_file, index=False)
        
        # Show what was added
        original_columns = set(original_df.columns)
        new_columns = set(enriched_df.columns) - original_columns
        
        logger.info(f"SUCCESS: Excel saved")
        logger.info(f"  Total rows: {len(enriched_df)}")
        logger.info(f"  Total columns: {len(enriched_df.columns)}")
        logger.info(f"  New email columns: {len(new_columns)}")
        
        if new_columns:
            logger.info(f"  Added columns: {', '.join(sorted(new_columns))}")
        
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Failed to save Excel - {e}")
        return False

def show_sample_results(enriched_leads, num_samples=5):
    """Show sample results"""
    logger.info(f"Sample results (first {num_samples} leads):")
    logger.info("-" * 60)
    
    for i, lead in enumerate(enriched_leads[:num_samples]):
        name = f"{lead.get('firstName', 'Unknown')} {lead.get('lastName', '')}"
        company = lead.get('companyName', 'Unknown Company')
        email = lead.get('generatedEmail', 'No email generated')
        confidence = lead.get('emailConfidence', 0)
        pattern = lead.get('emailPattern', 'N/A')
        
        logger.info(f"{i+1}. {name} @ {company}")
        logger.info(f"   Email: {email}")
        logger.info(f"   Confidence: {confidence:.1%} | Pattern: {pattern}")
        logger.info("")
    
    # Statistics
    with_emails = [lead for lead in enriched_leads if lead.get('generatedEmail')]
    high_confidence = [lead for lead in with_emails if lead.get('emailConfidence', 0) >= 0.8]
    medium_confidence = [lead for lead in with_emails if 0.6 <= lead.get('emailConfidence', 0) < 0.8]
    low_confidence = [lead for lead in with_emails if lead.get('emailConfidence', 0) < 0.6]
    
    logger.info("Confidence distribution:")
    logger.info(f"  High (>=80%): {len(high_confidence)}")
    logger.info(f"  Medium (60-79%): {len(medium_confidence)}")
    logger.info(f"  Low (<60%): {len(low_confidence)}")
    logger.info(f"  No email: {len(enriched_leads) - len(with_emails)}")
    
    # Pattern analysis
    if with_emails:
        patterns = {}
        for lead in with_emails:
            pattern = lead.get('emailPattern', 'unknown')
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        logger.info("Pattern usage:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {pattern}: {count} ({count/len(with_emails)*100:.1f}%)")

def main():
    """Main processing function"""
    logger.info("Excel Email Enrichment Tool - Windows Compatible")
    logger.info("=" * 60)
    
    # Step 1: Health check
    if not check_api_health():
        return False
    
    # Step 2: Read Excel
    leads, original_df = read_excel_file(EXCEL_INPUT_FILE)
    if leads is None:
        return False
    
    # Step 3: Enrich with emails
    enriched_leads = enrich_leads_with_emails(leads)
    
    # Step 4: Save results
    if save_results(enriched_leads, original_df, EXCEL_OUTPUT_FILE):
        # Step 5: Show results
        show_sample_results(enriched_leads)
        
        logger.info("COMPLETED: Processing finished successfully!")
        logger.info(f"Input: {EXCEL_INPUT_FILE}")
        logger.info(f"Output: {EXCEL_OUTPUT_FILE}")
        logger.info("Open the output Excel file to see your leads with emails!")
        
        return True
    else:
        logger.error("FAILED: Processing failed during save")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)