import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { analyzeSituation } from '../services/api';

export default function AnalyzeScreen() {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        if (!input.trim()) return;
        setLoading(true);
        setResult(null);

        try {
            const data = await analyzeSituation(input);
            setResult(data);
        } catch (e) {
            console.error(e);
            Alert.alert('Analysis Failed', e.message || 'Check your internet connection.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView contentContainerStyle={styles.container}>
            <View style={styles.inputSection}>
                <Text style={styles.label}>Describe the situation</Text>
                <TextInput
                    style={styles.input}
                    multiline
                    placeholder="e.g. A vendor is asking for a price hike..."
                    placeholderTextColor="#64748b"
                    value={input}
                    onChangeText={setInput}
                />

                <TouchableOpacity
                    style={[styles.btn, loading && styles.disabled]}
                    onPress={handleAnalyze}
                    disabled={loading}
                >
                    {loading ? (
                        <ActivityIndicator color="#0f172a" />
                    ) : (
                        <Text style={styles.btnText}>Analyze</Text>
                    )}
                </TouchableOpacity>
            </View>

            {result && (
                <View style={styles.resultSection}>
                    <Text style={styles.heading}>Recommendation</Text>
                    <Text style={styles.text}>{result.recommendation}</Text>

                    <Text style={[styles.heading, { marginTop: 16 }]}>Principles</Text>
                    {result.applicable_principles.map((p, i) => (
                        <View key={i} style={styles.principleCard}>
                            <Text style={styles.pTitle}>{p.principle.title}</Text>
                            <Text style={styles.pScore}>Match: {(p.relevance_score * 100).toFixed(0)}%</Text>
                        </View>
                    ))}

                    <Text style={[styles.heading, { marginTop: 16 }]}>Reasoning</Text>
                    <Text style={styles.text}>{result.reasoning}</Text>
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 20,
        backgroundColor: '#0f172a',
        flexGrow: 1,
    },
    inputSection: {
        marginBottom: 24,
    },
    label: {
        color: '#94a3b8',
        marginBottom: 8,
        fontSize: 16,
    },
    input: {
        backgroundColor: '#1e293b',
        color: '#fff',
        borderRadius: 12,
        padding: 16,
        height: 120,
        textAlignVertical: 'top',
        marginBottom: 16,
        fontSize: 16,
    },
    btn: {
        backgroundColor: '#38bdf8',
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    disabled: {
        opacity: 0.7,
    },
    btnText: {
        color: '#0f172a',
        fontWeight: 'bold',
        fontSize: 18,
    },
    resultSection: {
        marginTop: 8,
    },
    heading: {
        color: '#fff',
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    text: {
        color: '#e2e8f0',
        fontSize: 16,
        lineHeight: 24,
        marginBottom: 12,
    },
    principleCard: {
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: 12,
        borderRadius: 8,
        marginBottom: 8,
    },
    pTitle: {
        color: '#38bdf8',
        fontWeight: 'bold',
        fontSize: 16,
    },
    pScore: {
        color: '#94a3b8',
        fontSize: 14,
        marginTop: 4,
    }
});
