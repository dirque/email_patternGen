// Code35 Integration Script
// Add this after your existing deduplication logic

// Configuration
const EMAIL_API_URL = 'http://localhost:8000';
const BATCH_SIZE = 50; // Process 50 leads at a time
const REQUEST_DELAY = 100; // 100ms delay between batches to avoid overwhelming API

// Email enrichment function
async function enrichLeadsWithEmails(uniqueLeads) {
    console.log(`🚀 Starting email enrichment for ${uniqueLeads.length} leads...`);
    
    const enrichedResults = [];
    let totalSuccessful = 0;
    let totalFailed = 0;
    
    // Process leads in batches
    for (let i = 0; i < uniqueLeads.length; i += BATCH_SIZE) {
        const batch = uniqueLeads.slice(i, i + BATCH_SIZE);
        const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
        const totalBatches = Math.ceil(uniqueLeads.length / BATCH_SIZE);
        
        console.log(`📦 Processing batch ${batchNumber}/${totalBatches} (${batch.length} leads)`);
        
        try {
            const response = await fetch(`${EMAIL_API_URL}/enrich-leads-batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(batch)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const batchResult = await response.json();
            
            if (batchResult.success) {
                enrichedResults.push(...batchResult.enriched_leads);
                totalSuccessful += batchResult.successful_generations;
                totalFailed += batchResult.failed_generations;
                
                console.log(`✅ Batch ${batchNumber} completed: ${batchResult.successful_generations}/${batch.length} emails generated`);
            } else {
                throw new Error('Batch processing failed');
            }
            
        } catch (error) {
            console.error(`❌ Batch ${batchNumber} failed:`, error.message);
            
            // Add original leads without email data if API call fails
            const fallbackLeads = batch.map(lead => ({
                ...lead,
                generatedEmail: null,
                emailConfidence: 0.0,
                emailPattern: null,
                emailReasoning: `API Error: ${error.message}`,
                emailCandidates: []
            }));
            
            enrichedResults.push(...fallbackLeads);
            totalFailed += batch.length;
            
            console.log(`⚠️  Added ${batch.length} leads without emails due to API error`);
        }
        
        // Small delay between batches to avoid overwhelming the API
        if (i + BATCH_SIZE < uniqueLeads.length) {
            await new Promise(resolve => setTimeout(resolve, REQUEST_DELAY));
        }
    }
    
    // Final summary
    console.log(`\n📊 Email Enrichment Summary:`);
    console.log(`   Total leads processed: ${uniqueLeads.length}`);
    console.log(`   Emails generated: ${totalSuccessful} (${(totalSuccessful/uniqueLeads.length*100).toFixed(1)}%)`);
    console.log(`   Failed generations: ${totalFailed} (${(totalFailed/uniqueLeads.length*100).toFixed(1)}%)`);
    
    return enrichedResults;
}

// Health check function to verify API is running
async function checkEmailAPIHealth() {
    try {
        const response = await fetch(`${EMAIL_API_URL}/health`);
        if (response.ok) {
            const health = await response.json();
            console.log(`✅ Email API is healthy: ${health.message}`);
            return true;
        } else {
            console.error(`❌ Email API health check failed: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.error(`❌ Email API is not accessible:`, error.message);
        console.log(`💡 Make sure to start the FastAPI server first:`);
        console.log(`   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`);
        return false;
    }
}

// Integration point in your existing Code35 workflow
// Add this after your deduplication step:

async function processLeadsWithEmails() {
    // Your existing deduplication code...
    // const uniqueLeads = [...]; // Your deduplicated results
    
    // Check if email API is available
    const apiHealthy = await checkEmailAPIHealth();
    
    let finalResults;
    
    if (apiHealthy) {
        // Enrich with emails
        finalResults = await enrichLeadsWithEmails(uniqueLeads);
    } else {
        console.log(`⚠️  Continuing without email enrichment...`);
        finalResults = uniqueLeads.map(lead => ({
            ...lead,
            generatedEmail: null,
            emailConfidence: 0.0,
            emailPattern: null,
            emailReasoning: 'Email API not available',
            emailCandidates: []
        }));
    }
    
    return finalResults;
}

// Example usage - integrate this into your existing Code35 flow:
/*
async function main() {
    // Your existing Code35 processing...
    const rawData = await processRawData();
    const uniqueLeads = await deduplicateLeads(rawData);
    
    // NEW: Add email enrichment
    const enrichedLeads = await enrichLeadsWithEmails(uniqueLeads);
    
    // Continue with your existing workflow...
    console.log('Final enriched results:', enrichedLeads.slice(0, 3)); // Show first 3 for testing
    
    return enrichedLeads;
}
*/

// Utility function to test a single lead
async function testSingleEmail(firstName, lastName, companyDomain, companyIndustry = 'Technology') {
    const testLead = {
        firstName,
        lastName,
        companyDomain,
        companyIndustry,
        companySize: '51-200'
    };
    
    try {
        const response = await fetch(`${EMAIL_API_URL}/generate-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testLead)
        });
        
        const result = await response.json();
        
        console.log(`🧪 Test Results for ${firstName} ${lastName}:`);
        console.log(`   Email: ${result.generated_email}`);
        console.log(`   Confidence: ${(result.confidence_score * 100).toFixed(1)}%`);
        console.log(`   Pattern: ${result.pattern_used}`);
        console.log(`   Candidates: ${result.all_candidates.length}`);
        
        return result;
        
    } catch (error) {
        console.error(`❌ Test failed:`, error.message);
        return null;
    }
}

// Export functions for use in your main Code35 script
module.exports = {
    enrichLeadsWithEmails,
    checkEmailAPIHealth,
    testSingleEmail,
    processLeadsWithEmails
};