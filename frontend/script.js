// E-Book Navigation and Features - Professional Novel Layout
class EBookReader {
    
    constructor() {
        this.currentPage = 0;
        this.totalPages = 30; // Now only 30 pages
        this.fontSize = 12; // Default font size in pt (matches Garamond 12pt)
        this.isDarkMode = false;
        
        // Library card system variables
        this.currentUser = null;
        this.currentSession = null;
        this.userStats = null;
        
        // Touch/swipe variables
        this.startX = 0;
        this.endX = 0;
        
        this.initializeElements();
        this.bindEvents();
        this.updatePageInfo();
        this.applyFontSize();
        this.initializeStoryPages(); // Hide story pages by default - require library card login
        this.checkExistingSession();
    }

    initializeElements() {
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.pageInfo = document.getElementById('pageInfo');
        this.fontSizeBtn = document.getElementById('fontSizeBtn');
        this.themeBtn = document.getElementById('themeBtn');
        this.progressBar = document.getElementById('progressBar');
        this.pages = document.querySelectorAll('.page');
        
        // Library card elements
        this.libraryIdInput = document.getElementById('libraryIdInput');
        this.loginBtn = document.getElementById('loginBtn');
        this.createCardBtn = document.getElementById('createCardBtn');
        this.loginStatus = document.getElementById('loginStatus');
        this.loginSection = document.getElementById('loginSection');
        this.userInfoSection = document.getElementById('userInfoSection');
        this.displayLibraryId = document.getElementById('displayLibraryId');
        this.accessCount = document.getElementById('accessCount');
        this.totalPagesRead = document.getElementById('totalPagesRead');
        this.logoutBtn = document.getElementById('logoutBtn');
        
        // Name input elements
        this.femaleNameInput = document.getElementById('femaleNameInput');
        this.maleNameInput = document.getElementById('maleNameInput');
        this.setNamesBtn = document.getElementById('setNamesBtn');
        this.nameStatus = document.getElementById('nameStatus');
    }

