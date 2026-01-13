// emotional-intelligence-assessment/sheldon_replication.js
// Sheldon et al. (2014) replication study controller
// Manages consent → demographics → self-estimates → EI test → feedback → outcomes flow
// RELEVANT FILES: sheldon_replication.html, pilot_test/mini_feedback_engine.js, pilot_test/percentile_scorer.py

class SheldonReplicationStudy {
    constructor() {
        // Session data
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        
        // Study phases
        this.currentPhase = 1;
        this.totalPhases = 7;
        
        // Data storage
        this.data = {
            sessionId: this.sessionId,
            startTime: new Date().toISOString(),
            demographics: {},
            selfEstimates: {},
            testResponses: [],
            testScores: {},
            actualPercentiles: {},
            biasMetrics: {},
            outcomes: {},
            completionTime: null
        };
        
        // Test configuration (placeholder - replace with actual items)
        this.testItems = this.loadTestItems();
        this.currentTestItem = 0;
        
        // Percentile engine
        this.percentileEngine = new PercentileEngine();
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        this.setupPhaseNavigation();
        this.setupConsentHandlers();
        this.setupDemographicsHandlers();
        this.setupSelfEstimateHandlers();
        this.setupTestHandlers();
        this.setupFeedbackHandlers();
        this.setupOutcomesHandlers();
        
        // Load any saved session (for testing)
        this.loadSession();
    }
    
    // ========== PHASE NAVIGATION ==========
    
    setupPhaseNavigation() {
        // Update phase indicator and progress bar
        this.updatePhaseIndicator();
    }
    
    updatePhaseIndicator() {
        document.getElementById('phase-indicator').textContent = 
            `Step ${this.currentPhase} of ${this.totalPhases}`;
        
        const progress = (this.currentPhase / this.totalPhases) * 100;
        document.getElementById('main-progress').style.width = `${progress}%`;
    }
    
    showPhase(phaseNumber) {
        // Hide all phases
        const phases = [
            'consent-phase',
            'demographics-phase',
            'self-estimate-phase',
            'test-phase',
            'feedback-phase',
            'outcomes-phase',
            'debrief-phase'
        ];
        
        phases.forEach(phase => {
            document.getElementById(phase).classList.add('hidden');
        });
        
        // Show target phase
        document.getElementById(phases[phaseNumber - 1]).classList.remove('hidden');
        
        this.currentPhase = phaseNumber;
        this.updatePhaseIndicator();
        
        // Scroll to top
        window.scrollTo(0, 0);
        
        // Save progress
        this.saveSession();
    }
    
    // ========== PHASE 1: CONSENT ==========
    
    setupConsentHandlers() {
        const checkbox = document.getElementById('consent-checkbox');
        const continueBtn = document.getElementById('consent-continue');
        
        if (!checkbox || !continueBtn) {
            console.error('Consent elements not found!', { checkbox, continueBtn });
            return;
        }
        
        console.log('Setting up consent handlers...', { checkbox, continueBtn });
        
        checkbox.addEventListener('change', () => {
            console.log('Checkbox changed:', checkbox.checked);
            continueBtn.disabled = !checkbox.checked;
        });
        
        continueBtn.addEventListener('click', () => {
            console.log('Continue button clicked!');
            this.data.consentGiven = true;
            this.data.consentTime = new Date().toISOString();
            this.showPhase(2);
        });
    }
    
    // ========== PHASE 2: DEMOGRAPHICS ==========
    
    setupDemographicsHandlers() {
        document.getElementById('demographics-back').addEventListener('click', () => {
            this.showPhase(1);
        });
        
        document.getElementById('demographics-continue').addEventListener('click', () => {
            this.data.demographics = {
                ageRange: document.getElementById('age-range').value,
                gender: document.getElementById('gender').value,
                status: document.getElementById('status').value
            };
            this.showPhase(3);
        });
    }
    
    // ========== PHASE 3: SELF-ESTIMATES ==========
    
