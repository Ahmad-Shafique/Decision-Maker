import { ENV } from '../config/env';

const BASE_URL = ENV.API_URL;

export async function checkHealth() {
    try {
        console.log(`Checking health at ${BASE_URL}/health`);
        const response = await fetch(`${BASE_URL}/health`);
        const data = await response.json();
        return data.status === 'ok';
    } catch (error) {
        console.warn('Health check failed:', error);
        return false;
    }
}

export async function getPrinciples() {
    try {
        const response = await fetch(`${BASE_URL}/principles`);
        if (!response.ok) throw new Error('Failed to fetch principles');
        return await response.json();
    } catch (error) {
        console.error('Error fetching principles:', error);
        return [];
    }
}

export async function analyzeSituation(description) {
    try {
        const response = await fetch(`${BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Analysis failed: ${errText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Analysis error:', error);
        throw error;
    }
}
