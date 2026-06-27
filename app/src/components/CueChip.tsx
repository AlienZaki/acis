/**
 * CueChip — pill-shaped chip for a single cue.
 *
 * Tap → opens CueDetailModal.
 */

import React, { useState } from "react";
import { Modal, StyleSheet, Text, TouchableOpacity, View, Pressable } from "react-native";
import type { CueNew } from "../lib/protocol";

const CUE_EMOJI: Record<CueNew["cue_type"], string> = {
  concept: "💡",
  answer: "❓",
  suggestion: "✨",
  bio: "👤",
};

const CUE_COLOR: Record<CueNew["cue_type"], string> = {
  concept: "#EEF4FF",
  answer: "#FFF8EE",
  suggestion: "#F0FFF0",
  bio: "#FFF0FF",
};

interface Props {
  cue: CueNew;
}

export function CueChip({ cue }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <TouchableOpacity style={[styles.chip, { backgroundColor: CUE_COLOR[cue.cue_type] }]} onPress={() => setOpen(true)}>
        <Text style={styles.emoji}>{CUE_EMOJI[cue.cue_type]}</Text>
        <Text style={styles.label} numberOfLines={1}>{cue.title}</Text>
      </TouchableOpacity>
      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
          <View style={styles.card}>
            <Text style={styles.cardEmoji}>{CUE_EMOJI[cue.cue_type]}</Text>
            <Text style={styles.cardTitle}>{cue.title}</Text>
            <Text style={styles.cardBody}>{cue.body}</Text>
            <TouchableOpacity style={styles.closeBtn} onPress={() => setOpen(false)}>
              <Text style={styles.closeBtnText}>Done</Text>
            </TouchableOpacity>
          </View>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  chip: { flexDirection: "row", alignItems: "center", paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginRight: 8, marginBottom: 8, maxWidth: 200 },
  emoji: { fontSize: 14, marginRight: 5 },
  label: { fontSize: 13, fontWeight: "500", flexShrink: 1 },
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.35)", alignItems: "center", justifyContent: "center" },
  card: { backgroundColor: "#fff", borderRadius: 20, padding: 28, marginHorizontal: 24, width: "85%", alignItems: "center" },
  cardEmoji: { fontSize: 36, marginBottom: 12 },
  cardTitle: { fontSize: 20, fontWeight: "700", textAlign: "center", marginBottom: 12 },
  cardBody: { fontSize: 15, lineHeight: 22, color: "#444", textAlign: "center" },
  closeBtn: { marginTop: 20, paddingHorizontal: 32, paddingVertical: 10, backgroundColor: "#111", borderRadius: 10 },
  closeBtnText: { color: "#fff", fontWeight: "600" },
});
