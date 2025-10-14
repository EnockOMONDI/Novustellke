/**
 * Novustell Travel - Enhanced Analytics Tracking
 * ==============================================
 * 
 * Travel industry specific analytics tracking for Google Analytics 4
 * Tracks user interactions specific to travel booking and inquiry processes
 */

// Ensure gtag is available (fallback for development)
window.gtag = window.gtag || function() { 
    if (window.console && window.console.log) {
        console.log('GA Event (Dev Mode):', arguments); 
    }
};

/**
 * Travel Package Interaction Tracking
 */
function trackTravelPackageInteraction() {
    // Track package card clicks
    document.querySelectorAll('.package-card, .destination-card, .accommodation-card').forEach(function(card) {
        card.addEventListener('click', function() {
            const packageName = card.querySelector('.package-title, .destination-title, .accommodation-title')?.textContent?.trim() || 'Unknown Package';
            const packageType = card.dataset.packageType || 'general';
            const destination = card.dataset.destination || 'unknown';
            const price = card.dataset.price || 0;
            
            gtag('event', 'view_item', {
                event_category: 'travel_package',
                event_label: packageName,
                item_name: packageName,
                item_category: packageType,
                destination: destination,
                value: parseFloat(price) || 0,
                currency: 'USD'
            });
        });
    });
}

/**
 * Travel Inquiry Form Tracking
 */
function trackTravelInquiryForms() {
    // Track travel inquiry form submissions
    document.querySelectorAll('form[data-form-type="travel-inquiry"], form[data-form-type="student-travel"], form[data-form-type="ngo-travel"], form[data-form-type="mice-travel"]').forEach(function(form) {
        form.addEventListener('submit', function() {
            const formType = form.dataset.formType || 'general-inquiry';
            const destination = form.querySelector('select[name*="destination"], input[name*="destination"]')?.value || 'not-specified';
            const numberOfPeople = form.querySelector('input[name*="students"], input[name*="people"], input[name*="participants"]')?.value || 0;
            const travelType = form.querySelector('select[name*="program"], select[name*="service"]')?.value || 'general';
            
            gtag('event', 'generate_lead', {
                event_category: 'conversion',
                event_label: formType,
                form_type: formType,
                destination: destination,
                number_of_people: parseInt(numberOfPeople) || 0,
                travel_type: travelType,
                value: 50, // Assign lead value
                currency: 'USD'
            });
        });
    });
}

/**
 * Service Page Navigation Tracking
 */
function trackServicePageNavigation() {
    // Track navigation to different service pages
    document.querySelectorAll('a[href*="student-travel"], a[href*="ngo-travel"], a[href*="mice-travel"]').forEach(function(link) {
        link.addEventListener('click', function() {
            const serviceType = link.href.includes('student-travel') ? 'student' : 
                              link.href.includes('ngo-travel') ? 'ngo' : 
                              link.href.includes('mice-travel') ? 'mice' : 'general';
            
            gtag('event', 'service_navigation', {
                event_category: 'navigation',
                event_label: serviceType,
                service_type: serviceType,
                source_page: window.location.pathname
            });
        });
    });
}

/**
 * Model UN Specific Tracking
 */
function trackModelUNInteractions() {
    // Track Model UN section visits
    if (window.location.hash === '#model-un') {
        gtag('event', 'model_un_section_view', {
            event_category: 'engagement',
            event_label: 'Model UN Section',
            section: 'model-un',
            source: 'direct_link'
        });
    }
    
    // Track Model UN form selections
    document.querySelectorAll('select[name="program_stage"]').forEach(function(select) {
        select.addEventListener('change', function() {
            if (select.value === 'Model UN 2025-2026') {
                gtag('event', 'model_un_selection', {
                    event_category: 'engagement',
                    event_label: 'Model UN Program Selected',
                    program_type: 'model-un',
                    academic_year: '2025-2026'
                });
            }
        });
    });
}

/**
 * Contact Method Preference Tracking
 */
function trackContactMethodPreferences() {
    // Track WhatsApp widget interactions
    document.addEventListener('click', function(e) {
        // WhatsApp widget clicks
        if (e.target.closest('.whatsapp-widget, [href*="wa.me"], [href*="whatsapp"]')) {
            gtag('event', 'contact_method_preference', {
                event_category: 'engagement',
                event_label: 'WhatsApp',
                contact_method: 'whatsapp',
                value: 10
            });
        }
        
        // Email link clicks
        if (e.target.closest('a[href^="mailto:"]')) {
            const emailType = e.target.closest('a').href.includes('info@') ? 'general' :
                             e.target.closest('a').href.includes('careers@') ? 'careers' :
                             e.target.closest('a').href.includes('news@') ? 'newsletter' : 'other';
            
            gtag('event', 'contact_method_preference', {
                event_category: 'engagement',
                event_label: 'Email',
                contact_method: 'email',
                email_type: emailType,
                value: 8
            });
        }
        
        // Phone link clicks
        if (e.target.closest('a[href^="tel:"]')) {
            gtag('event', 'contact_method_preference', {
                event_category: 'engagement',
                event_label: 'Phone',
                contact_method: 'phone',
                value: 15
            });
        }
    });
}

/**
 * Blog and Content Engagement Tracking
 */
