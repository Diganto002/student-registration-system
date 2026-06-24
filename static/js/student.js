// Student Portal JS Logic

// Tab Switching logic
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => 
        btn.getAttribute('onclick').includes(tabId)
    );
    if (activeBtn) activeBtn.classList.add('active');
    
    const targetContent = document.getElementById(tabId);
    if (targetContent) targetContent.classList.add('active');
}

// Toast Notifications Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    // Trigger transition
    setTimeout(() => toast.classList.add('show'), 50);

    // Destroy after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Client Side Validation
function validateForm(data) {
    const errors = {};
    
    // Name validation
    const nameRegex = /^[A-Za-z\s]+$/;
    if (!data.first_name || data.first_name.trim().length < 2 || data.first_name.trim().length > 50) {
        errors.first_name = "First name must be between 2 and 50 characters.";
    } else if (!nameRegex.test(data.first_name)) {
        errors.first_name = "First name must contain only alphabetic characters.";
    }

    if (!data.last_name || data.last_name.trim().length < 2 || data.last_name.trim().length > 50) {
        errors.last_name = "Last name must be between 2 and 50 characters.";
    } else if (!nameRegex.test(data.last_name)) {
        errors.last_name = "Last name must contain only alphabetic characters.";
    }

    // Email validation
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    if (!data.email || !emailRegex.test(data.email)) {
        errors.email = "Please enter a valid email address.";
    }

    // Phone validation
    const phoneRegex = /^\d{11}$/;
    if (!data.phone || !phoneRegex.test(data.phone)) {
        errors.phone = "Phone number must be exactly 11 digits (numbers only).";
    }

    // DOB validation
    if (!data.date_of_birth) {
        errors.date_of_birth = "Date of birth is required.";
    } else {
        const dob = new Date(data.date_of_birth);
        const today = new Date();
        if (dob >= today) {
            errors.date_of_birth = "Date of birth must be in the past.";
        } else {
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }
            if (age < 16) {
                errors.date_of_birth = "Student must be at least 16 years old.";
            }
        }
    }

    // Gender validation
    if (!data.gender) {
        errors.gender = "Gender selection is required.";
    }

    // Address validation
    if (!data.address || data.address.trim().length === 0) {
        errors.address = "Address is required.";
    } else if (data.address.trim().length > 255) {
        errors.address = "Address must not exceed 255 characters.";
    }

    // Course validation
    if (!data.course_name) {
        errors.course_name = "Please select a target course.";
    }

    return errors;
}

// Clear all error message elements
function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
    });
}

// Submit Registration via AJAX
async function submitRegistration(event) {
    event.preventDefault();
    clearErrors();

    const form = document.getElementById('registration-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Run client side checks
    const clientErrors = validateForm(data);
    if (Object.keys(clientErrors).length > 0) {
        for (const [key, msg] of Object.entries(clientErrors)) {
            const errSpan = document.getElementById(`err-${key}`);
            if (errSpan) errSpan.textContent = msg;
        }
        showToast("Please correct the highlighted form errors.", "error");
        return;
    }

    const submitBtn = document.getElementById('submit-reg-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting Application...';

    try {
        const response = await fetch('/students', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (response.ok) {
            // Success
            showToast("Application submitted successfully!", "success");
            
            // Hide Form and Show Success Card
            form.style.display = 'none';
            document.querySelector('#register-tab h2').style.display = 'none';
            document.querySelector('#register-tab p').style.display = 'none';
            
            const displayRegId = document.getElementById('display-reg-id');
            displayRegId.textContent = result.registration_id;
            
            document.getElementById('success-screen-wrapper').style.display = 'block';
        } else {
            // Server-side validation errors or duplicate data
            if (result.errors) {
                for (const [key, msg] of Object.entries(result.errors)) {
                    const errSpan = document.getElementById(`err-${key}`);
                    if (errSpan) errSpan.textContent = msg;
                }
                showToast("Submission failed: Please check entered details.", "error");
            } else {
                showToast(result.error || "An error occurred during submission.", "error");
            }
        }
    } catch (err) {
        console.error(err);
        showToast("Network error. Please try again later.", "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Application 🚀';
    }
}

// Reset form to submit again
function resetForm() {
    const form = document.getElementById('registration-form');
    form.reset();
    clearErrors();

    // Show form elements
    form.style.display = 'block';
    document.querySelector('#register-tab h2').style.display = 'block';
    document.querySelector('#register-tab p').style.display = 'block';
    
    // Hide success screen
    document.getElementById('success-screen-wrapper').style.display = 'none';
}

// Go to tracker tab and auto fill registration ID
function switchToTracker() {
    const newRegId = document.getElementById('display-reg-id').textContent;
    resetForm();
    switchTab('track-tab');
    
    const queryInput = document.getElementById('track-query');
    queryInput.value = newRegId;
    trackStatus();
}

// Track Status query logic
async function trackStatus() {
    const queryInput = document.getElementById('track-query');
    const query = queryInput.value.trim();
    const errorSpan = document.getElementById('track-error');
    const resultCard = document.getElementById('lookup-result');
    
    errorSpan.textContent = '';
    resultCard.style.display = 'none';

    if (!query) {
        errorSpan.textContent = "Please enter an Email, Phone Number, or Registration ID.";
        return;
    }

    const trackBtn = document.getElementById('track-btn');
    trackBtn.disabled = true;
    trackBtn.textContent = 'Searching...';

    try {
        const response = await fetch(`/students/track?query=${encodeURIComponent(query)}`);
        const result = await response.json();

        if (response.ok) {
            // Populating UI card fields
            document.getElementById('lookup-name').textContent = `${result.first_name} ${result.last_name}`;
            document.getElementById('lookup-course').textContent = result.course_name;
            document.getElementById('lookup-reg-id').textContent = result.registration_id;
            
            // Format dates
            const dateObj = new Date(result.created_at);
            document.getElementById('lookup-date').textContent = dateObj.toLocaleDateString(undefined, {
                year: 'numeric', month: 'long', day: 'numeric'
            });
            
            document.getElementById('lookup-email').textContent = result.email;
            document.getElementById('lookup-phone').textContent = result.phone;

            // Set badge class
            const badge = document.getElementById('lookup-status-badge');
            badge.textContent = result.status;
            badge.className = 'badge'; // clear original status classes
            
            if (result.status === 'Submitted') badge.classList.add('badge-submitted');
            else if (result.status === 'Approved') badge.classList.add('badge-approved');
            else if (result.status === 'Rejected') badge.classList.add('badge-rejected');

            resultCard.style.display = 'block';
            showToast("Registration record found.", "success");
        } else {
            errorSpan.textContent = result.error || "No matching registration record found.";
            showToast("Search failed: No record matches that input.", "error");
        }
    } catch (err) {
        console.error(err);
        errorSpan.textContent = "Network error. Please try again.";
    } finally {
        trackBtn.disabled = false;
        trackBtn.textContent = 'Track 🔍';
    }
}
