// Initialize
let tickets = JSON.parse(localStorage.getItem("tickets")) || []
const THEME_KEY = "tickethub-theme"
const AUTH_TOKEN_KEY = "tickethub-auth-token"
const USER_DATA_KEY = "tickethub-user-data"
const bootstrap = window.bootstrap // Declare the bootstrap variable

// Authentication State
let isAuthenticated = false;
let currentUser = null;

// Theme Management
const themeToggle = document.getElementById("themeToggle")
if (themeToggle) {
  themeToggle.addEventListener("click", toggleTheme)
}

function toggleTheme() {
  const currentTheme = localStorage.getItem(THEME_KEY) || "light"
  const newTheme = currentTheme === "light" ? "dark" : "light"

  localStorage.setItem(THEME_KEY, newTheme)
  applyTheme(newTheme)
}

function applyTheme(theme) {
  if (theme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark")
    document.body.classList.add("dark-mode")
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>'
  } else {
    document.documentElement.removeAttribute("data-theme")
    document.body.classList.remove("dark-mode")
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>'
  }
}

// Apply saved theme and check auth status on load
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem(THEME_KEY) || "light"
  applyTheme(savedTheme)
  checkAuthStatus()
  renderDashboard()
  setupAuthEventListeners()
})

// Authentication Functions
function checkAuthStatus() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  const userData = JSON.parse(localStorage.getItem(USER_DATA_KEY) || 'null')
  
  if (token && userData) {
    isAuthenticated = true
    currentUser = userData
    updateUIForAuthenticatedUser(userData)
  } else {
    isAuthenticated = false
    currentUser = null
    updateUIForGuest()
  }
}

function setupAuthEventListeners() {
  // Login form submission
  const loginForm = document.getElementById('loginForm')
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin)
  }

  // Register form submission
  const registerForm = document.getElementById('registerForm')
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister)
  }

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn')
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout)
  }
}

async function handleLogin(e) {
  e.preventDefault()
  
  const email = document.getElementById('loginEmail').value
  const password = document.getElementById('loginPassword').value
  const rememberMe = document.getElementById('rememberMe').checked

  try {
    // In a real app, you would make an API call here
    // const response = await fetch('/api/auth/login', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ email, password })
    // })
    // const data = await response.json()

    // Mock response for demo
    const data = {
      token: 'mock-jwt-token',
      user: {
        id: '123',
        firstName: 'John',
        lastName: 'Doe',
        email: email
      }
    }

    // Store token and user data
    localStorage.setItem(AUTH_TOKEN_KEY, data.token)
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user))
    
    // Update state and UI
    isAuthenticated = true
    currentUser = data.user
    updateUIForAuthenticatedUser(data.user)
    
    // Close modal and show success message
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'))
    loginModal.hide()
    showToast('Login successful!')
    
  } catch (error) {
    console.error('Login failed:', error)
    showToast('Login failed. Please try again.', 'error')
  }
}

async function handleRegister(e) {
  e.preventDefault()
  
  const firstName = document.getElementById('firstName').value
  const lastName = document.getElementById('lastName').value
  const email = document.getElementById('registerEmail').value
  const password = document.getElementById('registerPassword').value
  const confirmPassword = document.getElementById('confirmPassword').value

  if (password !== confirmPassword) {
    showToast('Passwords do not match', 'error')
    return
  }

  try {
    // In a real app, you would make an API call here
    // const response = await fetch('/api/auth/register', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ firstName, lastName, email, password })
    // })
    // const data = await response.json()

    // Mock response for demo
    const data = {
      token: 'mock-jwt-token',
      user: {
        id: '123',
        firstName,
        lastName,
        email
      }
    }

    // Store token and user data
    localStorage.setItem(AUTH_TOKEN_KEY, data.token)
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user))
    
    // Update state and UI
    isAuthenticated = true
    currentUser = data.user
    updateUIForAuthenticatedUser(data.user)
    
    // Close modal and show success message
    const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'))
    registerModal.hide()
    showToast('Registration successful!')
    
  } catch (error) {
    console.error('Registration failed:', error)
    showToast('Registration failed. Please try again.', 'error')
  }
}

function handleLogout() {
  // Clear auth data
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(USER_DATA_KEY)
  
  // Update state
  isAuthenticated = false
  currentUser = null
  
  // Update UI
  updateUIForGuest()
  showToast('Logged out successfully')
}

