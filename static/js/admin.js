// Admin Dashboard JS Logic

let currentPage = 1;
const limit = 8; // Items per page
let searchQuery = '';
let statusFilter = '';
let selectedStudent = null;

// On page load
document.addEventListener('DOMContentLoaded', () => {
    loadRegistrations();
});

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

    setTimeout(() => toast.classList.add('show'), 50);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Format SQLite timestamps nicely
function formatDate(timestampStr) {
    if (!timestampStr) return 'N/A';
    try {
        // SQLite timezone defaults to UTC/Z, parse and represent nicely
        const date = new Date(timestampStr.replace(' ', 'T') + 'Z');
        if (isNaN(date.getTime())) {
            // fallback if browser fails parsing
            return timestampStr;
        }
        return date.toLocaleDateString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch (e) {
        return timestampStr;
    }
}

// Fetch and render registrations
async function loadRegistrations() {
    const tableBody = document.getElementById('admin-table-body');
    const offset = (currentPage - 1) * limit;
    
    // Construct query parameters
    const params = new URLSearchParams({
        limit: limit,
        offset: offset,
        search: searchQuery,
        status: statusFilter
    });

    try {
        const response = await fetch(`/students?${params.toString()}`);
        if (response.status === 401) {
            // Unauthorized session, send back to login
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        // Clear table
        tableBody.innerHTML = '';
        
        if (data.students && data.students.length > 0) {
            data.students.forEach(student => {
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = (e) => {
                    // Prevent drawer trigger if clicking specifically an action button
                    if (e.target.tagName !== 'BUTTON') {
                        openDrawer(student.id);
                    }
                };

                // Determine badge class
                let statusBadge = '';
                if (student.status === 'Submitted') statusBadge = '<span class="badge badge-submitted">Submitted</span>';
                else if (student.status === 'Approved') statusBadge = '<span class="badge badge-approved">Approved</span>';
                else if (student.status === 'Rejected') statusBadge = '<span class="badge badge-rejected">Rejected</span>';

                tr.innerHTML = `
                    <td style="font-weight: 600; color: var(--secondary);">${student.registration_id}</td>
                    <td>${student.first_name} ${student.last_name}</td>
                    <td>${student.course_name}</td>
                    <td>${student.email}</td>
                    <td>${student.phone}</td>
                    <td>${statusBadge}</td>
                    <td>${formatDate(student.created_at)}</td>
                    <td>
                        <button class="pagination-btn" style="padding: 0.25rem 0.6rem; font-size: 0.8rem;" onclick="openDrawer(${student.id})">
                            View Info
                        </button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 3rem;">
                        No registrations match your search filters.
                    </td>
                </tr>
            `;
        }

        // Update Pagination controls
        const total = data.total || 0;
        const totalPages = Math.ceil(total / limit) || 1;
        
        document.getElementById('pagination-info').textContent = `Page ${currentPage} of ${totalPages}`;
        document.getElementById('table-summary-info').textContent = `Showing ${Math.min(offset + 1, total)}-${Math.min(offset + limit, total)} of ${total} entries`;
        
        document.getElementById('prev-page-btn').disabled = (currentPage === 1);
        document.getElementById('next-page-btn').disabled = (currentPage === totalPages || total === 0);

    } catch (err) {
        console.error(err);
        showToast("Error loading registration records.", "error");
    }
}

// Input search listener (with debounce layout)
let searchTimeout;
function handleSearchInput() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        searchQuery = document.getElementById('admin-search').value.trim();
        currentPage = 1;
        loadRegistrations();
    }, 300);
}

// Status dropdown listener
function handleFilterChange() {
    statusFilter = document.getElementById('admin-status-filter').value;
    currentPage = 1;
    loadRegistrations();
}

// Pagination navigation
function changePage(direction) {
    currentPage += direction;
    loadRegistrations();
}

// Export CSV
function exportCSV() {
    const params = new URLSearchParams({
        search: searchQuery,
        status: statusFilter
    });
    // Triggers file download in browser
    window.location.href = `/students/export?${params.toString()}`;
}

// Drawer details loader
async function openDrawer(studentId) {
    try {
        const response = await fetch(`/students/${studentId}`);
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            showToast("Failed to fetch student details.", "error");
            return;
        }

        const data = await response.json();
        const student = data.student;
        const history = data.history || [];
        
        selectedStudent = student;

        // Populate drawer text
        document.getElementById('drawer-student-name').textContent = `${student.first_name} ${student.last_name}`;
        document.getElementById('drawer-student-course').textContent = student.course_name;
        document.getElementById('drawer-reg-id').textContent = student.registration_id;
        document.getElementById('drawer-dob').textContent = student.date_of_birth;
        document.getElementById('drawer-gender').textContent = student.gender;
        document.getElementById('drawer-created').textContent = formatDate(student.created_at);
        document.getElementById('drawer-email').textContent = student.email;
        document.getElementById('drawer-phone').textContent = student.phone;
        document.getElementById('drawer-address').textContent = student.address;

        // Set status badge
        const badge = document.getElementById('drawer-student-status');
        badge.textContent = student.status;
        badge.className = 'badge';
        if (student.status === 'Submitted') badge.classList.add('badge-submitted');
        else if (student.status === 'Approved') badge.classList.add('badge-approved');
        else if (student.status === 'Rejected') badge.classList.add('badge-rejected');

        // Manage Decision panel visibility
        const actionBox = document.getElementById('admin-actions-container');
        const remarksInput = document.getElementById('action-remarks');
        remarksInput.value = ''; // clear input
        
        if (student.status === 'Submitted') {
            actionBox.style.display = 'block';
        } else {
            actionBox.style.display = 'none';
        }

        // Render Timeline history logs
        renderTimeline(history);

        // Open drawer animations
        document.getElementById('drawer-overlay').classList.add('open');
        document.getElementById('student-drawer').classList.add('open');

    } catch (err) {
        console.error(err);
        showToast("Error loading application drawer details.", "error");
    }
}

