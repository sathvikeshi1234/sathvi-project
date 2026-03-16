// // update-html-files.js
// const fs = require('fs');
// const path = require('path');

// // List of HTML files to update
// const htmlFiles = [
//     'chat.html',
//     'custom-fields.html',
//     'customers.html',
//     'ratings.html',
//     'reports.html',
//     'roles.html',
//     'settings.html',
//     'users.html'
// ];

// // The script content to insert
// const scriptContent = `
//     <!-- Core JavaScript -->
//     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
//     <!-- Utility function for loading components -->
//     <script>
//         // Function to load HTML content into an element
//         function loadComponent(url, elementId) {
//             return fetch(url)
//                 .then(response => {
//                     if (!response.ok) throw new Error('Network response was not ok');
//                     return response.text();
//                 })
//                 .then(html => {
//                     const element = document.getElementById(elementId);
//                     if (element) {
//                         element.innerHTML = html;
                        
//                         // If loading the sidebar, set the active nav item
//                         if (url.includes('sidebar.html')) {
//                             const currentPage = window.location.pathname.split('/').pop() || 'index.html';
//                             const pageName = currentPage.replace('.html', '') || 'dashboard';
//                             const activeNavItem = document.querySelector(\`.nav-item[data-page="\${pageName}"]\`);
//                             if (activeNavItem) {
//                                 // Remove active class from all nav items
//                                 document.querySelectorAll('.nav-item').forEach(item => {
//                                     item.classList.remove('active');
//                                 });
//                                 activeNavItem.classList.add('active');
//                             }
//                         }
                        
//                         // If loading the header, initialize it after a short delay
//                         if (url.includes('header.html') && window.initializeHeader) {
//                             setTimeout(() => {
//                                 window.initializeHeader();
//                             }, 50);
//                         }
                        
//                         return true;
//                     }
//                     return false;
//                 })
//                 .catch(error => {
//                     console.error('Error loading component:', error);
//                     return false;
//                 });
//         }
        
//         // Initialize components when DOM is loaded
//         document.addEventListener('DOMContentLoaded', function() {
//             // Load header if container exists
//             if (document.getElementById('header-container')) {
//                 loadComponent('partials/header.html', 'header-container');
//             }
            
//             // Load sidebar if container exists
//             if (document.getElementById('sidebar-container')) {
//                 loadComponent('partials/sidebar.html', 'sidebar-container');
//             }
            
//             // Load modals if container exists
//             if (document.getElementById('modals-container')) {
//                 loadComponent('partials/modals.html', 'modals-container');
//             }
            
//             // Listen for navigation events (for single-page navigation)
//             document.body.addEventListener('click', function(e) {
//                 // Check if the click was on a navigation link
//                 const navLink = e.target.closest('a[data-page]');
//                 if (navLink) {
//                     // Re-initialize header after a short delay to allow the page to update
//                     setTimeout(() => {
//                         if (window.initializeHeader) {
//                             window.initializeHeader();
//                         }
//                     }, 100);
//                 }
//             });
//         });
//     </script>
    
//     <!-- Application Scripts -->
//     <script src="js/script.js"></script>
//     <script src="js/header.js"></script>
// `;

// // Function to update an HTML file
// function updateHtmlFile(filePath) {
//     try {
//         let content = fs.readFileSync(filePath, 'utf8');
        
//         // Remove existing script tags
//         content = content.replace(/<script\b[\s\S]*?<\/script>/gi, '');
        
//         // Remove existing script includes
//         content = content.replace(/<script[^>]*src=["'][^"']*[\/\\]bootstrap\.bundle\.min\.js["'][^>]*><\/script>/gi, '');
//         content = content.replace(/<script[^>]*src=["'][^"']*[\/\\]script\.js["'][^>]*><\/script>/gi, '');
//         content = content.replace(/<script[^>]*src=["'][^"']*[\/\\]header\.js["'][^>]*><\/script>/gi, '');
        
//         // Insert the new script before the closing body tag
//         content = content.replace('</body>', `${scriptContent}</body>`);
        
//         // Write the updated content back to the file
//         fs.writeFileSync(filePath, content, 'utf8');
//         console.log(`Updated: ${filePath}`);
//         return true;
//     } catch (error) {
//         console.error(`Error updating ${filePath}:`, error.message);
//         return false;
//     }
// }

// // Update all HTML files
// htmlFiles.forEach(file => {
//     const filePath = path.join(__dirname, file);
//     if (fs.existsSync(filePath)) {
//         updateHtmlFile(filePath);
//     } else {
//         console.log(`File not found: ${filePath}`);
//     }
// });

// console.log('Update complete!');
