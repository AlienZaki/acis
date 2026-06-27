import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { SessionList } from "./src/screens/SessionList";
import { SessionDetail } from "./src/screens/SessionDetail";
import { Settings } from "./src/screens/Settings";
import { PrepNotes } from "./src/screens/PrepNotes";
import type { RootStackParamList } from "./src/navigation";

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="SessionList" screenOptions={{ headerShown: false }}>
          <Stack.Screen name="SessionList" component={SessionList} />
          <Stack.Screen name="SessionDetail" component={SessionDetail} />
          <Stack.Screen name="Settings" component={Settings} options={{ headerShown: true, title: "Settings" }} />
          <Stack.Screen name="PrepNotes" component={PrepNotes} options={{ headerShown: true, title: "Prep Notes" }} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