function updateUIForAuthenticatedUser(user) {
  // Hide login/register buttons
  const authButtons = document.querySelectorAll('.auth-buttons')
  authButtons.forEach(btn => btn.style.display = 'none')
  
  // Show user dropdown and create ticket button
  const userDropdown = document.querySelector('.user-dropdown')
  const createTicketBtn = document.querySelector('.create-ticket-btn')
  
  if (userDropdown) {
    userDropdown.classList.remove('d-none')
    const userNameElement = userDropdown.querySelector('.user-name')
    if (userNameElement) {
      userNameElement.textContent = `${user.firstName} ${user.lastName}`
    }
  }
  
  if (createTicketBtn) {
    createTicketBtn.classList.remove('d-none')
  }
  
  // Update any protected UI elements
  const startTrialBtn = document.querySelector('.start-trial-btn')
  if (startTrialBtn) {
    startTrialBtn.innerHTML = '<i class="fas fa-ticket-alt me-2"></i>Create Ticket'
    startTrialBtn.setAttribute('data-bs-target', '#ticketModal')
  }
}

function updateUIForGuest() {
  // Show login/register buttons
  const authButtons = document.querySelectorAll('.auth-buttons')
  authButtons.forEach(btn => btn.style.display = 'block')
  
  // Hide user dropdown and create ticket button
  const userDropdown = document.querySelector('.user-dropdown')
  const createTicketBtn = document.querySelector('.create-ticket-btn')
  
  if (userDropdown) {
    userDropdown.classList.add('d-none')
  }
  
  if (createTicketBtn) {
    createTicketBtn.classList.add('d-none')
  }
  
  // Update any protected UI elements
  const startTrialBtn = document.querySelector('.start-trial-btn')
  if (startTrialBtn) {
    startTrialBtn.innerHTML = '<i class="fas fa-sparkles me-2"></i>Start Free Trial'
    startTrialBtn.setAttribute('data-bs-target', '#loginModal')
  }
}

// Ticket Form Handling
const ticketForm = document.getElementById("ticketForm")
const submitTicketBtn = document.getElementById("submitTicket")

if (submitTicketBtn && ticketForm) {
  submitTicketBtn.addEventListener("click", () => {
  if (ticketForm.checkValidity() === false) {
    event.preventDefault()
    event.stopPropagation()
    ticketForm.classList.add("was-validated")
    return
  }

  const title = document.getElementById("ticketTitle").value
  const category = document.getElementById("ticketCategory").value
  const priority = document.getElementById("ticketPriority").value
  const email = document.getElementById("ticketEmail").value
  const description = document.getElementById("ticketDescription").value

  const ticket = {
    id: generateTicketId(),
    title,
    category,
    priority,
    email,
    description,
    status: "pending",
    date: new Date().toLocaleDateString(),
    timestamp: new Date().getTime(),
  }

  tickets.unshift(ticket)
  localStorage.setItem("tickets", JSON.stringify(tickets))

  showToast(`Ticket #${ticket.id} created successfully!`)
  ticketForm.reset()
  ticketForm.classList.remove("was-validated")

  // Close modal
  const modal = bootstrap.Modal.getInstance(document.getElementById("ticketModal"))
  modal.hide()

  renderDashboard()
  })
}

// Generate Ticket ID
function generateTicketId() {
  return "TK" + String(tickets.length + 1).padStart(5, "0")
}

