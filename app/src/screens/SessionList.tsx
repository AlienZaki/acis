/**
 * SessionList — home screen.
 *
 * Shows stored sessions newest-first.  Bottom bar: language label + Start button.
 * Tap a session → SessionDetail.
 * Tap Start → opens live session (SessionDetail in live mode).
 */

import React, { useCallback } from "react";
import {
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { RootStackParamList } from "../navigation";
import { useSessionStore } from "../store/sessions";
import { GlassesStatusBadge } from "../components/GlassesStatusBadge";

type Props = NativeStackScreenProps<RootStackParamList, "SessionList">;

export function SessionList({ navigation }: Props) {
  const sessions = useSessionStore((s) => s.sessions);
  const startSession = useSessionStore((s) => s.startSession);

  const handleStart = useCallback(async () => {
    const id = await startSession();
    navigation.navigate("SessionDetail", { sessionId: id, live: true });
  }, [navigation, startSession]);

  return (
    <View style={styles.root}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>ACIS</Text>
        <GlassesStatusBadge />
      </View>

      {/* Session list */}
      <FlatList
        data={sessions}
        keyExtractor={(s) => s.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No sessions yet.</Text>
            <Text style={styles.emptyHint}>Tap Start to begin.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate("SessionDetail", { sessionId: item.id, live: false })}
          >
            <Text style={styles.cardTitle} numberOfLines={1}>
              {item.name}
            </Text>
            <Text style={styles.cardMeta}>
              {new Date(item.started_at).toLocaleString()}
            </Text>
          </TouchableOpacity>
        )}
      />

      {/* Bottom bar */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.startBtn} onPress={handleStart}>
          <Text style={styles.startBtnText}>Start</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#fff" },
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 20, paddingTop: 56, paddingBottom: 16 },
  title: { fontSize: 28, fontWeight: "700" },
  list: { paddingHorizontal: 16, paddingBottom: 100 },
  empty: { paddingTop: 80, alignItems: "center" },
  emptyText: { fontSize: 17, color: "#333" },
  emptyHint: { fontSize: 14, color: "#888", marginTop: 8 },
  card: { paddingVertical: 14, paddingHorizontal: 4, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#E5E5E5" },
  cardTitle: { fontSize: 16, fontWeight: "600" },
  cardMeta: { fontSize: 13, color: "#888", marginTop: 3 },
  bottomBar: { position: "absolute", bottom: 0, left: 0, right: 0, paddingHorizontal: 20, paddingBottom: 36, paddingTop: 12, backgroundColor: "#fff", borderTopWidth: StyleSheet.hairlineWidth, borderColor: "#E5E5E5" },
  startBtn: { backgroundColor: "#111", borderRadius: 14, paddingVertical: 16, alignItems: "center" },
  startBtnText: { color: "#fff", fontSize: 17, fontWeight: "700" },
});
