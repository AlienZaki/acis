/**
 * GlassesStatusBadge — small indicator showing Meta glasses connection state.
 *
 * States:
 *   connected  → green pill  "Meta glasses connected"
 *   phone      → grey pill   "Phone only"
 */

import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { useGlassesStore } from "../store/glasses";

export function GlassesStatusBadge() {
  const connected = useGlassesStore((s) => s.connected);
  return (
    <View style={[styles.badge, connected ? styles.connected : styles.phone]}>
      <Text style={styles.label}>{connected ? "Glasses connected" : "Phone only"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  connected: { backgroundColor: "#D4EDDA" },
  phone: { backgroundColor: "#E9ECEF" },
  label: { fontSize: 12, fontWeight: "500" },
});