function trackContentEngagement() {
    // Track blog post reading time
    let startTime = Date.now();
    let engagementTracked = false;
    
    // Track significant reading time (2+ minutes)
    setTimeout(function() {
        if (!engagementTracked && document.visibilityState === 'visible') {
            gtag('event', 'content_engagement', {
                event_category: 'engagement',
                event_label: 'Deep Read',
                page_type: document.body.classList.contains('blog-post') ? 'blog_post' : 'page',
                reading_time: 120,
                value: 5
            });
            engagementTracked = true;
        }
    }, 120000); // 2 minutes
    
    // Track social sharing (if implemented)
    document.querySelectorAll('.social-share-button, [data-share]').forEach(function(button) {
        button.addEventListener('click', function() {
            const platform = button.dataset.platform || 'unknown';
            const contentType = document.body.classList.contains('blog-post') ? 'blog_post' : 'page';
            
            gtag('event', 'share', {
                event_category: 'engagement',
                event_label: platform,
                method: platform,
                content_type: contentType,
                value: 3
            });
        });
    });
}

/**
 * Search and Filter Tracking
 */
function trackSearchAndFilters() {
    // Track site search usage
    document.querySelectorAll('form[role="search"], .search-form, [data-search-form]').forEach(function(form) {
        form.addEventListener('submit', function() {
            const searchInput = form.querySelector('input[type="search"], input[name*="search"], input[name*="query"]');
            if (searchInput && searchInput.value.trim()) {
                gtag('event', 'search', {
                    search_term: searchInput.value.trim(),
                    search_type: form.dataset.searchType || 'site_search'
                });
            }
        });
    });
    
    // Track filter usage (if implemented)
    document.querySelectorAll('.filter-option, [data-filter]').forEach(function(filter) {
        filter.addEventListener('click', function() {
            const filterType = filter.dataset.filterType || 'unknown';
            const filterValue = filter.dataset.filterValue || filter.textContent.trim();
            
            gtag('event', 'filter_usage', {
                event_category: 'engagement',
                event_label: filterType,
                filter_type: filterType,
                filter_value: filterValue
            });
        });
    });
}

/**
 * Error and Performance Tracking
 */
function trackErrorsAndPerformance() {
    // Track JavaScript errors
    window.addEventListener('error', function(e) {
        gtag('event', 'javascript_error', {
            event_category: 'error',
            event_label: e.message,
            error_message: e.message,
            error_filename: e.filename,
            error_line: e.lineno
        });
    });
    
    // Track page load performance
    window.addEventListener('load', function() {
        setTimeout(function() {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                
                gtag('event', 'page_load_time', {
                    event_category: 'performance',
                    event_label: 'Load Time',
                    load_time: Math.round(loadTime),
                    page_type: document.body.className || 'unknown'
                });
            }
        }, 1000);
    });
}

/**
 * Seasonal and Campaign Tracking
 */
function trackSeasonalAndCampaigns() {
    // Track seasonal interest based on current month
    const currentMonth = new Date().getMonth() + 1;
    const season = currentMonth >= 6 && currentMonth <= 8 ? 'peak_travel' :
                  currentMonth >= 12 || currentMonth <= 2 ? 'holiday_season' :
                  currentMonth >= 3 && currentMonth <= 5 ? 'spring_travel' : 'off_season';
    
    // Track session with seasonal context
    gtag('event', 'seasonal_visit', {
        event_category: 'seasonality',
        event_label: season,
        season: season,
        month: currentMonth
    });
    
    // Track campaign parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const campaign = urlParams.get('utm_campaign');
    const source = urlParams.get('utm_source');
    const medium = urlParams.get('utm_medium');
    
    if (campaign || source || medium) {
        gtag('event', 'campaign_visit', {
            event_category: 'marketing',
            event_label: campaign || 'unknown_campaign',
            campaign_name: campaign,
            campaign_source: source,
            campaign_medium: medium
        });
    }
}

/**
 * Initialize all tracking when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tracking functions
    trackTravelPackageInteraction();
    trackTravelInquiryForms();
    trackServicePageNavigation();
    trackModelUNInteractions();
    trackContactMethodPreferences();
    trackContentEngagement();
    trackSearchAndFilters();
    trackErrorsAndPerformance();
    trackSeasonalAndCampaigns();
    
    console.log('🎯 Novustell Travel Analytics: Enhanced tracking initialized');
});

/**
 * Export functions for manual tracking
 */
window.NovustellAnalytics = {
    trackPackageView: function(packageName, packageType, destination, price) {
        gtag('event', 'view_item', {
            event_category: 'travel_package',
            event_label: packageName,
            item_name: packageName,
            item_category: packageType,
            destination: destination,
            value: parseFloat(price) || 0,
            currency: 'USD'
        });
    },
    
    trackInquiry: function(inquiryType, destination, numberOfPeople) {
        gtag('event', 'generate_lead', {
            event_category: 'conversion',
            event_label: inquiryType,
            inquiry_type: inquiryType,
            destination: destination,
            number_of_people: parseInt(numberOfPeople) || 0,
            value: 50,
            currency: 'USD'
        });
    },
    
    trackCustomEvent: function(eventName, parameters) {
        gtag('event', eventName, parameters);
    }
};
