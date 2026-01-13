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
        this.totalPhases = 8;  // Added perception phase (4.5)
        
        // Data storage
        this.data = {
            sessionId: this.sessionId,
            startTime: new Date().toISOString(),
            demographics: {},
            selfEstimates: {},
            testResponses: [],
            perceptionResponses: [],  // New: perception task data
            testScores: {},
            actualPercentiles: {},
            biasMetrics: {},
            outcomes: {},
            completionTime: null
        };
        
        // Test configuration - loaded asynchronously
        this.testItems = [];
        this.perceptionItems = [];
        this.currentTestItem = 0;
        this.currentPerceptionTrial = 0;
        this.itemsLoaded = false;
        this.perceptionLoaded = false;
        
        // Percentile engine
        this.percentileEngine = new PercentileEngine();
    }
    
    async initialize() {
        // Load test items and perception items from JSON
        await this.loadTestItems();
        await this.loadPerceptionItems();
        
        // Set up handlers after items are loaded
        this.init();
        
        console.log(`✓ Loaded ${this.testItems.length} EI assessment items`);
        console.log(`  Videos: ${[...new Set(this.testItems.map(i => i.videoId))].length}`);
        console.log(`  Domains: ${[...new Set(this.testItems.map(i => i.domain))].join(', ')}`);
        console.log(`✓ Loaded ${this.perceptionItems.length} perception trials`);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    ordinal(n) {
        // Convert number to ordinal string (1st, 2nd, 3rd, 21st, etc.)
        const s = ['th', 'st', 'nd', 'rd'];
        const v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    }
    
    init() {
        this.setupPhaseNavigation();
        this.setupConsentHandlers();
        this.setupDemographicsHandlers();
        this.setupSelfEstimateHandlers();
        this.setupTestHandlers();
        this.setupPerceptionHandlers();
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
            'perception-phase',  // Phase 4.5 (after test, before feedback)
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
        const continueBtn = document.getElementById('consent-continue');
        const declineBtn = document.getElementById('consent-decline');
        
        if (!continueBtn || !declineBtn) {
            console.error('Consent buttons not found!', { continueBtn, declineBtn });
            return;
        }
        
        console.log('Setting up consent handlers...');
        
        continueBtn.addEventListener('click', () => {
            console.log('Consent given!');
            this.data.consentGiven = true;
            this.data.consentTime = new Date().toISOString();
            this.showPhase(2);
        });
        
        declineBtn.addEventListener('click', () => {
            console.log('Consent declined');
            this.data.consentGiven = false;
            this.data.consentTime = new Date().toISOString();
            alert('Thank you for your time. You have chosen not to participate in this study. You may now close this window.');
            // Optionally redirect or show a thank you page
            window.location.href = '/studies/';
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
                status: document.getElementById('status').value,
                ethnicity: document.getElementById('ethnicity').value
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
    
    async loadTestItems() {
        // Load 60-item mixed-format EI assessment (3 videos × 20 items each)
        // 24 tendency items (what you would do) + 36 ability items (what you should do)
        // Maps facets to 4 domains: recognition→understanding, understanding→knowledge, 
        // regulation_self→competence, management_others→management
        
        try {
            const response = await fetch('/static/projects/ei-dk/data/ei60_mixed_format.json', { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`Failed to load item bank: ${response.status} ${response.statusText}`);
            }
            
            const rawItems = await response.json();
            
            // Validate: 60 items (24 tendency + 36 ability)
            if (!Array.isArray(rawItems) || rawItems.length !== 60) {
                throw new Error(`Expected 60 items, got ${rawItems.length}`);
            }
            
            // Transform schema: video_url→videoUrl, sjt_prompt→prompt, text→question, facet→domain
            const domainMap = {
                'recognition': 'understanding',
                'understanding': 'knowledge',
                'regulation_self': 'competence',
                'management_others': 'management'
            };
            
            // Map video IDs to static URLs
            const videoUrlMap = {
                'audio_vid01': '/static/projects/ei-dk/videos/video1.mp4',  // feedback_delivery_lipsync
                'audio_vid02': '/static/projects/ei-dk/videos/video2.mp4',  // stress scenario
                'audio_vid03': '/static/projects/ei-dk/videos/video3.mp4'   // colleague support
            };
            
            this.testItems = rawItems.map(item => {
                return {
                    id: item.id,
                    type: item.type,
                    videoId: item.video_id,
                    videoUrl: videoUrlMap[item.video_id] || item.video_url,
                    prompt: item.sjt_prompt,
                    question: item.text,
                    options: item.options,
                    correctAnswer: item.correctAnswer,
                    domain: domainMap[item.facet] || item.facet,
                    facet: item.facet,
                    difficulty: item.difficulty,
                    theme: item.theme
                };
            });
            
            this.itemsLoaded = true;
            
        } catch (error) {
            console.error('FATAL: Could not load EI assessment items', error);
            alert(`Error loading assessment: ${error.message}\n\nPlease refresh the page or contact support.`);
            throw error;
        }
    }
    
    async loadPerceptionItems() {
        // Load 15 rapid face perception items
        try {
            const response = await fetch('/static/projects/ei-dk/data/perception_items_page.json', { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`Failed to load perception items: ${response.status} ${response.statusText}`);
            }
            
            this.perceptionItems = await response.json();
            
            // Validate
            if (!Array.isArray(this.perceptionItems) || this.perceptionItems.length === 0) {
                throw new Error(`Invalid perception items format`);
            }
            
            this.perceptionLoaded = true;
            console.log(`✓ Loaded ${this.perceptionItems.length} perception items`);
        } catch (error) {
            console.error('Error loading perception items:', error);
            // Non-fatal - can continue without perception task
            this.perceptionLoaded = false;
        }
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
        
        // Show perception phase
        this.showPhase(5);
        this.loadPerceptionTrial(0);
    }
    
    // ========== PHASE 5: PERCEPTION TASK ==========
    
    setupPerceptionHandlers() {
        // No explicit buttons - handled by trial timing and response buttons
        console.log('Perception handlers ready');
    }
    
    loadPerceptionTrial(trialIndex) {
        if (!this.perceptionLoaded || trialIndex >= this.perceptionItems.length) {
            this.completePerceptionTask();
            return;
        }
        
        this.currentPerceptionTrial = trialIndex;
        const trial = this.perceptionItems[trialIndex];
        
        // Update progress
        document.getElementById('perception-current').textContent = trialIndex + 1;
        document.getElementById('perception-total').textContent = this.perceptionItems.length;
        const progress = ((trialIndex + 1) / this.perceptionItems.length) * 100;
        document.getElementById('perception-progress').style.width = `${progress}%`;
        
        // Render trial
        const trialArea = document.getElementById('perception-trial-area');
        
        trialArea.innerHTML = `
            <div class="flex flex-col items-center space-y-6 py-8">
                <!-- Emotion Word -->
                <div class="text-center mb-4">
                    <h3 class="text-4xl font-bold text-gray-900 mb-2">${trial.emotion_label || trial.emotionLabel}</h3>
                    <p class="text-sm text-gray-500">Does this word match the face below?</p>
                </div>
                
                <!-- Face Image -->
                <div class="mb-6">
                    <img src="/static/projects/ei-dk/data/${trial.face_image || trial.faceImage}" 
                         alt="Facial expression" 
                         class="w-64 h-64 object-cover rounded-lg shadow-lg border-4 border-gray-300"
                         id="perception-face">
                </div>
                
                <!-- Timer -->
                <div class="w-full max-w-md">
                    <div class="h-2 bg-gray-200 rounded-full">
                        <div class="h-2 bg-purple-600 rounded-full transition-all duration-100" id="perception-timer" style="width: 100%"></div>
                    </div>
                    <p class="text-xs text-gray-500 text-center mt-1">Time remaining: <span id="perception-time-left">5</span>s</p>
                </div>
                
                <!-- Center Reset Button -->
                <div class="my-6">
                    <button id="perception-center" class="px-6 py-3 bg-gray-300 text-gray-700 rounded-full hover:bg-gray-400 font-medium">
                        Keep Cursor Here
                    </button>
                </div>
                
                <!-- Response Buttons -->
                <div class="flex gap-8">
                    <button id="perception-no" class="px-12 py-4 bg-red-500 text-white rounded-lg hover:bg-red-600 font-bold text-xl disabled:opacity-50" disabled>
                        NO
                    </button>
                    <button id="perception-yes" class="px-12 py-4 bg-green-500 text-white rounded-lg hover:bg-green-600 font-bold text-xl disabled:opacity-50" disabled>
                        YES
                    </button>
                </div>
            </div>
        `;
        
        // Start trial after brief delay
        setTimeout(() => {
            this.startPerceptionTrial(trial);
        }, 1000);
    }
    
    startPerceptionTrial(trial) {
        const stimulusOnset = Date.now();
        let timeLeft = 5;
        
        // Enable response buttons
        document.getElementById('perception-yes').disabled = false;
        document.getElementById('perception-no').disabled = false;
        
        // Countdown timer
        const timerInterval = setInterval(() => {
            timeLeft -= 0.1;
            const percentage = (timeLeft / 5) * 100;
            document.getElementById('perception-timer').style.width = `${percentage}%`;
            document.getElementById('perception-time-left').textContent = Math.ceil(timeLeft);
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                this.recordPerceptionResponse(trial, null, stimulusOnset, true);  // Timeout
            }
        }, 100);
        
        // Response handlers
        const yesBtn = document.getElementById('perception-yes');
        const noBtn = document.getElementById('perception-no');
        
        const handleResponse = (response) => {
            clearInterval(timerInterval);
            this.recordPerceptionResponse(trial, response, stimulusOnset, false);
        };
        
        yesBtn.onclick = () => handleResponse(true);
        noBtn.onclick = () => handleResponse(false);
    }
    
    recordPerceptionResponse(trial, response, stimulusOnset, timeout) {
        const responseTime = Date.now() - stimulusOnset;
        const correct = response === (trial.is_match || trial.isMatch);
        
        // Store trial data
        this.data.perceptionResponses.push({
            trialId: trial.id,
            emotionLabel: trial.emotion_label || trial.emotionLabel,
            response: response,  // true = Yes, false = No, null = timeout
            correct: correct,
            responseTime: responseTime,
            timeout: timeout,
            difficulty: trial.difficulty
        });
        
        // Move to next trial
        setTimeout(() => {
            this.loadPerceptionTrial(this.currentPerceptionTrial + 1);
        }, 500);
    }
    
    completePerceptionTask() {
        console.log('Perception task complete:', this.data.perceptionResponses);
        
        // Transition to feedback
        this.showPhase(6);
        this.displayFeedback();
    }
    
    // ========== PHASE 6: FEEDBACK ==========
    
    setupFeedbackHandlers() {
        document.getElementById('feedback-continue').addEventListener('click', () => {
            this.showPhase(7);
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
        // Summary box: Assessed vs Self-Reported
        const overallActual = this.data.actualPercentiles.overall.point;
        const overallSelf = this.data.selfEstimates.overall;
        const overallBias = this.data.biasMetrics.overall.bias;
        
        document.getElementById('feedback-overall-assessed').textContent = this.ordinal(overallActual);
        document.getElementById('feedback-overall-self').textContent = this.ordinal(overallSelf);
        
        const biasText = overallBias > 0 
            ? `Overestimated by ${overallBias} points`
            : overallBias < 0 
                ? `Underestimated by ${Math.abs(overallBias)} points`
                : 'Perfect calibration!';
        
        const biasColor = Math.abs(overallBias) <= 10 ? 'text-green-600' : 
                         Math.abs(overallBias) <= 20 ? 'text-yellow-600' : 'text-red-600';
        
        const biasElement = document.getElementById('feedback-overall-bias');
        biasElement.textContent = biasText;
        biasElement.className = `text-xl font-bold ${biasColor}`;
        
        // Calibration message
        document.getElementById('feedback-calibration-message').textContent = this.getCalibrationMessage(overallBias);
        
        // Interpretation text
        document.getElementById('feedback-interpretation-text').textContent = this.getInterpretationText(overallActual, overallSelf, overallBias);
        
        // Render charts
        this.renderRadarCharts();
        this.renderBiasChart();
    }
    
    renderRadarCharts() {
        const domains = ['Overall', 'Understanding', 'Knowledge', 'Competence', 'Management'];
        const domainKeys = ['overall', 'understanding', 'knowledge', 'competence', 'management'];
        
        // Extract data
        const selfData = domainKeys.map(key => this.data.selfEstimates[key]);
        const actualData = domainKeys.map(key => this.data.actualPercentiles[key].point);
        
        // Self-Reported Radar (Blue)
        const selfRadar = new Chart(document.getElementById('self-radar'), {
            type: 'radar',
            data: {
                labels: domains,
                datasets: [{
                    label: 'Self-Reported Percentile',
                    data: selfData,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgb(59, 130, 246)',
                    pointBackgroundColor: 'rgb(59, 130, 246)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2
                }]
            },
            options: {
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 25
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.r + 'th percentile';
                            }
                        }
                    }
                }
            }
        });
        
        // Assessed Radar (Green)
        const actualRadar = new Chart(document.getElementById('actual-radar'), {
            type: 'radar',
            data: {
                labels: domains,
                datasets: [{
                    label: 'Assessed Percentile',
                    data: actualData,
                    backgroundColor: 'rgba(34, 197, 94, 0.2)',
                    borderColor: 'rgb(34, 197, 94)',
                    pointBackgroundColor: 'rgb(34, 197, 94)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(34, 197, 94)',
                    borderWidth: 2
                }]
            },
            options: {
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 25
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.r + 'th percentile';
                            }
                        }
                    }
                }
            }
        });
    }
    
    renderBiasChart() {
        const domains = ['Overall', 'Understanding', 'Knowledge', 'Competence', 'Management'];
        const domainKeys = ['overall', 'understanding', 'knowledge', 'competence', 'management'];
        
        const biasData = domainKeys.map(key => this.data.biasMetrics[key].bias);
        
        // Color based on bias magnitude
        const colors = biasData.map(bias => {
            const abs = Math.abs(bias);
            if (abs <= 10) return 'rgba(34, 197, 94, 0.8)';  // green
            if (abs <= 20) return 'rgba(234, 179, 8, 0.8)';  // yellow
            return 'rgba(239, 68, 68, 0.8)';  // red
        });
        
        new Chart(document.getElementById('bias-chart'), {
            type: 'bar',
            data: {
                labels: domains,
                datasets: [{
                    label: 'Bias (Self - Actual)',
                    data: biasData,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                scales: {
                    x: {
                        min: -50,
                        max: 50,
                        ticks: {
                            callback: function(value) {
                                return value > 0 ? '+' + value : value;
                            }
                        },
                        grid: {
                            color: function(context) {
                                if (context.tick.value === 0) {
                                    return '#000';
                                }
                                return 'rgba(0, 0, 0, 0.1)';
                            },
                            lineWidth: function(context) {
                                if (context.tick.value === 0) {
                                    return 2;
                                }
                                return 1;
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const bias = context.parsed.x;
                                if (bias > 0) {
                                    return 'Overestimated by ' + bias + ' points';
                                } else if (bias < 0) {
                                    return 'Underestimated by ' + Math.abs(bias) + ' points';
                                }
                                return 'Perfect calibration';
                            }
                        }
                    }
                }
            }
        });
    }
    
    getCalibrationMessage(bias) {
        const absBias = Math.abs(bias);
        if (absBias <= 10) {
            return '✓ Well-calibrated: Your self-assessment closely matches your performance. This suggests good self-awareness—a key component of emotional intelligence.';
        } else if (absBias <= 20) {
            return '⚠ Moderate difference: There is some difference between your self-perception and assessed performance. This is common and provides opportunities to enhance self-awareness.';
        } else if (bias > 20) {
            return '⚠ Overestimation: You rated your EI abilities higher than your test performance suggests. This pattern is common and indicates opportunities to develop both your EI skills and self-awareness.';
        } else {
            return '⚠ Underestimation: You rated your EI abilities lower than your test performance suggests. You may be more skilled than you give yourself credit for—consider recognizing your strengths.';
        }
    }
    
    getInterpretationText(actual, self, bias) {
        let text = `Your assessed emotional intelligence is at the ${this.ordinal(actual)} percentile, `;
        text += `while you estimated yourself at the ${this.ordinal(self)} percentile. `;
        
        const absBias = Math.abs(bias);
        
        if (absBias <= 10) {
            text += 'Your self-assessment is well-calibrated with your performance, suggesting strong metacognitive awareness. ';
            if (actual >= 70) {
                text += 'You demonstrate advanced EI abilities and accurate self-perception.';
            } else if (actual >= 40) {
                text += 'You show solid EI abilities with room for growth. Your accurate self-awareness is a strength you can leverage for development.';
            } else {
                text += 'While your EI skills are developing, your accurate self-awareness provides a strong foundation for improvement.';
            }
        } else if (bias > 10) {
            text += 'This difference between self-perception and performance is common. ';
            text += 'The good news: both emotional intelligence skills and metacognitive awareness can be developed through practice, feedback, and training. ';
            text += 'Building your EI abilities while also enhancing self-awareness is a powerful path for growth.';
        } else {
            text += 'You underestimated your abilities. This suggests you may be more capable than you recognize. ';
            text += 'Consider acknowledging your current strengths while continuing to develop your emotional intelligence.';
        }
        
        return text;
    }
    
    
    // ========== PHASE 7: OUTCOMES ==========
    
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
        
        // Submit to SONA API
        (async () => {
            try {
                const res = await fetch(`/api/studies/${STUDY_ID}/submit/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.data)
                });
                const out = await res.json();
                console.log('✓ SONA submission successful:', out);
            } catch (e) { 
                console.error('✗ SONA submit error:', e);
                // Continue anyway - data saved to localStorage as backup
            }
        })();
        
        // Save to localStorage (for demo - replace with server submission)
        this.saveToLocalStorage();
        
        // Log to console (for testing)
        console.log('Study data collected:', this.data);
        
        // Show debrief
        this.showPhase(8);
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

document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('Initializing Sheldon Replication Study...');
        study = new SheldonReplicationStudy();
        
        // Load items asynchronously
        await study.initialize();
        
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