    setupSelfEstimateHandlers() {
        // Setup sliders with real-time updates
        const sliders = [
            { id: 'overall', label: 'overall-value' },
            { id: 'understanding', label: 'understanding-value' },
            { id: 'management', label: 'management-value' },
            { id: 'knowledge', label: 'knowledge-value' },
            { id: 'competence', label: 'competence-value' }
        ];
        
        sliders.forEach(slider => {
            const input = document.getElementById(`self-estimate-${slider.id}`);
            const label = document.getElementById(`${slider.label}`);
            
            input.addEventListener('input', (e) => {
                const value = e.target.value;
                label.textContent = `${value}th`;
            });
        });
        
        document.getElementById('self-estimate-back').addEventListener('click', () => {
            this.showPhase(2);
        });
        
        document.getElementById('self-estimate-continue').addEventListener('click', () => {
            // Collect self-estimates
            this.data.selfEstimates = {
                overall: parseInt(document.getElementById('self-estimate-overall').value),
                understanding: parseInt(document.getElementById('self-estimate-understanding').value),
                management: parseInt(document.getElementById('self-estimate-management').value),
                knowledge: parseInt(document.getElementById('self-estimate-knowledge').value),
                competence: parseInt(document.getElementById('self-estimate-competence').value),
                timestamp: new Date().toISOString()
            };
            
            this.showPhase(4);
            this.loadTestQuestion(0);
        });
    }
    
    // ========== PHASE 4: EI TEST ==========
    
    setupTestHandlers() {
        document.getElementById('test-back').addEventListener('click', () => {
            if (this.currentTestItem > 0) {
                this.loadTestQuestion(this.currentTestItem - 1);
            }
        });
        
        document.getElementById('test-continue').addEventListener('click', () => {
            if (this.currentTestItem < this.testItems.length - 1) {
                this.loadTestQuestion(this.currentTestItem + 1);
            } else {
                this.completeTest();
            }
        });
    }
    
