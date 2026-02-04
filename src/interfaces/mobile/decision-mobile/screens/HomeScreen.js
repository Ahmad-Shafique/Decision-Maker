import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, RefreshControl } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { checkHealth } from '../services/api';

export default function HomeScreen({ navigation }) {
    const [status, setStatus] = useState('Connecting to Cloud...');
    const [online, setOnline] = useState(false);
    const [refreshing, setRefreshing] = useState(false);

    const check = async () => {
        setRefreshing(true);
        setStatus('Pinging Render...');
        const alive = await checkHealth();
        setOnline(alive);
        setStatus(alive ? 'System Online (Cloud)' : 'System Offline');
        setRefreshing(false);
    };

    useEffect(() => {
        check();
    }, []);

    return (
        <ScrollView
            contentContainerStyle={styles.container}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={check} tintColor="#fff" />}
        >
            <LinearGradient
                colors={['#1e293b', '#0f172a']}
                style={styles.header}
            >
                <Text style={styles.greeting}>Welcome Back</Text>
                <View style={[styles.badge, online ? styles.online : styles.offline]}>
                    <Text style={styles.badgeText}>{status}</Text>
                </View>
                <Text style={styles.subtext}>Connected to Render Deployment</Text>
            </LinearGradient>

            <View style={styles.actions}>
                <TouchableOpacity
                    style={styles.card}
                    onPress={() => navigation.navigate('Analyze')}
                    activeOpacity={0.8}
                >
                    <LinearGradient colors={['#38bdf8', '#0ea5e9']} style={styles.cardBg}>
                        <Text style={styles.cardTitle}>Analyze Situation</Text>
                        <Text style={styles.cardDesc}>Evaluate a scenario against your principles.</Text>
                    </LinearGradient>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.card}
                    onPress={() => navigation.navigate('Principles')}
                    activeOpacity={0.8}
                >
                    <LinearGradient colors={['#a855f7', '#9333ea']} style={styles.cardBg}>
                        <Text style={styles.cardTitle}>Browse Principles</Text>
                        <Text style={styles.cardDesc}>Review your 45 core principles.</Text>
                    </LinearGradient>
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        backgroundColor: '#0f172a',
        padding: 20,
    },
    header: {
        padding: 24,
        borderRadius: 16,
        marginBottom: 24,
        alignItems: 'flex-start',
    },
    greeting: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 8,
    },
    badge: {
        paddingVertical: 4,
        paddingHorizontal: 12,
        borderRadius: 20,
        marginBottom: 8,
    },
    online: {
        backgroundColor: 'rgba(74, 222, 128, 0.2)',
    },
    offline: {
        backgroundColor: 'rgba(248, 113, 113, 0.2)',
    },
    badgeText: {
        color: '#fff',
        fontSize: 14,
        fontWeight: '600',
    },
    subtext: {
        color: '#64748b',
        fontSize: 12,
    },
    actions: {
        gap: 16,
    },
    card: {
        height: 120,
        borderRadius: 16,
        overflow: 'hidden',
    },
    cardBg: {
        flex: 1,
        padding: 20,
        justifyContent: 'center',
    },
    cardTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 4,
    },
    cardDesc: {
        fontSize: 14,
        color: 'rgba(255,255,255,0.9)',
    },
});
