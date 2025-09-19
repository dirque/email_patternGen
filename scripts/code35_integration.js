// Code35 Integration Script
// Configuration
const EMAIL_API_URL = 'http://localhost:8000';
const BATCH_SIZE = 50;
const REQUEST_DELAY = 100;
const ENABLE_VERIFICATION = false; // Set to true to enable email verification

// STEP 1: VALIDATION - Pre-validate leads before API calls
function validateLead(lead) {
    const errors = [];
    
    // Check firstName (required)
    if (!lead.firstName || typeof lead.firstName !== 'string' || lead.firstName.trim().length < 2) {
        errors.push('firstName required (min 2 chars)');
    }
    
    // Check companyDomain (required)  
    if (!lead.companyDomain || typeof lead.companyDomain !== 'string') {
        errors.push('companyDomain required');
    } else {
        // Clean and validate domain format
        const domain = cleanDomain(lead.companyDomain);
        if (!isValidDomain(domain)) {
            errors.push('invalid domain format');
        }
    }
    
    return {
        isValid: errors.length === 0,
        errors,
        cleanedLead: errors.length === 0 ? cleanLead(lead) : null
    };
}

function cleanDomain(domain) {
    if (!domain) return '';
    let cleaned = domain.toLowerCase().trim();
    cleaned = cleaned.replace(/^https?:\/\//, '');
    cleaned = cleaned.replace(/^www\./, '');
    cleaned = cleaned.split('/')[0];
    cleaned = cleaned.split(':')[0];
    return cleaned;
}

function isValidDomain(domain) {
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$/;
    return domainRegex.test(domain) && domain.length >= 4;
}

function cleanLead(lead) {
    const cleaned = { ...lead };
    if (cleaned.firstName) cleaned.firstName = cleaned.firstName.trim();
    if (cleaned.lastName) cleaned.lastName = cleaned.lastName.trim();  
    if (cleaned.companyDomain) cleaned.companyDomain = cleanDomain(cleaned.companyDomain);
    if (cleaned.companyName) cleaned.companyName = cleaned.companyName.trim();
    if (cleaned.companyIndustry) cleaned.companyIndustry = cleaned.companyIndustry.trim();
    return cleaned;
}

function validateBatch(leads) {
    console.log(`Validating ${leads.length} leads...`);
    
    const results = leads.map((lead, index) => ({
        ...validateLead(lead),
        originalIndex: index
    }));
    
    const validLeads = results.filter(r => r.isValid).map(r => r.cleanedLead);
    const invalidLeads = results.filter(r => !r.isValid);
    
    const successRate = (validLeads.length / leads.length * 100).toFixed(1);
    console.log(`Validation: ${validLeads.length}/${leads.length} valid (${successRate}%)`);
    
    if (invalidLeads.length > 0) {
        console.log(`Invalid leads sample:`, invalidLeads.slice(0, 3).map(invalid => ({
            lead: leads[invalid.originalIndex],
            errors: invalid.errors
        })));
    }
    
    return { validLeads, invalidLeads };
}

// STEP 2: ENRICHMENT - Your existing email generation (enhanced)
async function enrichLeadsWithEmails(uniqueLeads) {
    console.log(`Starting email enrichment for ${uniqueLeads.length} leads...`);
    
    // Step 2a: Validate leads first
    const { validLeads, invalidLeads } = validateBatch(uniqueLeads);
    
    if (validLeads.length === 0) {
        console.log(`No valid leads to process`);
        return createFinalResults([], invalidLeads, uniqueLeads);
    }
    
    // Step 2b: Process valid leads through your existing email generation
    const enrichedResults = [];
    let totalSuccessful = 0;
    let totalFailed = 0;
    
    // Process leads in batches
    for (let i = 0; i < validLeads.length; i += BATCH_SIZE) {
        const batch = validLeads.slice(i, i + BATCH_SIZE);
        const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
        const totalBatches = Math.ceil(validLeads.length / BATCH_SIZE);
        
        console.log(`Processing batch ${batchNumber}/${totalBatches} (${batch.length} leads)`);
        
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
                const results = batchResult.enriched_leads || batchResult.results || [];
                enrichedResults.push(...results);
                totalSuccessful += batchResult.successful_generations || 0;
                totalFailed += batchResult.failed_generations || 0;
                
                console.log(`Batch ${batchNumber} completed: ${batchResult.successful_generations}/${batch.length} emails generated`);
            } else {
                throw new Error('Batch processing failed');
            }
            
        } catch (error) {
            console.error(`Batch ${batchNumber} failed:`, error.message);
            
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
        }
        
        // Small delay between batches to avoid overwhelming the API
        if (i + BATCH_SIZE < validLeads.length) {
            await new Promise(resolve => setTimeout(resolve, REQUEST_DELAY));
        }
    }
    
    console.log(`Email enrichment completed: ${totalSuccessful}/${validLeads.length} successful`);
    
    // Step 2c: Optional verification
    const finalResults = ENABLE_VERIFICATION ? 
        await verifyEmails(enrichedResults) : 
        enrichedResults;
    
    // Step 2d: Combine with invalid leads
    return createFinalResults(finalResults, invalidLeads, uniqueLeads);
}

