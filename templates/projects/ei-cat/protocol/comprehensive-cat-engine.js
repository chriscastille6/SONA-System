/**
 * Comprehensive Computer Adaptive Testing Engine for Emotional Intelligence Assessment
 * 
 * This file implements a multi-domain CAT system using all 289 GPT-generated items
 * from the research study across 5 EI domains with item culling capabilities.
 * 
 * RELEVANT FILES: comprehensive-cat-assessment.html, comprehensive-item-bank.json, validation-analysis.js
 */

class ComprehensiveCATEngine {
    constructor() {
        // CAT Configuration
        this.maxItems = 25;
        this.minItems = 8;
        this.terminationThreshold = 0.25; // Standard error threshold
        this.initialAbility = 0.0;
        this.abilityEstimate = this.initialAbility;
        this.standardError = 1.0;
        
        // Multi-domain configuration
        this.domains = ['steu', 'stem', 'gemok', 'gecoem', 'gecoer'];
        this.domainWeights = {
            'steu': 0.2,      // Understanding
            'stem': 0.2,      // Management  
            'gemok': 0.2,     // Knowledge
            'gecoem': 0.2,    // Emotion Management
            'gecoer': 0.2     // Emotion Regulation
        };
        
        // Item bank (will be loaded from JSON)
        this.itemBank = [];
        this.filteredItemBank = [];
        
        // Assessment state
        this.responses = [];
        this.usedItems = new Set();
        this.domainScores = {};
        this.domainItemCounts = {};
        
        // IRT parameters
        this.maxIterations = 20;
        this.convergenceThreshold = 0.001;
        
        // Item culling parameters
        this.cullingEnabled = true;
        this.minDiscrimination = 0.5;
        this.maxDifficulty = 3.0;
        this.minResponses = 50;
        
        // Initialize domain scores
        for (const domain of this.domains) {
            this.domainScores[domain] = 0;
            this.domainItemCounts[domain] = 0;
        }
    }

    async loadItemBank() {
        try {
            const response = await fetch('comprehensive-item-bank.json');
            this.itemBank = await response.json();
            this.filterItems();
            console.log(`Loaded ${this.itemBank.length} items, ${this.filteredItemBank.length} after filtering`);
        } catch (error) {
            console.error('Error loading item bank:', error);
            // Fallback to basic items
            this.itemBank = this.getBasicItemBank();
            this.filteredItemBank = this.itemBank;
        }
    }

    filterItems() {
        if (!this.cullingEnabled) {
            this.filteredItemBank = [...this.itemBank];
            return;
        }

        this.filteredItemBank = this.itemBank.filter(item => {
            // Filter by discrimination
            if (item.discrimination < this.minDiscrimination) return false;
            
            // Filter by difficulty range
            if (Math.abs(item.difficulty) > this.maxDifficulty) return false;
            
            // Filter by response count
            if (item.total_responses < this.minResponses) return false;
            
            return true;
        });

        console.log(`Item culling: ${this.itemBank.length} → ${this.filteredItemBank.length} items`);
    }

    getBasicItemBank() {
        // Fallback item bank if JSON loading fails
        return [
            {
                id: 'fallback_1',
                domain: 'steu',
                text: 'Sample emotional understanding scenario',
                options: ['Option A', 'Option B', 'Option C', 'Option D'],
                correctAnswer: 0,
                difficulty: 0.0,
                discrimination: 1.0,
                human_performance: 0.5
            }
        ];
    }

    reset() {
        this.abilityEstimate = this.initialAbility;
        this.standardError = 1.0;
        this.responses = [];
        this.usedItems.clear();
        
        for (const domain of this.domains) {
            this.domainScores[domain] = 0;
            this.domainItemCounts[domain] = 0;
        }
    }

    selectNextItem() {
        if (this.responses.length >= this.maxItems) {
            return null;
        }

        // Filter out used items
        const availableItems = this.filteredItemBank.filter(item => !this.usedItems.has(item.id));
        
        if (availableItems.length === 0) {
            return null;
        }

        // Balance domain representation
        const domainBalance = this.calculateDomainBalance();
        const balancedItems = this.balanceDomainSelection(availableItems, domainBalance);

        // Select item with maximum information at current ability estimate
        let bestItem = null;
        let maxInformation = -1;

        for (const item of balancedItems) {
            const information = this.calculateItemInformation(item, this.abilityEstimate);
            if (information > maxInformation) {
                maxInformation = information;
                bestItem = item;
            }
        }

        return bestItem;
    }

    calculateDomainBalance() {
        const balance = {};
        const totalItems = this.responses.length;
        
        for (const domain of this.domains) {
            const currentCount = this.domainItemCounts[domain];
            const targetCount = Math.ceil(totalItems * this.domainWeights[domain]);
            balance[domain] = targetCount - currentCount;
        }
        
        return balance;
    }

    balanceDomainSelection(availableItems, domainBalance) {
        // Prioritize items from underrepresented domains
        const prioritizedItems = [];
        
        for (const domain of this.domains) {
            if (domainBalance[domain] > 0) {
                const domainItems = availableItems.filter(item => item.domain === domain);
                prioritizedItems.push(...domainItems);
            }
        }
        
        // If no domain needs balancing, use all available items
        if (prioritizedItems.length === 0) {
            return availableItems;
        }
        
        return prioritizedItems;
    }

    calculateItemInformation(item, ability) {
        // Calculate item information function for 2PL model
        const { difficulty, discrimination } = item;
        const exp = Math.exp(discrimination * (ability - difficulty));
        const p = exp / (1 + exp);
        return Math.pow(discrimination, 2) * p * (1 - p);
    }