// Render Dashboard
function renderDashboard() {
  const tableBody = document.getElementById("ticketsTableBody")
  const noTicketsMessage = document.getElementById("noTicketsMessage")

  // Update stats
  const total = tickets.length
  const pending = tickets.filter((t) => t.status === "pending").length
  const resolved = tickets.filter((t) => t.status === "resolved").length
  const critical = tickets.filter((t) => t.priority === "critical").length

  document.getElementById("statTotal").textContent = total
  document.getElementById("statPending").textContent = pending
  document.getElementById("statResolved").textContent = resolved
  document.getElementById("statCritical").textContent = critical

  if (tickets.length === 0) {
    tableBody.innerHTML = ""
    noTicketsMessage.style.display = "block"
    return
  }

  noTicketsMessage.style.display = "none"

  tableBody.innerHTML = tickets
    .map(
      (ticket) => `
        <tr>
            <td><strong>${ticket.id}</strong></td>
            <td>${ticket.title}</td>
            <td><span class="badge bg-info">${ticket.category}</span></td>
            <td><span class="badge bg-${getPriorityColor(ticket.priority)}">${ticket.priority.toUpperCase()}</span></td>
            <td><span class="badge bg-${getStatusColor(ticket.status)}">${ticket.status.toUpperCase()}</span></td>
            <td>${ticket.date}</td>
            <td>
                <div class="btn-group" role="group">
                    <select class="form-select form-select-sm" onchange="updateTicketStatus('${ticket.id}', this.value)" style="max-width: 120px;">
                        <option value="pending" ${ticket.status === "pending" ? "selected" : ""}>Pending</option>
                        <option value="progress" ${ticket.status === "progress" ? "selected" : ""}>Progress</option>
                        <option value="resolved" ${ticket.status === "resolved" ? "selected" : ""}>Resolved</option>
                    </select>
                    <button class="btn btn-sm btn-danger" onclick="deleteTicket('${ticket.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `,
    )
    .join("")
}

// Update Ticket Status
function updateTicketStatus(id, status) {
  const ticket = tickets.find((t) => t.id === id)
  if (ticket) {
    ticket.status = status
    localStorage.setItem("tickets", JSON.stringify(tickets))
    renderDashboard()
    showToast(`Ticket #${id} status updated to ${status}`)
  }
}

// Delete Ticket
function deleteTicket(id) {
  if (confirm("Are you sure you want to delete this ticket?")) {
    tickets = tickets.filter((t) => t.id !== id)
    localStorage.setItem("tickets", JSON.stringify(tickets))
    renderDashboard()
    showToast("Ticket deleted successfully")
  }
}

// Search Tickets
document.getElementById("searchTickets")?.addEventListener("keyup", (e) => {
  const searchTerm = e.target.value.toLowerCase()
  const rows = document.querySelectorAll("#ticketsTableBody tr")

  rows.forEach((row) => {
    const text = row.textContent.toLowerCase()
    row.style.display = text.includes(searchTerm) ? "" : "none"
  })
})

// Export Tickets
function exportTickets() {
  if (tickets.length === 0) {
    showToast("No tickets to export")
    return
  }

  let csv = "ID,Title,Category,Priority,Status,Email,Date\n"

  tickets.forEach((ticket) => {
    csv += `${ticket.id},"${ticket.title}",${ticket.category},${ticket.priority},${ticket.status},${ticket.email},${ticket.date}\n`
  })

  const blob = new Blob([csv], { type: "text/csv" })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `tickets-${new Date().toISOString().split("T")[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)

  showToast("Tickets exported successfully")
}

// Utility Functions
function getPriorityColor(priority) {
  const colors = {
    low: "success",
    medium: "warning",
    high: "danger",
    critical: "dark",
  }
  return colors[priority] || "secondary"
}

function getStatusColor(status) {
  const colors = {
    pending: "warning",
    progress: "info",
    resolved: "success",
  }
  return colors[status] || "secondary"
}

function showToast(message) {
  const toast = document.getElementById("successToast")
  document.getElementById("toastMessage").textContent = message
  const bootstrapToast = new bootstrap.Toast(toast)
  bootstrapToast.show()
}

// File Upload Area
const uploadArea = document.querySelector(".upload-area")
if (uploadArea) {
  uploadArea.addEventListener("click", () => {
    document.getElementById("ticketAttachment").click()
  })

  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault()
    uploadArea.style.background = "linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(236, 72, 153, 0.2))"
  })

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.background = "linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(236, 72, 153, 0.05))"
  })

  document.getElementById("ticketAttachment")?.addEventListener("change", (e) => {
    const file = e.target.files[0]
    if (file) {
      uploadArea.innerHTML = `
                <i class="fas fa-check-circle" style="color: #10b981;"></i>
                <p style="color: #10b981; margin: 0;"><strong>${file.name}</strong> uploaded!</p>
            `
    }
  })
}

// Scroll Animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.animation = "slideIn 0.6s ease-out"
      observer.unobserve(entry.target)
    }
  })
}, observerOptions)

document.querySelectorAll("section").forEach((section) => {
  observer.observe(section)
})
