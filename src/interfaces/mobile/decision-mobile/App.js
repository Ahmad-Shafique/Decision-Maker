import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import HomeScreen from './screens/HomeScreen';
import AnalyzeScreen from './screens/AnalyzeScreen';
import PrinciplesScreen from './screens/PrinciplesScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: { backgroundColor: '#0f172a' },
            headerTintColor: '#fff',
            headerTitleStyle: { fontWeight: 'bold' },
            contentStyle: { backgroundColor: '#0f172a' }
          }}
        >
          <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Decision Maker' }} />
          <Stack.Screen name="Analyze" component={AnalyzeScreen} options={{ title: 'Analyze Situation' }} />
          <Stack.Screen name="Principles" component={PrinciplesScreen} options={{ title: 'Principles' }} />
        </Stack.Navigator>
        <StatusBar style="light" />
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