// Close drawer panel
function closeDrawer() {
    document.getElementById('drawer-overlay').classList.remove('open');
    document.getElementById('student-drawer').classList.remove('open');
    selectedStudent = null;
}

// Draw history timeline logs
function renderTimeline(historyList) {
    const timeline = document.getElementById('drawer-timeline');
    timeline.innerHTML = '';

    if (historyList.length === 0) {
        timeline.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No history trails recorded.</p>';
        return;
    }

    historyList.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'timeline-item';
        
        // determine timeline marker styling
        if (item.new_status === 'Approved') itemDiv.classList.add('approved');
        else if (item.new_status === 'Rejected') itemDiv.classList.add('rejected');
        else if (item.new_status === 'Submitted') itemDiv.classList.add('submitted');

        const remarksText = item.remarks ? `<p class="timeline-remarks">${item.remarks}</p>` : '';

        itemDiv.innerHTML = `
            <div class="timeline-marker"></div>
            <div class="timeline-info">${formatDate(item.changed_at)} by ${item.changed_by}</div>
            <div class="timeline-status">Transitioned to ${item.new_status}</div>
            ${remarksText}
        `;
        timeline.appendChild(itemDiv);
    });
}

// Perform status change operations (Approve/Reject)
async function updateRegistrationStatus(decision) {
    if (!selectedStudent) return;

    const remarks = document.getElementById('action-remarks').value.trim();
    
    // We send request to app.py endpoints /students/<id>/approve or /reject
    const url = `/students/${selectedStudent.id}/${decision}`;
    
    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ remarks: remarks })
        });

        const result = await response.json();
        
        if (response.ok) {
            showToast(`Application successfully ${decision === 'approve' ? 'Approved' : 'Rejected'}!`, "success");
            closeDrawer();
            loadRegistrations(); // refresh list
        } else {
            showToast(result.error || "Decision action failed.", "error");
        }
    } catch (err) {
        console.error(err);
        showToast("Error updating application status.", "error");
    }
}

// Admin logout session termination
async function logoutAdmin() {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        } else {
            showToast("Logout failed.", "error");
        }
    } catch (e) {
        console.error(e);
        window.location.href = '/login';
    }
}
