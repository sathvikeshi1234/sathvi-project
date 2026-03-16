// ============================================
// DARK MODE
// ============================================
const themeToggle = document.getElementById("theme-toggle")
const htmlElement = document.documentElement
const body = document.body

// Initialize dark mode from localStorage
function initializeDarkMode() {
  const stored = localStorage.getItem("darkMode")
  const isDarkMode = stored === "true" || stored === "enabled"
  if (isDarkMode) {
    body.classList.add("dark-mode")
    if (themeToggle) updateThemeIcon()
  }
}

function updateThemeIcon() {
  if (!themeToggle) return
  const icon = themeToggle.querySelector("i")
  if (!icon) return
  if (body.classList.contains("dark-mode")) {
    icon.classList.remove("bi-moon-stars")
    icon.classList.add("bi-sun-fill")
  } else {
    icon.classList.remove("bi-sun-fill")
    icon.classList.add("bi-moon-stars")
  }
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    body.classList.toggle("dark-mode")
    const isDarkMode = body.classList.contains("dark-mode")
    localStorage.setItem("darkMode", isDarkMode ? "true" : "false")
    updateThemeIcon()
  })
}

// ============================================
// SIDEBAR TOGGLE
// ============================================
const sidebarToggle = document.getElementById("sidebar-toggle")
const sidebar = document.querySelector(".sidebar")

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed")
    localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"))
  })
}

// Initialize sidebar state from localStorage
function initializeSidebar() {
  const sidebar = document.querySelector(".sidebar")
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true"
  if (isCollapsed && sidebar) {
    sidebar.classList.add("collapsed")
  }
}

const sidebarToggleMobile = document.getElementById("mobile-sidebar-toggle")
const sidebarMobile = document.querySelector(".sidebar")

if (sidebarToggleMobile && sidebarMobile) {
  sidebarToggleMobile.addEventListener("click", () => {
    sidebarMobile.classList.toggle("collapsed")
    localStorage.setItem("sidebarCollapsed", sidebarMobile.classList.contains("collapsed"))
  })
}

// ============================================
// PAGE NAVIGATION
// ============================================
const navItems = document.querySelectorAll(".nav-item")
const pageContents = document.querySelectorAll(".page-content")

navItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault()
    const pageName = item.dataset.page

    // Remove active class from all items and pages
    navItems.forEach((nav) => nav.classList.remove("active"))
    pageContents.forEach((page) => page.classList.remove("active"))

    // Add active class to clicked item and corresponding page
    item.classList.add("active")
    const pageElement = document.getElementById(pageName)
    if (pageElement) {
      pageElement.classList.add("active")
    }
  })
})

// ============================================
// NOTIFICATIONS
// ============================================
const notificationsBtn = document.getElementById("notifications-btn")
const notificationsDropdown = document.getElementById("notifications-dropdown")
const profileBtn = document.getElementById("profile-btn")
const profileDropdown = document.getElementById("profile-dropdown")

if (notificationsBtn && notificationsDropdown && profileDropdown) {
  notificationsBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    notificationsDropdown.classList.toggle("show")
    profileDropdown.classList.remove("show")
  })
}

if (profileBtn && profileDropdown && notificationsDropdown) {
  profileBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    profileDropdown.classList.toggle("show")
    notificationsDropdown.classList.remove("show")
  })
}

document.addEventListener("click", () => {
  if (notificationsDropdown) notificationsDropdown.classList.remove("show")
  if (profileDropdown) profileDropdown.classList.remove("show")
})

const profileDropdownItems = document.querySelectorAll(".profile-dropdown .dropdown-item")
profileDropdownItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault()
    const action = item.dataset.action

    if (action === "profile") {
      navItems.forEach((nav) => nav.classList.remove("active"))
      pageContents.forEach((page) => page.classList.remove("active"))

      const profilePage = document.getElementById("profile")
      if (profilePage) {
        profilePage.classList.add("active")
      }

      // Note: profile is not in sidebar nav, so we don't need to activate a nav item
    } else if (action === "settings") {
      // Navigate to settings page
      navItems.forEach((nav) => nav.classList.remove("active"))
      pageContents.forEach((page) => page.classList.remove("active"))
      document.getElementById("settings").classList.add("active")
      const settingsNav = document.querySelector('.nav-item[data-page="settings"]')
      if (settingsNav) settingsNav.classList.add("active")
    }

    profileDropdown.classList.remove("show")
  })
})