    bindEvents() {
        this.prevBtn.addEventListener('click', () => this.previousPage());
        this.nextBtn.addEventListener('click', () => this.nextPage());
        this.fontSizeBtn.addEventListener('click', () => this.toggleFontSize());
        this.themeBtn.addEventListener('click', () => this.toggleTheme());
        
        // Library card events
        this.loginBtn.addEventListener('click', () => this.loginUser());
        this.createCardBtn.addEventListener('click', () => this.createNewUser());
        this.logoutBtn.addEventListener('click', () => this.logoutUser());
        this.setNamesBtn.addEventListener('click', () => this.saveNamesAndStartReading());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.previousPage();
            if (e.key === 'ArrowRight') this.nextPage();
        });

        // Touch/swipe support for mobile
        document.addEventListener('touchstart', (e) => {
            this.startX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', (e) => {
            this.endX = e.changedTouches[0].screenX;
            this.handleSwipe();
        });
    }

    checkExistingSession() {
        // Check if user is already logged in
        const savedUser = localStorage.getItem('ebookUser');
        const savedSession = localStorage.getItem('ebookSession');
        
        if (savedUser && savedSession) {
            try {
                this.currentUser = JSON.parse(savedUser);
                this.currentSession = JSON.parse(savedSession);
                this.showUserInterface();
                this.loadUserStats();
            } catch (e) {
                this.clearStoredData();
            }
        }
    }

    async createNewUser() {
        try {
            this.createCardBtn.disabled = true;
            this.createCardBtn.textContent = 'Creating...';
            
            const response = await fetch(frontendConfig.createUserUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentUser = {
                    user_id: data.user_id,
                    library_id: data.library_id
                };
                
                this.libraryIdInput.value = data.library_id;
                this.showStatus('New library card created! Please login.', 'success');
            } else {
                this.showStatus('Failed to create library card: ' + data.error, 'error');
            }
        } catch (error) {
            this.showStatus('Network error. Please try again.', 'error');
        } finally {
            this.createCardBtn.disabled = false;
            this.createCardBtn.textContent = 'New Card';
        }
    }

    async loginUser() {
        const libraryId = this.libraryIdInput.value.trim();
        
        if (!libraryId) {
            this.showStatus('Please enter your Library ID', 'error');
            return;
        }
        
        try {
            this.loginBtn.disabled = true;
            this.loginBtn.textContent = 'Logging in...';
            
            const response = await fetch(frontendConfig.loginUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ library_id: libraryId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentUser = {
                    user_id: data.user_id,
                    library_id: data.library_id
                };
                this.currentSession = {
                    session_id: data.session_id
                };
                
                // Save to localStorage
                localStorage.setItem('ebookUser', JSON.stringify(this.currentUser));
                localStorage.setItem('ebookSession', JSON.stringify(this.currentSession));
                
                this.showUserInterface();
                this.loadUserStats();
                this.showStatus('Login successful!', 'success');
            } else {
                this.showStatus('Login failed: ' + data.error, 'error');
            }
        } catch (error) {
            this.showStatus('Network error. Please try again.', 'error');
        } finally {
            this.loginBtn.disabled = false;
            this.loginBtn.textContent = 'Login';
        }
    }

    showUserInterface() {
        this.loginSection.style.display = 'none';
        this.userInfoSection.style.display = 'block';
        this.displayLibraryId.textContent = this.currentUser.library_id;
    }

    async loadUserStats() {
        try {
            const response = await fetch(`${frontendConfig.userStatsUrl}/${this.currentUser.user_id}`);
            const data = await response.json();
            
            if (data.success) {
                this.userStats = data;
                this.accessCount.textContent = data.user.access_count;
                this.totalPagesRead.textContent = data.session_stats.total_pages_read;
            }
        } catch (error) {
            console.error('Failed to load user stats:', error);
        }
    }

    logoutUser() {
        if (this.currentSession) {
            this.endCurrentSession();
        }
        
        this.clearStoredData();
        this.currentUser = null;
        this.currentSession = null;
        this.userStats = null;
        
        this.loginSection.style.display = 'block';
        this.userInfoSection.style.display = 'none';
        this.libraryIdInput.value = '';
        this.showStatus('Logged out successfully', 'success');
        
        // Hide story pages when logged out - require login to read
        this.hideStoryPages();
    }

    clearStoredData() {
        localStorage.removeItem('ebookUser');
        localStorage.removeItem('ebookSession');
        localStorage.removeItem('ebookFemaleName');
        localStorage.removeItem('ebookMaleName');
        localStorage.removeItem('whenHeartsWhisper_bookmark');
    }

    async saveNamesAndStartReading() {
        const femaleName = this.femaleNameInput.value.trim() || 'Sameena';
        const maleName = this.maleNameInput.value.trim() || 'Sanjay';

        this.setNamesBtn.disabled = true;
        this.setNamesBtn.textContent = 'Saving...';

        try {
            const saved = await this.saveNamesToDatabase(femaleName, maleName);

            if (saved) {
                localStorage.setItem('ebookFemaleName', femaleName);
                localStorage.setItem('ebookMaleName', maleName);
                this.showNameStatus('Names set! Enjoy your story.', 'success');
                this.replaceNamesInBook(femaleName, maleName);
                this.showStoryPages();
            } else {
                this.showNameStatus('Failed to save. Please try again.', 'error');
            }
        } catch (error) {
            this.showNameStatus('Network error. Please try again.', 'error');
        } finally {
            this.setNamesBtn.disabled = false;
            this.setNamesBtn.textContent = 'Start Reading';
        }
    }

    async saveNamesToDatabase(female, male) {
                    const response = await fetch(frontendConfig.saveNamesUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_id: this.currentUser.user_id,
                female, 
                male 
            })
        });
        return response.ok;
    }

    async updateSessionProgress() {
        if (this.currentSession) {
            try {
                await fetch(frontendConfig.updateSessionUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        session_id: this.currentSession.session_id,
                        pages_read: this.currentPage + 1
                    })
                });
            } catch (error) {
                console.error('Failed to update session:', error);
            }
        }
    }

    async endCurrentSession() {
        if (this.currentSession) {
            try {
                await fetch(frontendConfig.endSessionUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        session_id: this.currentSession.session_id
                    })
                });
            } catch (error) {
                console.error('Failed to end session:', error);
            }
        }
    }

    showStatus(message, type) {
        this.loginStatus.style.display = 'block';
        this.loginStatus.textContent = message;
        this.loginStatus.style.color = type === 'success' ? '#16a34a' : '#ef4444';
        
        setTimeout(() => {
            this.loginStatus.style.display = 'none';
        }, 3000);
    }

    showNameStatus(message, type) {
        this.nameStatus.style.display = 'block';
        this.nameStatus.textContent = message;
        this.nameStatus.style.color = type === 'success' ? '#16a34a' : '#ef4444';
    }

    hideStoryPages() {
        const storyPages = document.querySelectorAll('.page:not(#page-0)');
        storyPages.forEach(page => page.style.display = 'none');
    }

    showStoryPages() {
        const storyPages = document.querySelectorAll('.page:not(#page-0)');
        storyPages.forEach(page => page.style.display = '');
    }

    // Hide story pages by default - require library card login
    initializeStoryPages() {
        this.hideStoryPages();
    }

    replaceNamesInBook(female, male) {
        document.querySelectorAll('.novel-text').forEach(el => {
            el.innerHTML = el.innerHTML
                .replace(/Sameena/g, female)
                .replace(/Sanjay/g, male);
        });
    }

    handleSwipe() {
        const swipeThreshold = 50;
        const diff = this.startX - this.endX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.nextPage();
            } else {
                this.previousPage();
            }
        }
    }

    showPage(pageIndex) {
        // Hide all pages
        this.pages.forEach(page => {
            page.classList.remove('active');
        });

        // Show current page
        if (this.pages[pageIndex]) {
            this.pages[pageIndex].classList.add('active');
        }

        this.currentPage = pageIndex;
        this.updatePageInfo();
        this.updateNavigationButtons();
        this.updateProgress();
        this.updateSessionProgress();
        
        // Smooth scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    nextPage() {
        if (this.currentPage < this.totalPages - 1) {
            this.showPage(this.currentPage + 1);
        }
    }

    previousPage() {
        if (this.currentPage > 0) {
            this.showPage(this.currentPage - 1);
        }
    }

    updatePageInfo() {
        this.pageInfo.textContent = `Page ${this.currentPage + 1} of ${this.totalPages}`;
    }

    updateNavigationButtons() {
        this.prevBtn.disabled = this.currentPage === 0;
        this.nextBtn.disabled = this.currentPage === this.totalPages - 1;
        
        if (this.currentPage === 0) {
            this.prevBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            this.prevBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
        
        if (this.currentPage === this.totalPages - 1) {
            this.nextBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            this.nextBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    toggleFontSize() {
        // Professional font sizes: 10pt, 11pt, 12pt, 14pt, 16pt
        const sizes = [10, 11, 12, 14, 16];
        const currentIndex = sizes.indexOf(this.fontSize);
        const nextIndex = (currentIndex + 1) % sizes.length;
        this.fontSize = sizes[nextIndex];
        this.applyFontSize();
        
        // Update button text to show current size
        this.fontSizeBtn.textContent = `A${'a'.repeat(Math.floor(this.fontSize / 4))}`;
    }

    applyFontSize() {
        const novelTexts = document.querySelectorAll('.novel-text');
        novelTexts.forEach(text => {
            text.style.fontSize = `${this.fontSize}pt`;
        });
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        
        if (this.isDarkMode) {
            document.body.classList.add('dark-mode');
            this.themeBtn.textContent = '☀️';
        } else {
            document.body.classList.remove('dark-mode');
            this.themeBtn.textContent = '🌙';
        }
    }

    updateProgress() {
        const progress = ((this.currentPage + 1) / this.totalPages) * 100;
        this.progressBar.style.width = `${progress}%`;
    }

    // Bookmark functionality
    saveBookmark() {
        localStorage.setItem('whenHeartsWhisper_bookmark', this.currentPage);
    }

    loadBookmark() {
        const bookmark = localStorage.getItem('whenHeartsWhisper_bookmark');
        if (bookmark !== null) {
            this.showPage(parseInt(bookmark));
        }
    }

    // Auto-save bookmark when page changes
    autoSaveBookmark() {
        this.saveBookmark();
    }
}

// Initialize the e-book reader when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const reader = new EBookReader();
    
    // Load bookmark if available
    reader.loadBookmark();
    
    // Auto-save bookmark when page changes
    const originalShowPage = reader.showPage.bind(reader);
    reader.showPage = function(pageIndex) {
        originalShowPage(pageIndex);
        this.autoSaveBookmark();
    };
    
    // Initial progress update
    reader.updateProgress();
    
    // Handle page unload to end session
    window.addEventListener('beforeunload', () => {
        if (reader.currentSession) {
            reader.endCurrentSession();
        }
    });
});