    loadTestItems() {
        // Using mini EI assessment items (12 items from mini_item_bank.json)
        // 3 videos × 4 facets = 12 items total
        // Maps to 4 domains: understanding, management, knowledge, competence
        
        const items = [
            // Video 1: Feedback Delivery (4 items)
            {
                id: 'mini_vid01_recognition',
                domain: 'understanding',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/6dcccd56-43f2-4b8c-abcb-d4195213a275.mp4',
                prompt: 'You are observing an interaction between a manager and team member. The manager is delivering constructive feedback about a recent project. Watch carefully and pay attention to the emotional cues displayed by both people.',
                question: 'What emotion is the manager primarily displaying toward the team member?',
                options: [
                    'Concern combined with supportive intent',
                    'Anger or frustration about performance',
                    'Disappointment and judgment',
                    'Indifference or detachment'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid01_understanding',
                domain: 'knowledge',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/6dcccd56-43f2-4b8c-abcb-d4195213a275.mp4',
                prompt: 'You are observing an interaction between a manager and team member. The manager is delivering constructive feedback about a recent project. Watch carefully and pay attention to the emotional cues displayed by both people.',
                question: 'Why might the team member be experiencing uncertainty or slight concern during this interaction?',
                options: [
                    'Feedback creates ambiguity about their standing and requires self-evaluation',
                    'They are naturally anxious in all workplace interactions',
                    'They do not care about their job performance',
                    'The manager is being unclear in their communication'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid01_regulation_self',
                domain: 'competence',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/6dcccd56-43f2-4b8c-abcb-d4195213a275.mp4',
                prompt: 'You are observing an interaction between a manager and team member. The manager is delivering constructive feedback about a recent project. Watch carefully and pay attention to the emotional cues displayed by both people.',
                question: 'What would be the most effective emotional regulation approach for the team member receiving this feedback?',
                options: [
                    'Listen actively, pause before responding, and ask clarifying questions',
                    'Immediately defend their work and explain what went wrong',
                    'Agree with everything quickly to end the conversation',
                    'Suppress feelings and show no emotional reaction'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid01_management_others',
                domain: 'management',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/6dcccd56-43f2-4b8c-abcb-d4195213a275.mp4',
                prompt: 'You are observing an interaction between a manager and team member. The manager is delivering constructive feedback about a recent project. Watch carefully and pay attention to the emotional cues displayed by both people.',
                question: 'What supportive communication strategy is the manager using most effectively?',
                options: [
                    'Reflective listening with empathetic body language and direct eye contact',
                    'Quick delivery to minimize discomfort',
                    'Vague statements to soften the message',
                    'Focusing only on problems without acknowledging effort'
                ],
                correctAnswer: 0
            },
            
            // Video 2: Deadline Stress (4 items)
            {
                id: 'mini_vid02_recognition',
                domain: 'understanding',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/5e5c54eb-6b7c-4444-b0f2-f90ab7fd3314.mp4',
                prompt: 'You are observing a workplace interaction where one professional approaches a colleague about an urgent task. The colleague at the desk appears to be under significant pressure. Watch for both people's emotional states and how they adapt to each other.',
                question: 'What emotional state is the person at the desk experiencing?',
                options: [
                    'Stress and feeling overwhelmed by time pressure',
                    'Anger at being interrupted',
                    'Boredom with routine tasks',
                    'Excitement about their work'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid02_understanding',
                domain: 'knowledge',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/5e5c54eb-6b7c-4444-b0f2-f90ab7fd3314.mp4',
                prompt: 'You are observing a workplace interaction where one professional approaches a colleague about an urgent task. The colleague at the desk appears to be under significant pressure. Watch for both people's emotional states and how they adapt to each other.',
                question: 'According to emotion research, why does stress affect how people can receive and process information?',
                options: [
                    'Stress narrows cognitive focus and reduces capacity for processing complex information',
                    'Stress makes people more attentive to details',
                    'Stress does not affect communication or cognition',
                    'Stress only affects physical performance, not mental abilities'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid02_regulation_self',
                domain: 'competence',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/5e5c54eb-6b7c-4444-b0f2-f90ab7fd3314.mp4',
                prompt: 'You are observing a workplace interaction where one professional approaches a colleague about an urgent task. The colleague at the desk appears to be under significant pressure. Watch for both people's emotional states and how they adapt to each other.',
                question: 'What skill is the approaching colleague demonstrating in how they manage their own behavior?',
                options: [
                    'Emotional flexibility by adjusting their pace and energy to match situational needs',
                    'Ignoring the situation and proceeding as normal',
                    'Matching the stressed colleague's high energy level',
                    'Becoming frustrated with the colleague's state'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid02_management_others',
                domain: 'management',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/5e5c54eb-6b7c-4444-b0f2-f90ab7fd3314.mp4',
                prompt: 'You are observing a workplace interaction where one professional approaches a colleague about an urgent task. The colleague at the desk appears to be under significant pressure. Watch for both people's emotional states and how they adapt to each other.',
                question: 'What is the most effective strategy being used to support the stressed colleague?',
                options: [
                    'Problem-focused communication adjusted to their reduced cognitive capacity',
                    'Providing extensive detailed information to help them',
                    'Pointing out that stress is negatively affecting their performance',
                    'Leaving them alone until they calm down'
                ],
                correctAnswer: 0
            },
            
            // Video 3: Colleague Support (4 items)
            {
                id: 'mini_vid03_recognition',
                domain: 'understanding',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/c0e7f5b6-2b1c-4c5d-9f3e-8a4d7e6c5b4a.mp4',
                prompt: 'You are observing a supportive conversation between two colleagues in a quiet area of the office. One colleague is sharing something difficult while the other listens. Pay attention to the emotional dynamic between them and how they communicate nonverbally.',
                question: 'What emotions are most clearly present in this interaction?',
                options: [
                    'Vulnerability (speaker) and empathy (listener)',
                    'Anger (speaker) and fear (listener)',
                    'Indifference from both parties',
                    'Excitement (speaker) and confusion (listener)'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid03_understanding',
                domain: 'knowledge',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/c0e7f5b6-2b1c-4c5d-9f3e-8a4d7e6c5b4a.mp4',
                prompt: 'You are observing a supportive conversation between two colleagues in a quiet area of the office. One colleague is sharing something difficult while the other listens. Pay attention to the emotional dynamic between them and how they communicate nonverbally.',
                question: 'Why is empathy particularly important in this type of disclosure scenario?',
                options: [
                    'It creates psychological safety that enables trust and honest communication',
                    'It is simply good manners in professional settings',
                    'It helps avoid confrontation about work issues',
                    'It allows the listener to end the conversation quickly'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid03_regulation_self',
                domain: 'competence',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/c0e7f5b6-2b1c-4c5d-9f3e-8a4d7e6c5b4a.mp4',
                prompt: 'You are observing a supportive conversation between two colleagues in a quiet area of the office. One colleague is sharing something difficult while the other listens. Pay attention to the emotional dynamic between them and how they communicate nonverbally.',
                question: 'What advanced emotional competence is the listener demonstrating?',
                options: [
                    'Managing their own potential discomfort to remain present and supportive',
                    'Suppressing all emotion to appear professional',
                    'Becoming overly emotional themselves about the disclosure',
                    'Detaching completely to avoid personal involvement'
                ],
                correctAnswer: 0
            },
            {
                id: 'mini_vid03_management_others',
                domain: 'management',
                type: 'video',
                videoUrl: 'https://dnznrvs05pmza.cloudfront.net/c0e7f5b6-2b1c-4c5d-9f3e-8a4d7e6c5b4a.mp4',
                prompt: 'You are observing a supportive conversation between two colleagues in a quiet area of the office. One colleague is sharing something difficult while the other listens. Pay attention to the emotional dynamic between them and how they communicate nonverbally.',
                question: 'What supportive communication technique is the listener using most effectively?',
                options: [
                    'Active listening with validating nonverbal cues',
                    'Immediately offering solutions and advice',
                    'Changing the subject to lighten the mood',
                    'Minimizing the concern to reduce worry'
                ],
                correctAnswer: 0
            }
        ];
        
        return items;
    }
    
    loadTestQuestion(index) {
        this.currentTestItem = index;
        const item = this.testItems[index];
        
        // Update progress
        document.getElementById('test-current').textContent = index + 1;
        document.getElementById('test-total').textContent = this.testItems.length;
        const progress = ((index + 1) / this.testItems.length) * 100;
        document.getElementById('test-progress').style.width = `${progress}%`;
        
        // Render question with video if present
        const questionArea = document.getElementById('test-question-area');
        
        const videoHtml = item.type === 'video' ? `
            <div class="mb-6">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <p class="text-sm text-blue-900">${item.prompt}</p>
                </div>
                <video 
                    class="w-full rounded-lg shadow-lg mb-4" 
                    controls 
                    id="current-video"
                    style="max-height: 400px;">
                    <source src="${item.videoUrl}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        ` : '';
        
        questionArea.innerHTML = `
            ${videoHtml}
            <div class="mb-6">
                <div class="flex items-center space-x-2 mb-3">
                    <span class="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                        ${item.domain}
                    </span>
                </div>
                <p class="text-lg font-medium text-gray-900">${item.question}</p>
            </div>
            
            <div class="space-y-3">
                ${item.options.map((option, i) => `
                    <div class="option-card border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer" 
                         data-option="${i}">
                        <div class="flex items-center">
                            <div class="w-5 h-5 border-2 border-gray-300 rounded-full mr-3 flex items-center justify-center">
                                <div class="w-3 h-3 bg-blue-500 rounded-full hidden option-radio"></div>
                            </div>
                            <span class="text-gray-900">${option}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add click handlers to options
        const options = questionArea.querySelectorAll('.option-card');
        options.forEach((option, i) => {
            option.addEventListener('click', () => {
                this.selectTestOption(option, i);
            });
        });
        
        // Restore previous answer if exists
        if (this.data.testResponses[index] !== undefined) {
            this.selectTestOption(options[this.data.testResponses[index]], this.data.testResponses[index]);
        } else {
            document.getElementById('test-continue').disabled = true;
        }
        
        // Update button text
        const continueBtn = document.getElementById('test-continue');
        if (index === this.testItems.length - 1) {
            continueBtn.textContent = 'Complete Test →';
        } else {
            continueBtn.textContent = 'Next →';
        }
    }
    
    selectTestOption(optionElement, optionIndex) {
        // Clear previous selection
        const options = document.querySelectorAll('.option-card');
        options.forEach(opt => {
            opt.classList.remove('border-blue-500', 'bg-blue-50');
            opt.querySelector('.option-radio').classList.add('hidden');
        });
        
        // Select new option
        optionElement.classList.add('border-blue-500', 'bg-blue-50');
        optionElement.querySelector('.option-radio').classList.remove('hidden');
        
        // Store response
        this.data.testResponses[this.currentTestItem] = optionIndex;
        
        // Enable continue
        document.getElementById('test-continue').disabled = false;
    }
    
    completeTest() {
        // Calculate scores by domain
        const scores = {
            understanding: { correct: 0, total: 0 },
            management: { correct: 0, total: 0 },
            knowledge: { correct: 0, total: 0 },
            competence: { correct: 0, total: 0 }
        };
        
        this.testItems.forEach((item, index) => {
            const domain = item.domain;
            scores[domain].total++;
            
            if (this.data.testResponses[index] === item.correctAnswer) {
                scores[domain].correct++;
            }
        });
        
        // Calculate overall
        const totalCorrect = Object.values(scores).reduce((sum, d) => sum + d.correct, 0);
        const totalItems = Object.values(scores).reduce((sum, d) => sum + d.total, 0);
        
        scores.overall = {
            correct: totalCorrect,
            total: totalItems
        };
        
        this.data.testScores = scores;
        
        // Calculate percentiles
        this.calculatePercentiles();
        
        // Calculate bias metrics
        this.calculateBiasMetrics();
        
        // Show feedback
        this.showPhase(5);
        this.displayFeedback();
    }
    
    // ========== PHASE 5: FEEDBACK ==========
    
    setupFeedbackHandlers() {
        document.getElementById('feedback-continue').addEventListener('click', () => {
            this.showPhase(6);
        });
    }
    
    calculatePercentiles() {
        // Calculate percentiles for overall and each domain
        const domains = ['overall', 'understanding', 'management', 'knowledge', 'competence'];
        
        domains.forEach(domain => {
            const score = this.data.testScores[domain];
            const percentile = this.percentileEngine.estimatePercentile(score.correct, score.total);
            this.data.actualPercentiles[domain] = percentile;
        });
    }
    
    calculateBiasMetrics() {
        // Calculate bias metrics for DK analysis
        // bias = self_estimate - actual_percentile
        // abs_error = |bias|
        
        const domains = ['overall', 'understanding', 'management', 'knowledge', 'competence'];
        
        domains.forEach(domain => {
            const selfEstimate = this.data.selfEstimates[domain];
            const actualPercentile = this.data.actualPercentiles[domain].point;
            const bias = selfEstimate - actualPercentile;
            
            this.data.biasMetrics[domain] = {
                self_estimate: selfEstimate,
                actual_percentile: actualPercentile,
                bias: bias,
                absolute_error: Math.abs(bias),
                overestimation: bias > 0,
                underestimation: bias < 0
            };
        });
    }
    
    displayFeedback() {
        // Display overall feedback
        const overall = this.data.actualPercentiles.overall;
        document.getElementById('feedback-overall-percentile').textContent = overall.point;
        document.getElementById('feedback-overall-ci').textContent = 
            `${overall.lower} - ${overall.upper}`;
        
        const level = this.getPerformanceLevel(overall.point);
        document.getElementById('feedback-overall-interpretation').textContent = 
            this.getOverallInterpretation(level, overall.point);
        
        // Display domain feedback
        const domains = ['understanding', 'management', 'knowledge', 'competence'];
        domains.forEach(domain => {
            const percentile = this.data.actualPercentiles[domain];
            document.getElementById(`feedback-${domain}-percentile`).textContent = percentile.point;
            document.getElementById(`feedback-${domain}-ci`).textContent = 
                `${percentile.lower} - ${percentile.upper}`;
        });
    }
    
    getPerformanceLevel(percentile) {
        if (percentile <= 40) return 'Developing';
        if (percentile <= 70) return 'Proficient';
        return 'Advanced';
    }
    
    getOverallInterpretation(level, percentile) {
        if (level === 'Advanced') {
            return `Excellent work! You scored at the ${percentile}th percentile, demonstrating strong emotional intelligence. This means you performed better than approximately ${percentile}% of people in the general population.`;
        } else if (level === 'Proficient') {
            return `Good performance! You scored at the ${percentile}th percentile, showing solid emotional intelligence skills. You're performing at or above the population average with room for continued growth.`;
        } else {
            return `You scored at the ${percentile}th percentile. This assessment reveals opportunities to develop your emotional intelligence skills. With focused practice and training, these abilities can improve significantly.`;
        }
    }
    
    // ========== PHASE 6: OUTCOMES ==========
    
    setupOutcomesHandlers() {
        // Handle Likert option selection
        const likertOptions = document.querySelectorAll('.likert-option');
        likertOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectLikertOption(option);
            });
        });
        
        document.getElementById('outcomes-back').addEventListener('click', () => {
            this.showPhase(5);
        });
        
        document.getElementById('outcomes-continue').addEventListener('click', () => {
            this.submitData();
        });
    }
    
    selectLikertOption(optionElement) {
        const question = optionElement.getAttribute('data-question');
        const value = parseInt(optionElement.getAttribute('data-value'));
        
        // Clear previous selection for this question
        const questionOptions = document.querySelectorAll(`[data-question="${question}"]`);
        questionOptions.forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Select new option
        optionElement.classList.add('selected');
        
        // Store response
        this.data.outcomes[question] = value;
        
        // Check if all questions answered
        const requiredQuestions = ['interest', 'likelihood', 'wtp'];
        const allAnswered = requiredQuestions.every(q => this.data.outcomes[q] !== undefined);
        
        document.getElementById('outcomes-continue').disabled = !allAnswered;
    }
    
    submitData() {
        // Finalize data
        this.data.completionTime = new Date().toISOString();
        this.data.durationSeconds = Math.floor((Date.now() - this.startTime) / 1000);
        
        // Save to localStorage (for demo - replace with server submission)
        this.saveToLocalStorage();
        
        // Log to console (for testing)
        console.log('Study data collected:', this.data);
        
        // Show debrief
        this.showPhase(7);
    }
    
    // ========== DATA STORAGE ==========
    
    saveSession() {
        localStorage.setItem('sheldon_session', JSON.stringify(this.data));
    }
    
    loadSession() {
        const saved = localStorage.getItem('sheldon_session');
        if (saved) {
            // For development - could restore progress
            // this.data = JSON.parse(saved);
        }
    }
    
    saveToLocalStorage() {
        // Save complete data
        const allData = JSON.parse(localStorage.getItem('sheldon_all_data') || '[]');
        allData.push(this.data);
        localStorage.setItem('sheldon_all_data', JSON.stringify(allData));
        
        // Clear session
        localStorage.removeItem('sheldon_session');
        
        console.log(`Saved data for session ${this.sessionId}`);
        console.log(`Total sessions collected: ${allData.length}`);
    }
    
    // ========== UTILITY ==========
    
    exportData() {
        // Export all collected data as JSON
        const allData = JSON.parse(localStorage.getItem('sheldon_all_data') || '[]');
        const dataStr = JSON.stringify(allData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sheldon_replication_data_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// ========== PERCENTILE ENGINE ==========

class PercentileEngine {
    constructor() {
        // Population assumptions (general population norms)
        this.populationMean = 0.60;  // 60% average accuracy
        this.populationSD = 0.15;    // 15% standard deviation
        
        // Convert to Beta distribution parameters
        this.betaParams = this.calculateBetaParams(this.populationMean, this.populationSD);
    }
    
    calculateBetaParams(mean, sd) {
        const variance = sd * sd;
        const alpha = mean * ((mean * (1 - mean) / variance) - 1);
        const beta = (1 - mean) * ((mean * (1 - mean) / variance) - 1);
        return { alpha, beta };
    }
    
    estimatePercentile(correct, total) {
        if (total === 0) return { point: 50, lower: 25, upper: 75 };
        
        const proportion = correct / total;
        
        // Posterior Beta parameters (Bayesian update)
        const posteriorAlpha = this.betaParams.alpha + correct;
        const posteriorBeta = this.betaParams.beta + (total - correct);
        
        // Estimate percentile using normal approximation
        const posteriorMean = posteriorAlpha / (posteriorAlpha + posteriorBeta);
        const posteriorVar = (posteriorAlpha * posteriorBeta) / 
            (Math.pow(posteriorAlpha + posteriorBeta, 2) * (posteriorAlpha + posteriorBeta + 1));
        const posteriorSD = Math.sqrt(posteriorVar);
        
        // Z-score relative to population
        const zScore = (posteriorMean - this.populationMean) / this.populationSD;
        
        // Convert to percentile
        const percentile = this.normalCDF(zScore) * 100;
        
        // 80% confidence interval (±1.28 SD)
        const lowerZ = (posteriorMean - 1.28 * posteriorSD - this.populationMean) / this.populationSD;
        const upperZ = (posteriorMean + 1.28 * posteriorSD - this.populationMean) / this.populationSD;
        
        return {
            point: Math.max(1, Math.min(99, Math.round(percentile))),
            lower: Math.max(1, Math.min(99, Math.round(this.normalCDF(lowerZ) * 100))),
            upper: Math.max(1, Math.min(99, Math.round(this.normalCDF(upperZ) * 100)))
        };
    }
    
    normalCDF(z) {
        // Approximation of standard normal CDF
        const t = 1 / (1 + 0.2316419 * Math.abs(z));
        const d = 0.3989423 * Math.exp(-z * z / 2);
        const prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
        return z > 0 ? 1 - prob : prob;
    }
}

// ========== INITIALIZE ==========

let study;

document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('Initializing Sheldon Replication Study...');
        study = new SheldonReplicationStudy();
        console.log('Study initialized successfully!', study);
        
        // Add global export function for testing
        window.exportStudyData = () => {
            study.exportData();
        };
    } catch (error) {
        console.error('Failed to initialize study:', error);
        alert('Error initializing study. Please check the console for details.');
    }
});