// STEP 3: VERIFICATION - Email verification (optional)
async function verifyEmails(enrichedLeads) {
    if (!ENABLE_VERIFICATION) {
        return enrichedLeads;
    }
    
    console.log(`Starting email verification for ${enrichedLeads.length} leads...`);
    
    const leadsWithEmails = enrichedLeads.filter(lead => lead.generatedEmail);
    console.log(`Verifying ${leadsWithEmails.length} generated emails...`);
    
    // Simple verification based on confidence score (replace with real verification service)
    const verifiedLeads = enrichedLeads.map(lead => {
        if (lead.generatedEmail) {
            const isVerified = lead.emailConfidence > 0.7; // Heuristic - replace with real verification
            
            return {
                ...lead,
                emailVerified: isVerified,
                emailVerificationStatus: isVerified ? 'verified' : 'unverified',
                emailVerificationReason: isVerified ? 'High confidence' : 'Low confidence'
            };
        }
        
        return {
            ...lead,
            emailVerified: false,
            emailVerificationStatus: 'no_email',
            emailVerificationReason: 'No email generated'
        };
    });
    
    const verifiedCount = verifiedLeads.filter(lead => lead.emailVerified).length;
    console.log(`Email verification completed: ${verifiedCount}/${leadsWithEmails.length} verified`);
    
    return verifiedLeads;
}

// Helper function to create final results with all leads
function createFinalResults(enrichedLeads, invalidLeads, originalLeads) {
    const finalResults = [];
    
    // Add enriched leads
    enrichedLeads.forEach(lead => {
        finalResults.push({
            ...lead,
            processingStatus: 'completed'
        });
    });
    
    // Add invalid leads with error info
    invalidLeads.forEach(invalid => {
        const originalLead = originalLeads[invalid.originalIndex];
        finalResults.push({
            ...originalLead,
            generatedEmail: null,
            emailConfidence: 0.0,
            emailPattern: null,
            emailReasoning: `Validation failed: ${invalid.errors.join('; ')}`,
            emailCandidates: [],
            processingStatus: 'validation_failed',
            validationErrors: invalid.errors
        });
    });
    
    // Final summary
    const totalLeads = originalLeads.length;
    const validLeads = enrichedLeads.length;
    const emailsGenerated = enrichedLeads.filter(lead => lead.generatedEmail).length;
    
    console.log(`\nFinal Summary:`);
    console.log(`   Total leads processed: ${totalLeads}`);
    console.log(`   Passed validation: ${validLeads} (${(validLeads/totalLeads*100).toFixed(1)}%)`);
    console.log(`   Emails generated: ${emailsGenerated} (${(emailsGenerated/totalLeads*100).toFixed(1)}%)`);
    
    if (validLeads > 0) {
        console.log(`   Success rate on valid data: ${(emailsGenerated/validLeads*100).toFixed(1)}%`);
    }
    
    return finalResults;
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