// ============================================
// CHAT PAGE
// ============================================
const contactItems = document.querySelectorAll(".contact-item")
const chatMessages = document.getElementById("messages-tab")
const infoTab = document.getElementById("info-tab")
const tabButtons = document.querySelectorAll(".tab-btn")

contactItems.forEach((item) => {
  item.addEventListener("click", () => {
    // Remove active class from all contacts
    contactItems.forEach((contact) => contact.classList.remove("active"))

    // Add active class to clicked contact
    item.classList.add("active")

    // Show messages tab by default - only if elements exist
    if (chatMessages && infoTab && tabButtons.length > 0) {
      tabButtons.forEach((btn) => btn.classList.remove("active"))
      chatMessages.style.display = "flex"
      infoTab.style.display = "none"
      tabButtons[0].classList.add("active")
    }
  })
})

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const tabName = btn.dataset.tab

    // Remove active class from all tabs
    tabButtons.forEach((tab) => tab.classList.remove("active"))

    // Hide all tabs - only if elements exist
    if (chatMessages && infoTab) {
      chatMessages.style.display = "none"
      infoTab.style.display = "none"

      // Show selected tab
      btn.classList.add("active")
      if (tabName === "messages") {
        chatMessages.style.display = "flex"
      } else if (tabName === "info") {
        infoTab.style.display = "block"
      }
    }
  })
})

// ============================================
// SETTINGS PAGE
// ============================================
const settingItems = document.querySelectorAll(".settings-item")
const settingPanels = document.querySelectorAll(".setting-panel")

settingItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault()
    const settingName = item.dataset.setting

    // Remove active class
    settingItems.forEach((setting) => setting.classList.remove("active"))
    settingPanels.forEach((panel) => panel.classList.remove("active"))

    // Add active class
    item.classList.add("active")
    const panelId = `${settingName}-panel`
    document.getElementById(panelId).classList.add("active")
  })
})

// ============================================
// SEARCH FUNCTIONALITY
// ============================================
const searchInput = document.getElementById("search-input")
const ticketsTable = document.getElementById("tickets-table")

if (searchInput && ticketsTable) {
  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase()
    const rows = ticketsTable.querySelectorAll("tr")

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase()
      row.style.display = text.includes(searchTerm) ? "" : "none"
    })
  })
}

// ============================================
// CHAT BUTTON IN HEADER
// ============================================
const chatBtnHeader = document.getElementById("chat-btn")
if (chatBtnHeader) {
  chatBtnHeader.addEventListener("click", (e) => {
    e.preventDefault()
    navItems.forEach((nav) => nav.classList.remove("active"))
    pageContents.forEach((page) => page.classList.remove("active"))
    const chatPage = document.getElementById("chat")
    if (chatPage) {
      chatPage.classList.add("active")
    }
    // Find and activate chat nav item
    const chatNav = document.querySelector('.nav-item[data-page="chat"]')
    if (chatNav) chatNav.classList.add("active")
    notificationsDropdown.classList.remove("show")
    profileDropdown.classList.remove("show")
  })
}

// ============================================
// INITIALIZE
// ============================================
document.addEventListener("DOMContentLoaded", () => {
  initializeDarkMode()
  initializeSidebar()

  // Set first contact as active by default
  if (contactItems.length > 0) {
    contactItems[0].click()
  }
})

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatDate(date) {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function showToast(message, type = "info") {
  const toast = document.createElement("div")
  toast.className = `alert alert-${type} alert-dismissible fade show`
  toast.setAttribute("role", "alert")
  toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  const container = document.querySelector(".content-area")
  container.insertBefore(toast, container.firstChild)

  setTimeout(() => {
    toast.remove()
  }, 5000)
}
