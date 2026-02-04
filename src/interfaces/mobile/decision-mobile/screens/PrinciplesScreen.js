import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, TextInput } from 'react-native';
import { getPrinciples } from '../services/api';

export default function PrinciplesScreen() {
    const [principles, setPrinciples] = useState([]);
    const [search, setSearch] = useState('');

    useEffect(() => {
        getPrinciples().then(setPrinciples);
    }, []);

    const filtered = principles.filter(p =>
        p.title.toLowerCase().includes(search.toLowerCase()) ||
        p.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <View style={styles.container}>
            <TextInput
                style={styles.search}
                placeholder="Search tags or keywords..."
                placeholderTextColor="#64748b"
                value={search}
                onChangeText={setSearch}
            />

            <FlatList
                data={filtered}
                keyExtractor={item => item.id}
                contentContainerStyle={{ paddingBottom: 20 }}
                renderItem={({ item }) => (
                    <View style={styles.item}>
                        <View style={styles.row}>
                            <Text style={styles.id}>{item.id}</Text>
                            <Text style={styles.title}>{item.title}</Text>
                        </View>
                        <View style={styles.tags}>
                            {item.tags.map(t => (
                                <View key={t} style={styles.tag}>
                                    <Text style={styles.tagText}>{t}</Text>
                                </View>
                            ))}
                        </View>
                    </View>
                )}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f172a',
        padding: 20,
    },
    search: {
        backgroundColor: '#1e293b',
        color: '#fff',
        padding: 12,
        borderRadius: 8,
        marginBottom: 16,
        fontSize: 16,
    },
    item: {
        backgroundColor: '#1e293b',
        padding: 16,
        borderRadius: 12,
        marginBottom: 12,
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    id: {
        color: '#94a3b8',
        fontWeight: 'bold',
        marginRight: 12,
        fontSize: 14,
    },
    title: {
        color: '#fff',
        fontSize: 18,
        fontWeight: '600',
        flex: 1,
    },
    tags: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
    },
    tag: {
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 4,
    },
    tagText: {
        color: '#38bdf8',
        fontSize: 12,
    }
});
