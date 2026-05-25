// Web Traffic Tracker SDK

(function() {
    // Generate or retrieve session ID
    function getSessionId() {
        let sessionId = sessionStorage.getItem('wt_session_id');
        if (!sessionId) {
            sessionId = 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            sessionStorage.setItem('wt_session_id', sessionId);
        }
        return sessionId;
    }

    // Generate or retrieve user ID
    function getUserId() {
        let userId = localStorage.getItem('wt_user_id');
        if (!userId) {
            userId = 'usr_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            localStorage.setItem('wt_user_id', userId);
        }
        return userId;
    }

    const TRACKING_API_URL = 'http://localhost:8000/track';
    
    function sendEvent(eventType, metadata = {}) {
        const payload = {
            session_id: getSessionId(),
            user_id: getUserId(),
            event_type: eventType,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            metadata: metadata
        };

        // Send via beacon if available (better for page unloads), else fetch
        if (navigator.sendBeacon) {
            navigator.sendBeacon(TRACKING_API_URL, JSON.stringify(payload));
        } else {
            fetch(TRACKING_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            }).catch(e => console.error("Tracking error:", e));
        }
    }

    // Automatically track page view on load
    window.addEventListener('load', () => {
        sendEvent('page_view', { title: document.title });
    });

    // Track clicks on specific elements (e.g., links or buttons)
    window.addEventListener('click', (e) => {
        const target = e.target.closest('a, button');
        if (target) {
            sendEvent('click', {
                element_type: target.tagName,
                element_text: target.innerText || target.value,
                element_href: target.href || ''
            });
        }
    });

    // Expose a public function for custom events
    window.WebTracker = {
        track: sendEvent
    };
})();
