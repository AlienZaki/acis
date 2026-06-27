/**
 * PrepNotes — manage context notes that ACIS injects into Answer cue prompts.
 *
 * Each note has a title, body text, and an active toggle.  Only active notes
 * are sent to the LLM.  Tap a note to edit; swipe to delete.
 */

import React, { useState } from "react";
import {
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  Modal,
  Pressable,
  Switch,
} from "react-native";

interface PrepNote {
  id: string;
  title: string;
  body: string;
  active: boolean;
}

export function PrepNotes() {
  const [notes, setNotes] = useState<PrepNote[]>([]);
  const [editing, setEditing] = useState<PrepNote | null>(null);

  const openNew = () =>
    setEditing({ id: Date.now().toString(), title: "", body: "", active: true });

  const save = (note: PrepNote) => {
    setNotes((prev) => {
      const existing = prev.findIndex((n) => n.id === note.id);
      if (existing >= 0) {
        const next = [...prev];
        next[existing] = note;
        return next;
      }
      return [note, ...prev];
    });
    setEditing(null);
  };

  const remove = (id: string) => setNotes((prev) => prev.filter((n) => n.id !== id));

  const toggleActive = (id: string) =>
    setNotes((prev) => prev.map((n) => (n.id === id ? { ...n, active: !n.active } : n)));

  return (
    <View style={styles.root}>
      <FlatList
        data={notes}
        keyExtractor={(n) => n.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No prep notes.</Text>
            <Text style={styles.emptyHint}>Add notes to give ACIS context before a session.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.card} onPress={() => setEditing(item)}>
            <View style={styles.cardRow}>
              <Text style={styles.cardTitle} numberOfLines={1}>{item.title || "Untitled"}</Text>
              <Switch value={item.active} onValueChange={() => toggleActive(item.id)} />
            </View>
            <Text style={styles.cardPreview} numberOfLines={2}>{item.body}</Text>
          </TouchableOpacity>
        )}
      />
      <TouchableOpacity style={styles.fab} onPress={openNew}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {editing && (
        <Modal visible animationType="slide" presentationStyle="pageSheet">
          <View style={styles.editor}>
            <View style={styles.editorHeader}>
              <TouchableOpacity onPress={() => setEditing(null)}>
                <Text style={styles.editorCancel}>Cancel</Text>
              </TouchableOpacity>
              <Text style={styles.editorTitle}>Prep Note</Text>
              <TouchableOpacity onPress={() => save(editing)}>
                <Text style={styles.editorSave}>Save</Text>
              </TouchableOpacity>
            </View>
            <TextInput
              style={styles.editorTitleInput}
              placeholder="Title"
              value={editing.title}
              onChangeText={(t) => setEditing({ ...editing, title: t })}
              autoFocus
            />
            <TextInput
              style={styles.editorBody}
              placeholder="Notes, background info, key facts…"
              value={editing.body}
              onChangeText={(t) => setEditing({ ...editing, body: t })}
              multiline
              textAlignVertical="top"
            />
          </View>
        </Modal>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#fff" },
  list: { padding: 16, paddingBottom: 100 },
  empty: { paddingTop: 60, alignItems: "center" },
  emptyText: { fontSize: 17, color: "#333" },
  emptyHint: { fontSize: 14, color: "#888", marginTop: 8, textAlign: "center", paddingHorizontal: 32 },
  card: { padding: 16, borderRadius: 12, backgroundColor: "#F9F9F9", marginBottom: 12 },
  cardRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 4 },
  cardTitle: { fontSize: 15, fontWeight: "600", flex: 1 },
  cardPreview: { fontSize: 13, color: "#666", lineHeight: 18 },
  fab: { position: "absolute", bottom: 36, right: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: "#111", alignItems: "center", justifyContent: "center" },
  fabText: { color: "#fff", fontSize: 28, lineHeight: 32 },
  editor: { flex: 1, padding: 20 },
  editorHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 20, paddingTop: 12 },
  editorTitle: { fontSize: 17, fontWeight: "600" },
  editorCancel: { fontSize: 17, color: "#888" },
  editorSave: { fontSize: 17, color: "#007AFF", fontWeight: "600" },
  editorTitleInput: { fontSize: 20, fontWeight: "600", borderBottomWidth: StyleSheet.hairlineWidth, borderColor: "#E5E5E5", paddingVertical: 12, marginBottom: 16 },
  editorBody: { flex: 1, fontSize: 15, lineHeight: 22 },
});