    processResponse(itemId, response) {
        const item = this.filteredItemBank.find(i => i.id === itemId);
        if (!item) {
            throw new Error('Item not found');
        }

        const isCorrect = response === item.correctAnswer;
        
        // Store response
        this.responses.push({
            itemId: itemId,
            response: response,
            isCorrect: isCorrect,
            domain: item.domain,
            difficulty: item.difficulty,
            discrimination: item.discrimination
        });

        // Mark item as used
        this.usedItems.add(itemId);
        
        // Update domain counts
        this.domainItemCounts[item.domain]++;

        // Update ability estimate
        this.updateAbilityEstimate();

        // Update domain scores
        this.updateDomainScores();

        // Check termination criteria
        const shouldTerminate = this.shouldTerminate();

        return {
            isCorrect: isCorrect,
            shouldTerminate: shouldTerminate,
            abilityEstimate: this.abilityEstimate,
            standardError: this.standardError,
            domainScores: { ...this.domainScores }
        };
    }

    updateAbilityEstimate() {
        // Use Newton-Raphson method for maximum likelihood estimation
        let theta = this.abilityEstimate;
        
        for (let iteration = 0; iteration < this.maxIterations; iteration++) {
            const { firstDerivative, secondDerivative } = this.calculateDerivatives(theta);
            
            if (Math.abs(secondDerivative) < 1e-10) {
                break; // Avoid division by zero
            }
            
            const newTheta = theta - (firstDerivative / secondDerivative);
            
            if (Math.abs(newTheta - theta) < this.convergenceThreshold) {
                break;
            }
            
            theta = newTheta;
        }
        
        this.abilityEstimate = theta;
        this.standardError = Math.sqrt(-1 / this.calculateSecondDerivative(theta));
    }

    calculateDerivatives(theta) {
        let firstDerivative = 0;
        let secondDerivative = 0;
        
        for (const response of this.responses) {
            const item = this.filteredItemBank.find(i => i.id === response.itemId);
            const { difficulty, discrimination } = item;
            
            const exp = Math.exp(discrimination * (theta - difficulty));
            const p = exp / (1 + exp);
            
            const firstDeriv = discrimination * (response.isCorrect - p);
            const secondDeriv = -Math.pow(discrimination, 2) * p * (1 - p);
            
            firstDerivative += firstDeriv;
            secondDerivative += secondDeriv;
        }
        
        return { firstDerivative, secondDerivative };
    }

    calculateSecondDerivative(theta) {
        let secondDerivative = 0;
        
        for (const response of this.responses) {
            const item = this.filteredItemBank.find(i => i.id === response.itemId);
            const { difficulty, discrimination } = item;
            
            const exp = Math.exp(discrimination * (theta - difficulty));
            const p = exp / (1 + exp);
            
            secondDerivative += -Math.pow(discrimination, 2) * p * (1 - p);
        }
        
        return secondDerivative;
    }

    updateDomainScores() {
        // Calculate domain-specific scores based on responses
        for (const domain of this.domains) {
            const domainResponses = this.responses.filter(r => r.domain === domain);
            if (domainResponses.length > 0) {
                const correctCount = domainResponses.filter(r => r.isCorrect).length;
                this.domainScores[domain] = correctCount / domainResponses.length;
            }
        }
    }

    shouldTerminate() {
        // Check termination criteria
        if (this.responses.length < this.minItems) {
            return false;
        }
        
        if (this.responses.length >= this.maxItems) {
            return true;
        }
        
        if (this.standardError <= this.terminationThreshold) {
            return true;
        }
        
        // Check if we have minimum items from each domain
        const minDomainItems = Math.ceil(this.minItems / this.domains.length);
        for (const domain of this.domains) {
            if (this.domainItemCounts[domain] < minDomainItems) {
                return false;
            }
        }
        
        return false;
    }

    getStatus() {
        return {
            itemsCompleted: this.responses.length,
            abilityEstimate: this.abilityEstimate,
            standardError: this.standardError,
            domainScores: { ...this.domainScores },
            domainItemCounts: { ...this.domainItemCounts },
            totalItemsAvailable: this.filteredItemBank.length,
            itemsUsed: this.usedItems.size
        };
    }

    getDomainScores() {
        return { ...this.domainScores };
    }

    // Item culling methods
    enableCulling(minDiscrimination = 0.5, maxDifficulty = 3.0, minResponses = 50) {
        this.cullingEnabled = true;
        this.minDiscrimination = minDiscrimination;
        this.maxDifficulty = maxDifficulty;
        this.minResponses = minResponses;
        this.filterItems();
    }

    disableCulling() {
        this.cullingEnabled = false;
        this.filteredItemBank = [...this.itemBank];
    }

    getCullingStats() {
        const totalItems = this.itemBank.length;
        const filteredItems = this.filteredItemBank.length;
        const culledItems = totalItems - filteredItems;
        
        return {
            totalItems,
            filteredItems,
            culledItems,
            cullingRate: culledItems / totalItems,
            cullingEnabled: this.cullingEnabled
        };
    }

    // Export methods for validation
    exportItemBank() {
        return {
            totalItems: this.itemBank.length,
            filteredItems: this.filteredItemBank.length,
            items: this.filteredItemBank,
            cullingStats: this.getCullingStats()
        };
    }

    exportAssessmentResults() {
        return {
            abilityEstimate: this.abilityEstimate,
            standardError: this.standardError,
            domainScores: this.domainScores,
            responses: this.responses,
            itemsCompleted: this.responses.length,
            assessmentType: 'Comprehensive CAT'
        };
    }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComprehensiveCATEngine;
}



